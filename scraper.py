import requests
from bs4 import BeautifulSoup
import random
import pandas as pd
import openpyxl


def get_stock_list():
    url = 'https://www.tbank.ru/invest/stocks/'
    page = requests.get(url)
    encoding = page.encoding if 'charset' in page.headers.get('content-type', '').lower() else None
    soup = BeautifulSoup(page.content, 'lxml', from_encoding=encoding)
    stocks = soup.find_all("div", class_="SecurityRow__text_h1nrb w-full")

    stock_list = []
    if stocks is not None:
        for stock in stocks:
            formatted_name = stock.find("div", class_="SecurityRow__ticker_KMm7A").get_text()
            stock_list.append(formatted_name)
    return stock_list


def scrape_stock_data(stock_name):
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36 OPR/43.0.2442.991",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/604.4.7 (KHTML, like Gecko) Version/11.0.2 Safari/604.4.7"
    ]

    url = f"https://www.tbank.ru/invest/stocks/{stock_name}/pulse/"
    headers = {"User-Agent": random.choice(user_agents)}

    page = requests.get(url, headers=headers)
    encoding = page.encoding if 'charset' in page.headers.get('content-type', '').lower() else None
    soup = BeautifulSoup(page.content, 'lxml', from_encoding=encoding)

    scrapped_data = []
    posts = soup.find_all("div", class_="pulse-posts-by-ticker__dXTx8X")

    if posts is not None:
        for post in posts:
            data = {
                "author": post.find("span", class_="pulse-posts-by-ticker__aSULlZ").get_text(),
                "text": post.find("div",
                                  class_="pulse-posts-by-ticker__ffTK6Z pulse-posts-by-ticker__ifTK6Z").get_text(),
                "time": post.find("div", class_="pulse-posts-by-ticker__cSULlZ").get_text()
            }
            scrapped_data.append(data)

    # Сохраняем в Excel для анализа
    df = pd.DataFrame.from_dict(data=scrapped_data)
    df.index += 1
    df.to_excel("scrapping.xlsx", sheet_name='Tbank')

    return url, scrapped_data