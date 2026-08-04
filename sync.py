import requests
import pyzipper
import os
import time
import base64
import json

CONFIG_URL = "http://207.56.13.146:9999/dmtv/config.json?ver=1.0.0&t={t}&channel=baidu&sdkVer=36&k=59866f9c89dd1daf819f71c47f1e4105&pkg=com.dmtv.yj&deviceName=vivoV2307A&mac=4e:ef:60:02:cd:00"
ZIP_PASSWORD = b"DBhkhdnefkhfq,#%"
OUTPUT_FILE = "iptv_source.txt"

def run():
    # 1. 拉取最新 config，获得 zip 地址
    t = int(time.time())
    url = CONFIG_URL.format(t=t)
    print(f"[1] 拉取配置: {url}")
    resp = requests.get(url, timeout=15)
    config = resp.json()
    zip_url = config["source"]
    print(f"[2] 最新zip地址: {zip_url}")

    # 2. 下载 zip
    print("[3] 下载zip...")
    r = requests.get(zip_url, timeout=30)
    zip_path = "source_tmp.zip"
    with open(zip_path, "wb") as f:
        f.write(r.content)
    print(f"    下载完成，大小: {len(r.content)} 字节")

    # 3. 解压（AES加密zip）
    print("[4] 解压...")
    with pyzipper.AESZipFile(zip_path) as zf:
        zf.setpassword(ZIP_PASSWORD)
        names = zf.namelist()
        print(f"    zip内文件: {names}")
        # 优先找 txt，其次 m3u，最后取第一个
        txt_name = next(
            (n for n in names if n.lower().endswith(".txt")),
            next((n for n in names if n.lower().endswith(".m3u")), names[0])
        )
        print(f"    使用文件: {txt_name}")
        content = zf.read(txt_name).decode("utf-8")

    # 4. 保存本地
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    os.remove(zip_path)

    print(f"[5] 完成，共 {len(content)} 字节")
    print("=== 内容预览（前3行）===")
    for line in content.split("\n")[:3]:
        print(line)

if __name__ == "__main__":
    run()
