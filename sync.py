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
    out, removed, i, n = [], 0, 0, len(lines)
    while i < n:
        s = lines[i].strip()
        if s.startswith("#EXTINF"):
            name = s.rsplit(",", 1)[-1].strip() if "," in s else ""
            hit = any(k in name for k in AD_KEYWORDS)
            if i + 1 < n and not lines[i+1].strip().startswith("#"):
                if hit:
                    removed += 1
                    i += 2
                    continue
            else:
                if hit:
                    removed += 1
                    i += 1
                    continue
        elif "," in s and not s.startswith("#") and "://" in s and not s.startswith("http"):
            name = s.split(",", 1)[0].strip()
            if any(k in name for k in AD_KEYWORDS):
                removed += 1
                i += 1
                continue
        out.append(lines[i])
        i += 1
    return "\n".join(out), removed

def run():
    t = int(time.time())
    url = CONFIG_URL.format(t=t)
    print(f"拉取配置: {url}")
    resp = requests.get(url, timeout=30)
    config = resp.json()
    zip_url = config["source"]
    print(f"最新zip: {zip_url}")
    with open("last_zip_url.txt", "w") as f:
        f.write(zip_url)

    try:
        r = requests.get(zip_url, timeout=60)
        r.raise_for_status()
    except Exception as e:
        print(f"下载失败: {e}，尝试缓存地址")
        with open("last_zip_url.txt") as f:
            zip_url = f.read().strip()
        r = requests.get(zip_url, timeout=60)
        r.raise_for_status()
    zip_path = "source_tmp.zip"
    with open(zip_path, "wb") as f:
        f.write(r.content)
    print(f"下载完成: {len(r.content)} 字节")

    print("解压中...")
    with pyzipper.AESZipFile(zip_path) as zf:
        zf.setpassword(ZIP_PASSWORD)
        names = zf.namelist()
        print(f"zip内文件: {names}")
        txt_name = next(
            (n for n in names if n.lower().endswith(".txt")),
            next((n for n in names if n.lower().endswith(".m3u")), names[0])
        )
        print(f"使用文件: {txt_name}")
        content = zf.read(txt_name).decode("utf-8", errors="replace")

    content, removed = filter_ad(content)
    print(f"过滤广告台: {removed} 个")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    os.remove(zip_path)

    print(f"完成！{OUTPUT_FILE} 共 {len(content)} 字节")

if __name__ == "__main__":
    run()