import requests
import pyzipper
import os
import time

CONFIG_URL = "http://207.56.13.146:9999/dmtv/config.json?ver=1.0.0&t={t}&channel=baidu&sdkVer=36&k=59866f9c89dd1daf819f71c47f1e4105&pkg=com.dmtv.yj&deviceName=vivoV2307A&mac=4e:ef:60:02:cd:00"
ZIP_PASSWORD = b"DBhkhdnefkhfq,#%"
OUTPUT_FILE = "iptv_source.txt"

AD_KEYWORDS = [
    "好物推荐", "好物分享", "健康甄选", "健康有约", "养生馆",
    "精品甄选", "福利多多", "电视购物", "购物", "带货",
    "商城", "乐购", "惠买", "嗨购", "甄选好物", "精选好物",
    "生活馆", "直营", "央广购物", "家有购物", "快乐购", "好享购",
    "聚鲨", "优购物", "中视购物", "东方购物", "环球购物", "天天购物",
    "家家购物", "购物街", "严选好物", "会员专享", "美好生活", "健康在线"
]

def run():
    t = int(time.time())
    url = CONFIG_URL.format(t=t)
    print("1. 拉取配置:", url)
    resp = requests.get(url, timeout=30)
    conf = resp.json()
    zip_url = conf["source"]
    print("2. 最新zip:", zip_url)
    open("last_zip_url.txt", "w").write(zip_url)

    try:
        r = requests.get(zip_url, timeout=60)
        r.raise_for_status()
    except Exception as e:
        print("下载失败，尝试缓存:", e)
        zip_url = open("last_zip_url.txt").read().strip()
        r = requests.get(zip_url, timeout=60)
        r.raise_for_status()

    open("tmp.zip", "wb").write(r.content)
    print("3. 下载完成:", len(r.content), "字节")

    print("4. 解压中...")
    with pyzipper.AESZipFile("tmp.zip") as zf:
        zf.setpassword(ZIP_PASSWORD)
        names = zf.namelist()
        print("   zip内:", names)
        txt = next((x for x in names if x.lower().endswith(".txt")),
                   next((x for x in names if x.lower().endswith(".m3u")), names[0]))
        content = zf.read(txt).decode("utf-8", errors="replace")

    # 过滤
    lines = content.split("\n")
    out = []
    removed = 0
    filtered = []
    for line in lines:
        s = line.strip()
        if not s or "#genre#" in s:
            out.append(line)
            continue
        if "," in s:
            name = s.split(",", 1)[0].strip()
            hit = False
            for kw in AD_KEYWORDS:
                if kw in name:
                    hit = True
                    break
            if hit:
                filtered.append(name)
                removed += 1
                continue
        out.append(line)

    print("5. 过滤掉", removed, "个广告台:")
    for n in filtered:
        print("   -", n)

    result = "\n".join(out)
    open(OUTPUT_FILE, "w", encoding="utf-8").write(result)
    os.remove("tmp.zip")
    print("6. 完成！", OUTPUT_FILE, len(result), "字节")

if __name__ == "__main__":
    run()