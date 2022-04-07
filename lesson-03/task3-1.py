'''
Задание: Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы получаем должность) с 
сайтов HH(обязательно) и/или Superjob(по желанию). Приложение должно анализировать несколько страниц сайта (также вводим через input 
или аргументы). Получившийся список должен содержать в себе минимум:

Наименование вакансии.
Предлагаемую зарплату (разносим в три поля: минимальная и максимальная и валюта. цифры преобразуем к цифрам).
Ссылку на саму вакансию.
Сайт, откуда собрана вакансия.
По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение). Структура должна быть одинаковая для вакансий 
с обоих сайтов. Общий результат можно вывести с помощью dataFrame через pandas. Сохраните в json либо csv.
'''

#https://hh.ru/search/vacancy?search_field=name&search_field=company_name&search_field=description&text=python

from os import urandom
from posixpath import split
from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint
import json
from pymongo import MongoClient
import re
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
import time

# Подключение к БД 
client = MongoClient('192.168.8.3', 27017)
db = client['vacancy']
vacancies_db = db.vacancy
# Переменные для подсчета количества добавленных и игнорированных вакансий
data_add = 0
data_ignore = 0

def salary_parsing(compensation: str):
    '''
    Функция парсит данные о зарплате:
    salary_min - минимальная зарплата
    salary_max - максимальная зарплата
    currency - валюта
    '''
    global salary_min 
    global salary_max 
    global currency 
    prefix = ('от', 'до')

    if compensation:
        if compensation.startswith(prefix):
            if compensation.startswith('от'):
                salary_min = int(compensation.split()[1])
                salary_max = None
                currency_temp = compensation.split()[2:]
                currency = " ".join(currency_temp)
               
            elif compensation.startswith('до'):
                salary_min = None
                salary_max = int(compensation.split()[1])
                currency_temp = compensation.split()[2:]
                currency = " ".join(currency_temp)
                
        elif compensation.find("-"):
            temp_rez = compensation.split() #.replace('.', '')
            salary_min = int(temp_rez[0])
            salary_max = int(temp_rez[2])
            currency_temp = temp_rez[3:]
            currency = " ".join(currency_temp)
    else:
        salary_min = None
        salary_max = None 
        currency = None
    return salary_min, salary_max, currency

vacancy_name = input("Введите ключевое слово для поиска: ")

base_url = 'https://hh.ru'
headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'}

params = {
    'search_field':'company_name',
    'search_field':'description',
    'text':vacancy_name,
    'items_on_page':'20',
    'page':'0',
    'hhtmFrom':'vacancy_search_list'
}

url = base_url + '/search/vacancy?'
response = requests.get(url, params=params, headers=headers)
dom = bs(response.text, 'html.parser')

def max_num():
    '''
    Функция определяет сколько страниц 
    поиска доступно
    '''
    max_num = 0
    for item in dom.find_all('a', {'data-qa': 'pager-page'}):
        max_num = list(item.strings)[0].split(' ')[-1]
    return max_num

vacancy_list = []
max_page = int(max_num())

for i in range(max_page):
    url2 = base_url + '/search/vacancy?'
    response2 = requests.get(url2, params=params, headers=headers)

    dom2 = bs(response2.text, 'html.parser')
    vacancies = dom2.find_all('div', {'class':'vacancy-serp-item'})

    for vacancy in vacancies: 
        vacancy_data = {}
        # Отлавливаем блок с рекламой, иначе будет ошибка
        reklama = vacancy.find('h4', {'class': 'bloko-header-section-4'}) #.getText()
        if reklama == None:
            pass
        else:
            continue 
        # vacancy_name = vacancy.find('span', {'class': 'g-user-content'}).getText()C
        vacancy_name = vacancy.find('a', {'class': 'bloko-link'}).getText()
        vacancy_url = vacancy.find('a', {'class': 'bloko-link'})['href']
        vacancy_comp = vacancy.find('div', {'class': 'vacancy-serp-item__meta-info-company'}).getText().replace('\xa0', ' ')
        vacancy_address = vacancy.find('div', {'class': 'bloko-text_no-top-indent'}).getText().replace('\xa0', ' ')
        # Извлекаем номер вакансии для id
        vacancy_id_temp = re.findall(r'\d+', vacancy_url)
        # Так как есть ссылки на вакансии с цифрами кроме номера, проверяем это
        if len(vacancy_id_temp) >= 1:
            vacancy_id = vacancy_id_temp[0]
        else:
            vacancy_id = vacancy_id_temp
            
        # Готовим данные о зп 
        vacancy_salary = vacancy.find('span', {'class': 'bloko-header-section-3'})
        if vacancy_salary:
            vacancy_salary = vacancy_salary.text.replace('\u202f', '',)
            salary_parsing(vacancy_salary)
        else:
            vacancy_salary = None
            salary_parsing(vacancy_salary)

        # Формируем словарь
        vacancy_data['name'] = vacancy_name 
        vacancy_data['url'] = vacancy_url
        vacancy_data['company'] = vacancy_comp
        vacancy_data['comp_min'] = salary_min
        vacancy_data['comp_max'] = salary_max
        vacancy_data['currency'] = currency
        vacancy_data['address'] = vacancy_address
        vacancy_data['_id'] = vacancy_id

        # Передаем данные в БД
        try:
            vacancies_db.insert_one(vacancy_data)
            data_add += 1
        except DuplicateKeyError:
            data_ignore += 1
    # Увеличиваем счетчик для следующей ссылки
    params["page"] = str(i + 1)

print(f'Вакансий добавлено {data_add}')
print(f'Вакансий проигнорировано (дубликат) {data_ignore}')
