# import pymongo
import datetime
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from pyquery import PyQuery as pq
import pandas as pd
import time
from urllib.parse import quote

# MONGO_URL = 'localhost'
# MONGO_DB = 'taobao'
# MONGO_COLLECTION = 'products'
# client = pymongo.MongoClient(MONGO_URL)
# db = client[MONGO_DB]

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
browser = webdriver.Chrome(chrome_options=chrome_options)
# browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10)


def index_page(page, KEYWORD):
    """
    抓取索引页
    :param page: 页码
    """
    print('正在爬取第', page, '页')
    try:
        # https://list.tmall.com/search_product.htm?s=60&q=%B0%B2%CC%A4&sort=s&style=g
        url = 'https://s.taobao.com/search?q=' + quote(KEYWORD)
        browser.get(url)
        if page > 1:
            input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager div.form > input')))
            submit = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager div.form > span.btn.J_Submit')))
            input.clear()
            input.send_keys(page)
            submit.click()
        wait.until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#mainsrp-pager li.item.active > span'), str(page)))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.m-itemlist .items .item')))
        get_products(KEYWORD)
    except TimeoutException:
        time.sleep(5)
        index_page(page,KEYWORD)


def get_products(KEYWORD):
    """
    提取商品数据
    """
    html = browser.page_source
    doc = pq(html)
    items = doc('#mainsrp-itemlist .items .item').items()
    for item in items:
        product = {
            'keyword': KEYWORD,
            # 'image': item.find('.pic img').attr('data-src').replace('\n',''),
            'price': item.find('.price').text().replace('\n', ''),
            'deal': item.find('.deal-cnt').text().replace('\n', ''),
            'title': item.find('.title').text().replace('\n', ''),
            'shop': item.find('.shop').text().replace('\n', ''),
            'location': item.find('.location').text().replace('\n', '')
        }
        # print(product)
        save_to_mongo(product)


def save_to_mongo(result):
    """
    保存至MongoDB
    :param result: 结果
    """
    dt = datetime.datetime.now()
    dt_str = dt.strftime('%Y-%m-%d')

    with open(f'Data_result_{dt_str}.csv', 'a', encoding='utf-8') as f:
        f.write(
            f"{result['keyword']},{result['title']},{result['shop']},{result['location']},{result['price']},{result['deal']}\n")

    # try:
    #     if db[MONGO_COLLECTION].insert(result):
    #         print('存储到MongoDB成功')
    # except Exception:
    #     print('存储到MongoDB失败')


def main():
    """
    遍历每一页
    """
    KEYWORDS = ['安踏']
    MAX_PAGE = 20
    for word in KEYWORDS:
        for i in range(1, MAX_PAGE + 1):
            index_page(i, word)
    browser.close()


if __name__ == '__main__':
    main()
