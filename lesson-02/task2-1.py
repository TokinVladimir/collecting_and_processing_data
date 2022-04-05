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

#https://khabarovsk.hh.ru/search/vacancy?search_field=name&search_field=company_name&search_field=description&text=python

from os import urandom
from posixpath import split
from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint
import json

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
                salary_min = compensation.split()[1]
                salary_max = None
                currency = compensation.split()[2]
            elif compensation.startswith('до'):
                salary_min = None
                salary_max = compensation.split()[1]
                currency = compensation.split()[2]
        elif compensation.find("-"):
            # salary_min, temp, salary_max, currency = compensation.split() 
            temp_rez = compensation.split() #.replace('.', '')

            if len(temp_rez) > 4:
                salary_min = temp_rez[0]
                salary_max = temp_rez[2]
                currency = temp_rez[3] + temp_rez[4]
            else:
                salary_min = temp_rez[0]
                salary_max = temp_rez[2]
                currency = temp_rez[3]
    else:
        salary_min = None
        salary_max = None 
        currency = None
    return salary_min, salary_max, currency

vacancy_name = input("Введите ключевое слово для поиска: ")
index = input("Введите сколько страниц искать (цифрой): ")

base_url = 'https://khabarovsk.hh.ru'
headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'}

params = {
    'search_field':'company_name',
    'search_field':'description',
    'text':vacancy_name,
    'page':'0',
    'hhtmFrom':'vacancy_search_list'
}

vacancy_list = []

for i in range(int(index)):
    url = base_url + '/search/vacancy?'
    response = requests.get(url, params=params, headers=headers)

    # Проверяем, что сслыка валидная   
    if response:
        
        dom = bs(response.text, 'html.parser')
        vacancies = dom.find_all('div', {'class':'vacancy-serp-item'})
        
        for vacancy in vacancies:   
            vacancy_data = {}
            vacancy_name = vacancy.find('span', {'class': 'g-user-content'}).getText()
            vacancy_url = vacancy.find('a', {'class': 'bloko-link'})['href']
            vacancy_comp = vacancy.find('div', {'class': 'vacancy-serp-item__meta-info-company'}).getText().replace('\xa0', ' ')
            vacancy_address = vacancy.find('div', {'class': 'bloko-text_no-top-indent'}).getText().replace('\xa0', ' ')
            
            # Готовим данные о зп )
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

            # Словарь добавляем в список
            vacancy_list.append(vacancy_data)

            # Сохраняем vacancy_list в json файл
            with open('vacancy_data.json', 'w') as f:
                json.dump(vacancy_list, f)
        params["page"] = str(i + 1)
    else:
        print(f'Старницы с номером {i} не существует, поиск окончен')
        exit()

# pprint(vacancy_list)
