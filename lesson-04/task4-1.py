'''
Задание. Написать приложение, которое собирает основные новости с сайта на выбор news.mail.ru, lenta.ru, yandex-новости. 
Для парсинга использовать XPath. Структура данных должна содержать:
название источника;
наименование новости;
ссылку на новость;
дата публикации.
Сложить собранные новости в БД
Минимум один сайт, максимум - все три
'''

from distutils.dep_util import newer_pairwise
from ntpath import join
from lxml import html
import requests
from pprint import pprint
import re
from datetime import date
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

# Подключение к БД 
client = MongoClient('192.168.8.3', 27017)
db = client['news']
news_db = db.news

url = 'https://yandex.ru/news/'
headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'}

news_add = 0
news_ignore = 0

response = requests.get(url, headers=headers)
dom = html.fromstring(response.text)

# Создаем список для хранения новостей
news = []
# Собираем все блоки новостей
news_list = dom.xpath("//div[contains(@class,'mg-grid__item')]")

# Проходим по новостям и формируем словарь
for item in news_list:
    news_info = {}
    names_temp = item.xpath(".//div//a[@class='mg-card__link']/text()")
    # Приводим строку с названием новости в нормальный вид
    names = ' '.join(names_temp).replace('\xa0', ' ',)
    links = item.xpath(".//div//a[@class='mg-card__link']/@href")
    source = item.xpath(".//div//a[@class='mg-card__source-link']/text()")
    times = item.xpath(".//div//span[@class='mg-card-source__time']/text()")
    # формируем уникальный id (из ссылки story=) для БД
    news_id = str(links).split('&')[-1].replace("story=", "")
    # Формируем словарь
    news_info['name'] = names
    news_info['link'] = links
    news_info['source'] = source
    news_info['time'] = times
    news_info['_id'] = news_id 
    # Добавляем словарь в список
    news.append(news_info)

    # Отсекаем пустые строки
    if news_info['name'] == "":
        continue
    else:
        # Передаем данные в БД
        try:
            news_db.insert_one(news_info)
            news_add += 1
        except DuplicateKeyError:
            news_ignore += 1

pprint(f'Новостей добавлено {news_add}')
pprint(f'Новостей проигнорировано (дубликат) {news_ignore}')