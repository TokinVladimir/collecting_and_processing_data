from ssl import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo.errors import DuplicateKeyError
from pymongo import MongoClient
import time

# Подключение к БД 
client = MongoClient('192.168.8.3', 27017)
db = client['product']
products_db = db.product

options = Options()
options.add_argument("--start-maximized")

s = Service('/Users/vladimir/Documents/collecting_and_processing_data/lesson-05/chromedriver')

driver = webdriver.Chrome(service=s, options=options)
driver.implicitly_wait(15)

driver.get('https://www.dns-shop.ru/')

# Тыкаем кнопку, что наш город Москва
button = driver.find_element(By.XPATH, "//a[contains(@class,'btn btn-additional')]")
button.click()

# ТЫкнуть по Москва для выбора города
button = driver.find_element(By.XPATH, "//div[contains(@class,'header-top-menu__common-link header-top-menu__common-link_city')]")
button.click()

#Вводим город Хабаровск и жмем Энтер
button = driver.find_element(By.XPATH, "//input[contains(@class,'form-control')]")
button.send_keys("Хабаровск") 
button.send_keys(Keys.ENTER)

# Переходим в уцененные товар
time.sleep(1)
button = driver.find_element(By.XPATH, "//div[@class='menu-desktop__root menu-root__markdown']//a[contains(@class,'ui-link menu-desktop__root-title')]")
button.click()

while True:
    try :
       
        products_list = driver.find_elements(By.XPATH, "//div[@class='catalog-products view-simple']/div[contains(@class,'catalog-product')]")

        for p in products_list:
            data_info = {}
            # Наименование товара
            name = p.find_element(By.XPATH, ".//a[contains(@class,'catalog-product__name ui-link ui-link_black')]").text
            # Цена актуальная
            price_actual = p.find_element(By.XPATH, "//div[contains(@class,'catalog-product__price-actual')]").text
            # Цена до уценки
            price_old = p.find_element(By.XPATH, "//div[contains(@class,'catalog-product__price-old')]").text
            # вид ремонта
            info = p.find_element(By.XPATH, "//div[contains(@class,'catalog-product__reason-text-block')]").text

            # Формируем словарь
            data_info['name'] = name
            data_info['price_actual'] = price_actual
            data_info['price_old'] = price_old
            data_info['info'] = info

        # Передаем данные в БД
        try:
            products_db.insert_one(data_info)
        except DuplicateKeyError:
            pass

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'pagination-widget__show-more-btn')]"))).click()

    except :
        print("No more pages left")
        break