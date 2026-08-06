import requests
import pyzipper
import os
import time

# ====== 配置 ======
CONFIG_URL = "http://207.56.13.146:9999/dmtv/config.json?ver=1.0.0&t={t}&channel=baidu&sdkVer=36&k=59866f9c89dd1daf819f71c47f1e4105&pkg=com.dmtv.yj&deviceName=vivoV2307A&mac=4e:ef:60:02:cd:00"
ZIP_PASSWORD = b"DBhkhdnefkhfq,#%"
OUTPUT_FILE = "iptv_source.txt"

# ====== 广告台过滤关键词（频道名包含任一关键词即被过滤）======
AD_KEYWORDS = [
    "好物推荐", "健康甄选", "养生馆", "电视购物", "购物", "带货",
    "商城", "乐购", "惠买", "嗨购", "甄选好物", "精选好物",
    "生活馆", "直营", "央广购物", "家有购物", "快乐购", "好享购",
    "聚鲨", "优购物", "中视购物", "东方购物", "环球购物", "天天购物",
    "家家购物", "购物街"
]


def filter_ad_channels(content):
    """按行过滤广告台，兼容 m3u(#EXTINF+URL 成对) 和 diyp/txt(频道名,url) 两种格式"""
    lines = content.split("\n")
    out = []
    removed = 0
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()
        # ---- m3u 格式：#EXTINF 行与下一行 URL 成对 ----
        if stripped.startswith("#EXTINF"):
            name = ""
            if "," in stripped:
                name = stripped.rsplit(",", 1)[-1].strip()
            hit = any(k in name for k in AD_KEYWORDS)
            # 下一行是非 # 开头的 URL 行
            if i + 1 < n and not lines[i + 1].strip().startswith("#"):
                if hit:
                    removed += 1
                    i += 2          # #EXTINF 和它的 URL 一起删
                    continue
            else:
                if hit:
                    removed += 1
                    i += 1
                    continue
        # ---- diyp/txt 格式：频道名,url 一行 ----
        elif ("," in stripped and not stripped.startswith("#")
              and "://" in stripped and not stripped.startswith("http")):
            name = stripped.split(",", 1)[0].strip()
            if any(k in name for k in AD_KEYWORDS):
                removed += 1
                i += 1
                continue
        out.append(line)
        i += 1
    return "\n".join(out), removed


def run():
    # 1. 拉取最新配置，获得 zip 地址
    t = int(time.time())
    url = CONFIG_URL.format(t=t)
    print(f"[1] 拉取配置: {url}")
    resp = requests.get(url, timeout=30)
    config = resp.json()
    zip_url = config["source"]
    print(f"[2] 最新zip: {zip_url}")
    # 缓存本次地址，供下次境外超时时兜底
    with open("last_zip_url.txt", "w") as f:
        f.write(zip_url)

    # 2. 下载 zip（失败用缓存地址重试）
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
    print(f"[3] 下载完成: {len(r.content)} 字节")

    # 3. 解压（AES 加密 zip）
    print("[4] 解压中...")
    with pyzipper.AESZipFile(zip_path) as zf:
        zf.setpassword(ZIP_PASSWORD)
        names = zf.namelist()
        print(f"    zip内文件: {names}")
        txt_name = next(
            (n for n in names if n.lower().endswith(".txt")),
            next((n for n in names if n.lower().endswith(".m3u")), names[0])
        )
        print(f"    使用文件: {txt_name}")
        content = zf.read(txt_name).decode("utf-8", errors="replace")

    # 4. 过滤广告台
    print("[5] 过滤广告台...")
    content, removed = filter_ad_channels(content)
    print(f"    共过滤广告台: {removed} 个")

    # 5. 保存到仓库
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    os.remove(zip_path)

    print(f"[6] 完成！{OUTPUT_FILE} 共 {len(content)} 字节")
    print("=== 前5行预览 ===")
    for line in content.split("\n")[:5]:
        print(line)


if __name__ == "__main__":
    run()