import requests
import pyzipper
import os
import time

CONFIG_URL = "http://207.56.13.146:9999/dmtv/config.json?ver=1.0.0&t={t}&channel=baidu&sdkVer=36&k=59866f9c89dd1daf819f71c47f1e4105&pkg=com.dmtv.yj&deviceName=vivoV2307A&mac=4e:ef:60:02:cd:00"
ZIP_PASSWORD = b"DBhkhdnefkhfq,#%"
OUTPUT_FILE = "iptv_source.txt"

def run():
    t = int(time.time())
    url = CONFIG_URL.format(t=t)
    resp = requests.get(url, timeout=30)
    conf = resp.json()
    zip_url = conf["source"]
    print("zip:", zip_url)
    open("last_zip_url.txt", "w").write(zip_url)

    r = requests.get(zip_url, timeout=60)
    open("tmp.zip", "wb").write(r.content)
    print("下载完成:", len(r.content), "字节")

    with pyzipper.AESZipFile("tmp.zip") as zf:
        zf.setpassword(ZIP_PASSWORD)
        names = zf.namelist()
        print("zip内:", names)
        txt = next((x for x in names if x.lower().endswith(".txt")), next((x for x in names if x.lower().endswith(".m3u")), names[0]))
        content = zf.read(txt).decode("utf-8", errors="replace")

    print("=== 源文件前 10 行（看格式）===")
    lines = content.split("\n")
    for i in range(min(10, len(lines))):
        print(repr(lines[i]))
    print("=== 总行数:", len(lines), "===")

    # 统计包含广告关键词的行数
    keywords = ["好物", "健康", "甄选", "养生", "购物", "福利", "精品", "推荐"]
    count = 0
    for line in lines:
        for k in keywords:
            if k in line:
                count += 1
                break
    print("包含广告关键词的行数:", count)

    open(OUTPUT_FILE, "w", encoding="utf-8").write(content)
    os.remove("tmp.zip")
    print("完成")

if __name__ == "__main__":
    run()