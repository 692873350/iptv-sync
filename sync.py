导入请求请求
其他：
继续
导入时间time

# ====== 配置 ======
config_URL="http://207.56.13.146:9999/dmtv/config.json?ver=1.0.0&t={t}&channel=baidu&sdkVer=36&k=59866f9c89dd1daf819f71c47f1e4105&pkg=com.dmtv.yj&deviceName=vivoV2307A&mac=4e:ef:60:02:cd:00""http://207.56.13.146:9999/dmtv/config.json?ver=1.0.0&t={t}&channel=baidu&sdkVer=36&k=59866f9c89dd1daf819f71c47f1e4105&pkg=com.dmtv.yj&deviceName=vivoV2307A&mac=4e:ef:60:02:cd:00"
zip_PASSWORD=B"DBhkhdnefkhfq，#%"B"DBhkhdnefkhfq，#%"
output_FILE="iptv_source.txt""iptv_source.txt"

# ====== 广告台过滤关键词（频道名包含任一关键词即被过滤）======
ad_KEYWORDS=[[
"好物推荐"，"健康甄选"，"养生馆"，"电视购物"，"购物"，"带货"，"好物推荐"，"健康甄选"，"养生馆"，"电视购物"，"购物"，"带货"，"商城"，"乐购"，"惠买"，"嗨购"，"甄选好物"，"精选好物"，"商城"，"乐购"，"惠买"，"嗨购"，"甄选好物"，"精选好物"，"生活馆"，"直营"，"央广购物"，"家有购物"，"快乐购"，"好享购"，"生活馆"，"直营"，"央广购物"，"家有购物"，"快乐购"，"好享购"，"聚鲨"，"优购物"，"中视购物"，"东方购物"，"环球购物"，"天天购物"，"聚鲨"，"优购物"，"中视购物"，"东方购物"，"环球购物"，"天天购物"，"家家购物"，"购物街""家家购物"，"购物街"ad_KEYWORDS
"好物推荐", "好物分享", "健康甄选", "健康有约", "养生馆",
"精品甄选"，"福利多多"，"电视购物"，"购物"，"带货"，
"商城", "乐购", "惠买", "嗨购", "甄选好物", "精选好物",
"生活馆", "直营", "央广购物", "家有购物", "快乐购", "好享购",
"聚鲨"，"优购物"，"中视购物"，"东方购物"，"环球购物"，"天天购物"，
    "家家购物", "购物街"

]


定义filter_ad_channels(内容)：
"""按行过滤广告台，兼容M3U(#EXTINF+URL成对)和diyp/txt(频道名，URL)两种格式""""""按行过滤广告台，兼容M3U(#EXTINF+URL成对)和diyp/txt(频道名，URL)两种格式"""
行数=content.split("\n")拆分("\n")
从…… 里面出去=[][]
已删除=00
I=00
n=len(线)len(线)
当I<n：而i<n：
line=line[i][i]
stripped=line.strip()strip()
#----m3u格式：#EXTINF行与下一行URL成对----#----m3u格式：#EXTINF行与下一行URL成对----
如果stripped.startswith("#EXTINF")：如果stripped.startswith("#EXTINF")：
姓名=""""
如果“，”已被剥离：如果“，”已被剥离：
name=已剥离.rsplit("，"，1)[-1].条带()rsplit("，"，1)[-1].带()
hit=任意(名称中的k表示ad_KEYWORDS中的K)任何(AD_KEYWORDS中k的name中的k)
#下一行是非#开头的URL行
如果i+1<n且不是行[i+1].strip().startsWith("#")：
如果命中：
已删除+=1
Elif
如果命中：
                
如果命中：
已删除+=1
I+=1
继续
#----diyp/txt格式：频道名，URL一行---
Elif("，"在已剥离和未剥离中.startswith("#")
和“：//”(已剥离和未剥离.startswith("http"))：
name=stripped.split("，"，1)[0].strip()
如果有(AD_KEYWORDS中k的名称中的k)：
已删除+=1
I+=1
继续
out.append(行)
I+=1
return"\n".join(out)，已删除


Def运行()：
#1.拉取最新配置，获得zip地址
T=int(time.time())
URL=CONFIG_URL.format(t=t)
print(f"[1]拉取放置：{url}")
RESP=requests.get(url，timeout=30)
zip_url=config["source"]
RESP=requests.get(url，timeout=30)
print(f"[2]最新zip：{zip_url}")
    # 缓存本次地址，供下次境外超时时兜底
    # 缓存本次地址，供下次境外超时时兜底
f.write(zip_url)

#2.下载zip(失败用缓存地址重试)
尝试：
R=requests.get(zip_url，timeout=60)
r.aise_for_status()
例外情况除外，如e：
打印(f”下载失败：{e}，尝试缓存地址")
打开("last_zip_url.txt")为f：
zip_url=f.read().strip()
R=requests.get(zip_url，timeout=60)
r.aise_for_status()
zip_path="source_tmp.zip"
open(zip_path，"wb")为f：
f.write(r.content)
print(f"[3]下载完成：{len(r.content)}字节")

#3.降压(aes加密zip)
#3.降压(aes加密zip)
使用pyzipper.AESZipFile(zip_path)作为zf：
zf.setpassword(ZIP_PASSWORD)
names=zf.namelist()
使用pyzipper.AESZipFile(zip_path)作为zf：
txt_name=next(
(如果n.lower().endswith(".txt")，则n代表名称中的n)，
next((n表示n中的n，如果n.lower().endswith(".m3u"))，名称[0])
        )
打印(f"使用文件：{txt_name}")
跑()

# 4. 过滤广告台
打印(“[5]过滤广告台...")
删除的内容=filter_ad_channels(内容)
打印(f”共过滤广告台：{已移除}个")

# 5. 保存到仓库
将(OUTPUT_FILE，"w"，encoding="utf-8")作为f打开：
f.write(内容)
os.remove(zip_path)

print(f"[6]完成！{OUTPUT_FILE}共{len(content)}字节")
打印("===前5行预览===")
对于content.split("\n")[：5]中的行：
打印(行)


如果__名称__=="__主要的__"：
跑()
