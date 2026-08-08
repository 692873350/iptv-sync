import requests
import pyzipper
import os
import time

CONFIG_URL = "http://207.56.13.146:9999/dmtv/config.json?ver=1.0.0&t={t}&channel=baidu&sdkVer=36&k=59866f9c89dd1daf819f71c47f1e4105&pkg=com.dmtv.yj&deviceName=vivoV2307A&mac=4e:ef:60:02:cd:00"
ZIP_PASSWORD = b"DBhkhdnefkhfq,#%"
OUTPUT_FILE = "iptv_source.txt"
YIYI_URL = "https://raw.githubusercontent.com/fafa002/yf2025/main/yiyifafa.txt"

# 从 yiyifafa.txt 提取这些分类，合并到"港澳台"
TARGET_CATEGORIES = [
    "AK电影,#genre#", "极速港台,#genre#", "极速港台2,#genre#",
    "四季台湾,#genre#", "四季台湾2,#genre#", "今日影视,#genre#"
]
NEW_CATEGORY = "港澳台,#genre#"

AD_KEYWORDS = [
    "好物推荐", "好物分享", "健康甄选", "健康有约", "养生馆",
    "精品甄选", "福利多多", "电视购物", "购物", "带货",
    "商城", "乐购", "惠买", "嗨购", "甄选好物", "精选好物",
    "生活馆", "直营", "央广购物", "家有购物", "快乐购", "好享购",
    "聚鲨", "优购物", "中视购物", "东方购物", "环球购物", "天天购物",
    "家家购物", "购物街"
，"严选好物"，"会员专享"，"美好生活"，"健康在线"
]

def filter_ad(content):
    lines = content.split("\n")
    out, removed = [], 0
    for line in lines:
        s = line.strip()
        if not s or "#genre#" in s:
            out.append(line)
            continue
        if "," in s:
            name = s.split(",", 1)[0].strip()
            hit = any(k in name for k in AD_KEYWORDS)
            if hit:
                removed += 1
                continue
        out.append(line)
    return "\n".join(out), removed

def extract_categories(content):
    """从 yiyifafa.txt 提取目标分类频道，合并到港澳台"""
    lines = content.replace("\r", "").split("\n")
    result = [f"\n{NEW_CATEGORY}"]
    in_target = False
    added = 0
    for line in lines:
        s = line.strip()
        if not s:
            continue
        if "#genre#" in s:
            in_target = s in TARGET_CATEGORIES
            continue
        if in_target and "," in s and "://" in s:
            result.append(line)
            added += 1
    print(f"    从yiyifafa提取: {added} 个频道")
    return "\n".join(result), added

def run():
    # 1. 拉取多米配置
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

    open("tmp.zip", "wb").write(r.content)
    print("3. 下载完成:", len(r.content), "字节")

    # 4. 解压多米源
    print("4. 解压多米源...")
    with pyzipper.AESZipFile("tmp.zip") as zf:
        zf.setpassword(ZIP_PASSWORD)
        names = zf.namelist()
        print("   zip内:", names)
        txt = next((x for x in names if x.lower().endswith(".txt")),
                   next((x for x in names if x.lower().endswith(".m3u")), names[0]))
        content = zf.read(txt).decode("utf-8", errors="replace")
    os.remove("tmp.zip")

    # 5. 下载 yiyifafa.txt
    print("5. 下载 yiyifafa.txt...")
    r2 = requests.get(YIYI_URL, timeout=30)
    extra = r2.text
    print(f"    yiyifafa: {len(r2.text)} 字节")

    # 6. 提取目标分类频道
    print("6. 提取港澳台频道...")
    extra_content, added = extract_categories(extra)

    # 7. 合并
    content = content.rstrip("\n") + "\n" + extra_content

    # 8. 过滤广告
    content, removed = filter_ad(content)
    print(f"7. 过滤广告台: {removed} 个")

    open(OUTPUT_FILE, "w", encoding="utf-8").write(content)
    print(f"8. 完成！{OUTPUT_FILE} 共 {len(content)} 字节")

if __name__ == "__main__":
    run()