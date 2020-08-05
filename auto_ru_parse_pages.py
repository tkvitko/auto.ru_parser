import time
import wget
import os
import re
import logging

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from sys import argv
from translit import transliterate
from translit2 import transliterate2
from auto_ru_parse_desc import parse_description
from auto_ru_parse_name import parse_name

header = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
    'Accept': '*/*'}

chrome_options = Options()
chrome_options.add_argument('start-maximized')
# на всякий случай, без этого могло упасть по timeout:
chrome_options.add_argument('enable-features=NetworkServiceInProcess')
chrome_options.add_argument('--no-sandbox')
driver = webdriver.Chrome('./chromedriver', options=chrome_options)

# Лимиты для операций
max_offers_per_model = 100
max_offers_for_photo_per_model = 20
max_photoes_per_offer = 2

blocks_props = {
    1: 'bus',
    2: 'truck',
    3: 'artic',
    4: 'motorcycle',
    5: 'atv',
    6: 'moped',
    7: 'scooters',
    8: 'motoroller',
    9: 'bulldozer',
    10: 'bolotohod',
    11: 'snowmobile',
    12: 'buggi',
    13: 'tricycle',
    14: 'koleso_traktor',
    15: 'gus_traktor',
    16: 'combain',
    17: 'test'
}


def parse_type(type_url):
    # Работа с url, ведущем на страницу типа машины.
    # Пример URL: https://auto.ru/rossiya/agricultural/all/?agricultural_type=COMBAIN_HARVESTER

    driver.get(type_url)

    # Нажатие на конрол "показать все марки", если их слишком много
    try:
        #        button_xpass = "//*[contains(text(),'Все марки —')]"
        button_xpass = "//span[@class='Link ListingPopularMMM-module__expandLink']"
        button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, button_xpass))
        )
        button.click()
    except:
        pass

    # Сохраняем список URLs на марки:
    marks_urls_blocks = driver.find_elements_by_xpath("//a[@class='Link ListingPopularMMM-module__itemName']")
    logging.info(f'Marks count: {len(marks_urls_blocks)}')
    marks_urls = []  # каждый URL ведет на конкретную марку
    for i in range(len(marks_urls_blocks)):
        mark_name = marks_urls_blocks[i].text
        if mark_name.find('руг') == -1:
            mark_url = marks_urls_blocks[i].get_attribute('href')
            marks_urls.append(mark_url)

    return marks_urls


def parse_mark(mark_url):
    # Работа с url, ведущем на страницу марки машины.
    # Пример URL: https://auto.ru/rossiya/bus/citroen/all/

    driver.get(mark_url)

    # Нажатие на конрол "показать все модели", если моделей больше 12-ти
    try:
        #        button_xpass = "//*[contains(text(),'Все модели —')]"
        button_xpass = "//span[@class='Link ListingPopularMMM-module__expandLink']"
        button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, button_xpass))
        )
        button.click()
    except:
        pass

    # Сохраняем список URLs на модели:
    models_urls_blocks = driver.find_elements_by_xpath("//a[@class='Link ListingPopularMMM-module__itemName']")
    logging.info(f'Models count: {len(models_urls_blocks)}')
    models_urls = []  # каждый URL ведет на конкретную модель
    for i in range(len(models_urls_blocks)):
        model_name = models_urls_blocks[i].text
        if model_name.find('руг') == -1:
            model_url = models_urls_blocks[i].get_attribute('href')
            models_urls.append(model_url)

    return models_urls


