import requests
import pyzipper
import os
import time

ZIP_PASSWORD = b"DBhkhdnefkhfq,#%"
OUTPUT_FILE = "iptv_source.txt"

# 多米配置接口，境外可能超时，加重试
CONFIG_URLS = [
    "http://207.56.13.146:9999/dmtv/config.json?ver=1.0.0&t={t}&channel=baidu&sdkVer=36&k=59866f9c89dd1daf819f71c47f1e4105&pkg=com.dmtv.yj&deviceName=vivoV2307A&mac=4e:ef:60:02:cd:00",
]

def fetch_zip_url():
    """尝试从config接口获取最新zip地址，失败则用上次成功的地址"""
    t = int(time.time())
    for config_url in CONFIG_URLS:
        url = config_url.format(t=t)
        print(f"尝试获取配置: {url}")
        try:
            resp = requests.get(url, timeout=30)
            config = resp.json()
            zip_url = config["source"]
            print(f"获取成功: {zip_url}")
            # 保存本次成功的zip地址到缓存文件
            with open("last_zip_url.txt", "w") as f:
                f.write(zip_url)
            return zip_url
        except Exception as e:
            print(f"获取配置失败: {e}")

    # 读取上次成功的地址
    if os.path.exists("last_zip_url.txt"):
        with open("last_zip_url.txt") as f:
            zip_url = f.read().strip()
        print(f"使用缓存的zip地址: {zip_url}")
        return zip_url

    raise Exception("无法获取zip地址，且没有缓存")

def download_with_retry(url, max_retry=3):
    """带重试的下载"""
    for i in range(max_retry):
        try:
            print(f"下载 (第{i+1}次尝试): {url}")
            r = requests.get(url, timeout=60)
            r.raise_for_status()
            return r.content
        except Exception as e:
            print(f"下载失败: {e}")
            if i < max_retry - 1:
                time.sleep(10)
    raise Exception(f"下载失败，已重试{max_retry}次")

def run():
    # 1. 获取zip地址
    zip_url = fetch_zip_url()

    # 2. 下载zip（带重试）
    zip_data = download_with_retry(zip_url)
    zip_path = "source_tmp.zip"
    with open(zip_path, "wb") as f:
        f.write(zip_data)
    print(f"下载完成，大小: {len(zip_data)} 字节")

    # 3. 解压
    print("解压中...")
    with pyzipper.AESZipFile(zip_path) as zf:
        zf.setpassword(ZIP_PASSWORD)
        names = zf.namelist()
        print(f"zip内文件: {names}")
        txt_name = next(
            (n for n in names if n.lower().endswith(".txt")),
            next((n for n in names if n.lower().endswith(".m3u")), names[0])
        )
        print(f"读取文件: {txt_name}")
        content = zf.read(txt_name).decode("utf-8")

    # 4. 保存结果
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    os.remove(zip_path)

    print(f"完成！共 {len(content)} 字节")
    print("=== 内容预览（前5行）===")
    for line in content.split("\n")[:5]:
        print(line)

if __name__ == "__main__":
    run()
