'''
Задание 1. Посмотреть документацию к API GitHub, разобраться как вывести список наименований 
репозиториев для конкретного пользователя, сохранить JSON-вывод в файле *.json.
'''

import requests
import json

username = 'TokinVladimir'
url = 'https://api.github.com/users/'+username+'/repos'

response = requests.get(url)
j_data = response.json()

with open('repos_data.json', 'w') as f:
    json.dump(j_data, f)

print(f'Список репозиториев пользователя {username}:')
for i in j_data:
    print(i['name'])