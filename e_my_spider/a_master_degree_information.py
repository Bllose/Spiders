import urllib.request           # http
from bs4 import BeautifulSoup   # 解析网页
import re                       # 正则表达式
import bs4.element              # bs下的元素类型


# yjxkdm - 一级学科代码
# zymc - 专业名称
# (0775)计算机科学与技术
# (0812)计算机科学与技术
# (0835)软件工程
# (0854)电子信息

# xxfs=2 非全日制
request_data = "ssdm=&dwmc=&mldm=zyxw&mlmc=&yjxkdm=0775&zymc=&xxfs=2"
# ssdm=&dwmc=&mldm=&mlmc=&yjxkdm=0854&zymc=&xxfs=2&pageno=2
# pageno=2 第二页

urlString = "https://yz.chsi.com.cn/zsml/queryAction.do"


# post 请求获取页面信息
def gethtml(request_data, urlString):
    request_data = request_data.encode("utf-8")
    url = urllib.request.Request(urlString, request_data)
    result = urllib.request.urlopen(url)
    response = result.read()
    return response.decode("utf-8")


# 用以判断数据量，包含多少页
# 多页的情况下分页面进行分析
def analy_pages(html_data):
    target = BeautifulSoup(html_data, 'html.parser')
# 由于网页上并没有显性地显示数量，所以通过换页的数量来判断
    page_tags = target.find_all(onclick=re.compile('nextPage'))


    bigest_no = 1
    for link in page_tags:
        #print(type(link.string))

        try:
            currect_no = int(link.string)
            if bigest_no < currect_no:
                bigest_no = currect_no
        except ValueError as error:
            # print(error)
            print("非数字项，跳过当前项")
    return bigest_no


# 用以分析当前页面中院校的信息
def analy_informations(html_data):
    target = BeautifulSoup(html_data, 'html.parser')

    #将每一栏学校的网址取出，然后跳转到对应地址获取数据
    for url_tag in target.find_all('a', href=re.compile('/zsml/querySchAction.do?')):
        url = 'https://yz.chsi.com.cn' + str(url_tag['href'])
        name = url_tag.string

        #打印当前学校名称
        print(name)
        html_ = BeautifulSoup(gethtml('', url), 'html.parser')

        # 将当前学校信息拼装成一行信息输出
        information = ''
        for list in html_.find_all('td'):
            if isinstance(list.string, bs4.element.NavigableString):
                information = information + list.string + '\t'
            else:
                # 将当前专业详细信息页面地址取出，附带在信息最后
                if isinstance(list.a, bs4.element.Tag):
                    if(list.a.string == '查看'):
                        url_final = 'https://yz.chsi.com.cn' + str(list.a['href'])
                        information = information + url_final + '\n'

        print(information)   # for 循环结束


html_data = gethtml(request_data, urlString)
page_amount = analy_pages(html_data)
print("最大页数:" + str(page_amount))

# 打印第一页
analy_informations(html_data)

# 打印更多页面
#ssdm=&dwmc=&mldm=&mlmc=&yjxkdm=0854&zymc=&xxfs=2&pageno=2
currect_page = 2
if page_amount > 1:
    while currect_page <= page_amount:
        print("当前打印第 "+str(currect_page)+" 页")
        request_data = 'ssdm=&dwmc=&mldm=&mlmc=&yjxkdm=0854&zymc=&xxfs=2&pageno=' + str(currect_page)
        html_data = gethtml(request_data, urlString)
        analy_informations(html_data)
        currect_page += 1
