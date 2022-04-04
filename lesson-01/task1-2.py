'''
Задание 2. Изучить список открытых API (https://www.programmableweb.com/category/all/apis). Найти среди них любое, 
требующее авторизацию (любого типа). Выполнить запросы к нему, пройдя авторизацию. Ответ сервера записать в файл.
'''

'''
Получаем фотографии с марсохода через api Nasa
'''

import random
import requests
from pprint import pprint
import urllib.request

# Список где будем хранить ссылки на фото
list_url = []

URL = "https://api.nasa.gov/mars-photos/api/v1/rovers/perseverance/latest_photos"

params = {
    'api_key':'NepooK1No67ezfp05kAmxoqIwfzoUMoJDSsWqann'
}
response = requests.get(URL,params=params).json()

# Формируем список ссылками на фото
for i in response['latest_photos']:
    list_url.append(i['img_src'])

# Выбираем случайное фото из списка
url_foto = random.choice(list_url)

# скачиваем фото по ссылке и сохраняем
r = urllib.request.urlopen(url_foto)
with open("foto1.jpg", "wb") as f:
    f.write(r.read())