def parse_model(model_url, block_number, download):
    # Работа с url, ведущем на страницу модели машины.
    # Пример URL: https://auto.ru/rossiya/atv/russkaya_mehanika/gamax_ax600/all/

    # Вынимаем параметры из url модели
    url_marka = re.split('/', model_url)[-4]
    url_model = re.split('/', model_url)[-3]

    url = model_url
    cars = []

    counter_offer = 1  # счетчик обработанных объявлений (до 100)
    counter_filename = 1  # счетчик именования файлов фоток (скачиваем фотки даже для отброшенных объявлений)
    counter_offers_for_photoes = 0  # счетчик объвлений, по которым качаем фотки (до 20)

    while counter_offer <= max_offers_per_model:
        driver.get(url)
        cars_block_list = driver.find_elements_by_xpath("//div[@class='ListingItem-module__main']")

        # МЕДЛЕННО Скроллимся до низа страницы, чтобы подтянулись url на картинки

        if cars_block_list:
            actions = ActionChains(driver)
            for i in range(len(cars_block_list)):
                if i%6 == 0:    # достаточно такого шага, чтобы подгружались все фото
                #if i%5 == 0:   #first try
                    actions.move_to_element(cars_block_list[i])
            actions.move_to_element(cars_block_list[-1])
            actions.perform()

        # Вынимаем всё нужное из блока машины
        for car_block in cars_block_list:
            car = {}

            name_block = car_block.find_element_by_class_name('ListingItemTitle-module__link')
            name_text = name_block.text
            car['name_marka'], car['name_model'] = parse_name(name_text)
            car['nameplate'] = None

            # Транслитерация. Функция с "2" - библиотечная, функция без "2" - с ручным редактированием словаря
            car['rus_marka'] = transliterate(car['name_marka'])
            car['rus_model'] = transliterate(car['name_model'])
            car['rus_nameplate'] = None

            car['url_marka'] = url_marka
            car['url_model'] = url_model
            car['url_nameplate'] = None

            year_text = car_block.find_element_by_class_name('ListingItem-module__year').text
            car['year'] = year_text
            # motor_string = car_block.find_element_by_class_name('ListingItemTechSummaryDesktop__cell').text
            # car['dvigatel'] = motor_string

            descr_string = car_block.find_element_by_class_name('ListingItemTechSummaryDesktop__column').text
            car['dvigatel'], car['vsm3'], car['ls'], car['toplivo'], car['info'] = parse_description(descr_string)

            car['url_site'] = name_block.get_attribute('href')
            dest_block_folder = f"{blocks_props[block_number]}"
            dest_marka_folder = f"{url_marka}"
            dest_model_folder = f"{url_model}"

            if download:
                if counter_offers_for_photoes < max_offers_for_photo_per_model:
                    try:
                        imgs_urls_list = car_block.find_elements_by_class_name('LazyImage__image')
                        # Выбираем не больше 4 фоток для скачивания:
                        if len(imgs_urls_list) > max_photoes_per_offer:
                            imgs_urls_list = imgs_urls_list[:max_photoes_per_offer]
                        #        imgs_urls_list = car_block.find_elements_by_xpath("//img[@class='LazyImage__image']")
                        for i in range(len(imgs_urls_list)):
                            dest_folder = os.path.join(dest_block_folder, dest_marka_folder, dest_model_folder)
                            # создание папки, если ее нет
                            os.makedirs(dest_folder, exist_ok=True)
                            # получение url на картинку
                            url_img = imgs_urls_list[i].get_attribute('src')
                            # преобразование url для того, чтобы получить большую картинку вместо маленькой
                            url_big = re.sub('320x240', '1200x900n', url_img)
                            # формирование имени файла картинки
                            filename = f'{blocks_props[block_number]}_{url_marka}_{url_model}_{counter_filename}_{i + 1}.webp'
                            # формирование полного пути для скачивания картинки
                            destination = os.path.join(dest_folder, filename)
                            wget.download(url_big, out=destination)
                        counter_filename += 1
                        counter_offers_for_photoes += 1
                    except:
                        print('except')

            # По умолчанию берем все объявления
            drop_this_car = False

            # Локальные правила блоков для отсева объявлений
            if block_number == 4 or block_number == 13:
                if not car['ls'] or car['ls'] < 25:
                    drop_this_car = True

            if block_number == 7:
                if car['vsm3'] and car['vsm3'] < 51:
                    drop_this_car = True

            if block_number == 14 or block_number == 15 or block_number == 16:
                if not car['ls']:
                    drop_this_car = True

            # Если ни одно из локальных правил не сработало, берем объявение
            if drop_this_car == False:
                # Не оптимально, лишние объявления будут парситься, но отбрасываться.
                if counter_offer <= max_offers_per_model:
                    cars.append(car)
                    counter_offer += 1

        # Переход на следующую страницу, если она есть
        try:
            next_url = driver.find_element_by_xpath(
                "//a[@class='Button Button_color_white Button_size_s Button_type_link Button_width_default ListingPagination-module__next']").get_attribute(
                'href')
            url = next_url
            time.sleep(0.1)
        except:
            break

    return (cars)
