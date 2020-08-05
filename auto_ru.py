import pandas as pd
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

from auto_ru_parse_pages import parse_mark
from auto_ru_parse_pages import parse_type
from auto_ru_parse_pages import parse_model

# Глобальные настройки
logging.basicConfig(level=logging.INFO)

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

# Классификация блоков по типу url в них
model_links_blocks = [5, 8, 17]
mark_links_blocks = [1, 2, 3, 4, 6, 7, 9, 10, 11]
type_links_blocks = [12, 13, 14, 15, 16]


def go_parse(models_list):
    # Парсинг данных на странице модели и складирование в словарь

    for model in models_list:
        # Дебаг для 1 модели:
        #model = models_list[0]
        cars_new = parse_model(model, block_number, download)
        for car in cars_new:
            cars.append(car)
        #        print(car)
        logging.info(f'{model} done')


if __name__ == "__main__":
    #block_number = 3
    script, block_number_str, download = argv
    block_number = int(block_number_str)

    with open(f'auto_ru_source_urls/{block_number}.txt', 'r') as source:
        source_links = source.read().splitlines()

    cars = []

    if block_number in model_links_blocks:
        models_list = source_links
        go_parse(models_list)

    elif block_number in mark_links_blocks:
        for source_link in source_links:
            # Дебаг для одного URL:
            #source_link = source_links[0]
            models_list = parse_mark(source_link)
            go_parse(models_list)

    elif block_number in type_links_blocks:
        for source_link in source_links:
            marks_list = parse_type(source_link)
            for mark_link in marks_list:
                models_list = parse_mark(mark_link)
                go_parse(models_list)

    # Сохранение в csv
    df = pd.DataFrame(cars)
    csv_name = f'a_{blocks_props[block_number]}.csv'
    df.to_csv(csv_name)
    logging.info(f'{csv_name} has been created')
