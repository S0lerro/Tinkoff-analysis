from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import sqlite3


def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    return webdriver.Chrome(options=chrome_options)

def parse_data():
    url = "https://www.tbank.ru/invest/stocks/?start=0&end=12&orderType=Desc&sortType=ByPrice&currencies=RUB"
    driver = get_driver()
    driver.get(url)

    heading_list = []
    price_list = []
    percent_list = []
    for i in range(5):
        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")

        for heading in soup.find_all("div", class_="SecurityRow__text_h1nrb"):
            full_name = heading.find("div", class_="SecurityRow__showName_inlal SecurityRow__overflowFade_HRRj5")
            short_name = heading.find("div", class_="SecurityRow__ticker_KMm7A")
            if full_name and short_name:
                combined_name = f"{full_name.get_text(strip=True)} {short_name.get_text(strip=True)}"
                heading_list.append(combined_name)

        for price in soup.find_all("div", class_="DataTable__right_V1gy7"):
            price_element = price.find("span", class_="Money-module__money_UZBbh")
            if price_element:
                price_text = price_element.get_text(strip=True)
                if "+" not in price_text and "−" not in price_text:
                    price_list.append(price_text)

        for percent_pos in soup.find_all("span", class_=lambda value: value and value.startswith("ColorSignValue__nowrap_gx9IL ColorSignValue__")):
            percent_pos_get = percent_pos.find("span", attrs={"data-qa-file": "Money"})
            if percent_pos_get:
                percent_list.append(percent_pos_get.get_text(strip=True))
        try:
            driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div/div/div/div[3]/div[2]/div/a/span/div/button").click()
            time.sleep(5)

        except Exception as e:
            print(f"Не удалось найти кнопку пагинации: {e}")
            break

    driver.quit()
    return heading_list, price_list, percent_list


def csv_form():
    headings, prices, percents = parse_data()
    percentspday_list = []
    percentspyear_list = []
    for percentpday in range(0, len(percents), 2):
        percentspday_list.append(percents[percentpday])
    for percentpday in range(1, len(percents), 2):
        percentspyear_list.append(percents[percentpday])

    print(len(headings), len(prices), len(percentspday_list), len(percentspyear_list))

    df = pd.DataFrame({
        "Название": headings,
        "Цена": prices,
        "Изменение за день (Rub)": percentspday_list,
        "Изменение за год (Rub)": percentspyear_list
    })

    df.to_csv("Stocks.csv", index=False, encoding="utf-8")


def database():
    conn = sqlite3.connect('stocks.db')
    cursor = conn.cursor()

    # Полностью пересоздаем таблицу
    cursor.execute('DROP TABLE IF EXISTS stocks')
    cursor.execute('''
        CREATE TABLE stocks (
            "Название" TEXT NOT NULL,
            "Цена" TEXT NOT NULL,
            "Изменение за день (Rub)" TEXT NOT NULL,
            "Изменение за год (Rub)" TEXT NOT NULL
        )
    ''')

    # Читаем данные из CSV
    df = pd.read_csv('Stocks.csv', encoding='utf-8')

    # Вставляем данные
    for _, row in df.iterrows():
        cursor.execute('''
            INSERT INTO stocks ("Название", "Цена", "Изменение за день (Rub)", "Изменение за год (Rub)")
            VALUES (?, ?, ?, ?)
        ''', (row['Название'], row['Цена'],
              row['Изменение за день (Rub)'], row['Изменение за год (Rub)']))

    conn.commit()

    conn.close()
    print("База данных успешно создана и соответствует CSV файлу")

def main():
    csv_form()
    database()

if __name__ == "__main__":
    main()