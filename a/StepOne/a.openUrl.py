import urllib.request           # 用于发送http请求，获取网页信息
from bs4 import BeautifulSoup   # 用于解析网页
import time                     # 用于控制访问速度
import re
import pymongo
import urllib.error
import http.client


# 1、获取网页，分析想获取的数据规则
# 2、通过如上规则，使用BeautifulSoup批量获取
# 3、通过如上规则，遍历整个网站的每一个页面

urlPreFix = "https://www.sex.com/"
targetUrl = urlPreFix

dbClient = pymongo.MongoClient('mongodb://127.0.0.1:27017')
sexDb = dbClient['sex']
data = sexDb['info']
success_counter = 0
failed_counter = 0
ignore_counter = 0
print("当前忽略已入库[{}]份, 下载失败[{}]份， 下载成功[{}]份".format(ignore_counter, failed_counter, success_counter))


# 将key与url入库mongdb
def mongdbHanlder(key, url):
    global success_counter
    global failed_counter
    global ignore_counter
    query_param = {'name': key}
    if data.find_one(query_param) is not None:
        print(key + "已经存在数据库中，不再入库")
        ignore_counter += 1
        return
    print("开始下载图片: " + key)
    try:
        pic_response = urllib.request.urlopen(url)
        pic_byte = pic_response.read()
    except Exception as error:
        print(error)
        print("图片：" + key + "下载失败...")
        failed_counter += 1
        return
    insert_param = {'name': key, 'url': url, 'data': pic_byte}
    print("开始入库图片: " + key)
    data.insert_one(insert_param)
    success_counter += 1


# 如果 alt 为空，则从url中获取名字
def handler(alt, url):
    if '' == alt:
        result = re.search("/([\d]+)\.", url)
        alt = result.group(1)
    return alt


# 用于提取资源目标url
def geturls(target):
    target = BeautifulSoup(target, 'html.parser')
    for img in target.find_all('img', src='/images/t.png'):
        # 获取 key
        alt = img.attrs['alt']
        # 获取 url
        url = img.attrs['data-src']
        # 预处理 key
        key = handler(alt, url)
        print(key + " : " + url)
        # 下载并入库
        mongdbHanlder(key, url)


counter = 1
while counter < 58:
    print('当前执行URL:' + targetUrl)
    try:
        html = urllib.request.urlopen(targetUrl)
        # 获取名称和url； 下载图片； 入库mongodb
        geturls(html)
        counter += 1
        targetUrl = urlPreFix + "?page=" + str(counter)
        print("当前忽略已入库[{}]份, 下载失败[{}]份， 下载成功[{}]份".format(ignore_counter, failed_counter, success_counter))
        print('休眠5秒...')
        time.sleep(5)
    except urllib.error.HTTPError as error:
        print(error)
        if error.code == 404:
            break
    except http.client.RemoteDisconnected as disconnected:
        print(disconnected)
        print('重新尝试...')
    except http.client.IncompleteRead as incompleted_read:
        print(incompleted_read)
        print('重新尝试...')


