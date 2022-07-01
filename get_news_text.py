import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:45.0) Gecko/20100101 Firefox/45.0'}  # 指定UA防止反爬
homepage = "https://tech.sina.com.cn/roll/"


def getOneArticle(url):
    re = requests.get(url)  # 下载页面
    re.raise_for_status()  # 若请求失败则抛出异常
    re.encoding = re.apparent_encoding  # 检测编码
    soup = BeautifulSoup(re.text)  # 解析HTML

    for s in soup('script'):
        s.extract()  # 丢弃HTML中的JS内容

    title = soup.select(".main-title")
    if len(title) == 0:
        title = soup.select("#artibodyTitle")
    title = title[0].text
    content = soup.find("div", id="artibody").text.strip()
    return title, content


def getPageLinks():
    global browser
    results = browser.find_elements_by_xpath('//div[@class="d_list_txt"]/ul/li/span/a')
    links = []
    for result in results:
        links.append(result.get_attribute('href'))
    return links


counter = 0
metadata = []  # (id, 标题)元组的列表
visited = set()

browser = webdriver.Chrome()
browser.implicitly_wait(10)
browser.get(homepage)  # 滚动新闻首页

while True:
    links = getPageLinks()  # 获取滚动新闻一个页面的所有新闻链接
    for link in links:
        if link not in visited:  # 避免重复爬取
            visited.add(link)

            title, content = getOneArticle(link)

            if len(content) >= 1000:  # 忽略1000字以下的文章
                counter += 1
                metadata.append((counter, title))  # 记录id与标题的对应关系
                with open("data/" + str(counter) + ".txt", "w", encoding='utf-8') as f:
                    f.write(content)
                print(counter, title, len(content), link)

    browser.execute_script("newsList.page.next();return false;")  # 翻页
    browser.implicitly_wait(10)  # 等待页面加载完毕
    if counter >= 1000:
        break

browser.close()
print("[+] Done.")

# 把新闻id及标题的对应关系写入csv文件
df = pd.DataFrame(metadata, columns=["id", "title"])
df.to_csv("metadata.csv", index=False, encoding="utf-8")