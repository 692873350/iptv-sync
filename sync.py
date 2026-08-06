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
    "家家购物", "购物街"
]

def filter_ad(content):
    lines = content.split("\n")
    out = []
    removed = 0
    for line in lines:
        s = line.strip()
        # 跳过空行
        if not s:
            out.append(line)
            continue
        # 跳过 #genre# 分组行
        if "#genre#" in s:
            out.append(line)
            continue
        # diyp 格式: 频道名,URL
        # 检查是否包含逗号（频道名和 URL 的分隔符）
        if "," in s:
            # 取第一个逗号前面的部分作为频道名
            name = s.split(",", 1)[0].strip()
            # 检查频道名是否包含广告关键词
            hit = False
            for kw in AD_KEYWORDS:
                if kw in name:
                    hit = True
                    break
            if hit:
                removed += 1
                continue  # 跳过这一行
        # 其他行正常保留
        out.append(line)
    return "\n".join(out), removed

def run():
    t = int(time.time())
    url = CONFIG_URL.format(t=t)
    print("拉取配置:", url)
    resp = requests.get(url, timeout=30)
    conf = resp.json()
    zip_url = conf["source"]
    print("最新zip:", zip_url)
    with open("last_zip_url.txt", "w") as f:
        f.write(zip_url)

    try:
        r = requests.get(zip_url, timeout=60)
        r.raise_for_status()
    except Exception as e:
        print("下载失败，尝试缓存:", e)
        with open("last_zip_url.txt") as f:
            zip_url = f.read().strip()
        r = requests.get(zip_url, timeout=60)
        r.raise_for_status()

    with open("tmp.zip", "wb") as f:
        f.write(r.content)
    print("下载完成:", len(r.content), "字节")

    print("解压中...")
    with pyzipper.AESZipFile("tmp.zip") as zf:
        zf.setpassword(ZIP_PASSWORD)
        names = zf.namelist()
        print("zip内:", names)
        txt = next((x for x in names if x.lower().endswith(".txt")),
                   next((x for x in names if x.lower().endswith(".m3u")), names[0]))
        content = zf.read(txt).decode("utf-8", errors="replace")

    content, removed = filter_ad(content)
    print("过滤广告台:", removed, "个")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    os.remove("tmp.zip")

    print("完成！", OUTPUT_FILE, len(content), "字节")

if __name__ == "__main__":
    run()