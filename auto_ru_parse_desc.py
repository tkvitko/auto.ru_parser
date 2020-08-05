import re


def parse_description(description):
    step1 = re.sub('\u2009', ' ', description)
    step2 = re.sub('\n', '/', step1)
    chars = step2.split('/')

    motor_list = description.split('\n')
    motor_string = None

    # 3 попытки найти описание двигателя в блоке текста
    # 3 подстроки для поиска
    substr = 'л.с.'
    substr2 = 'см'
    substr3 = ' л'

    # первая попытка по первой подстроке поиска
    res = (s for s in motor_list if substr.lower() in s.lower())
    for i in res:
        if i:
            motor_string = i

    # вторая попытка по второй подстроке поиска
    res2 = (s for s in motor_list if substr2.lower() in s.lower())
    for i in res2:
        if i:
            motor_string = i

    # третья попытка по третьей подстроке поиска
    res3 = (s for s in motor_list if substr3.lower() in s.lower())
    for i in res3:
        if i:
            motor_string = i

    # Пробуем вынуть из блока текста нужные значения
    # Очень осторожно, т.к. их там может не быть
    capacity_l, capacity_sm, power, lifting, fuel = None, None, None, None, None

    capacity_l_list = [i for i in chars if ' л' in i]
    capacity_sm_list = [i for i in chars if 'см' in i]
    power_list = [i for i in chars if 'л.' in i]
    lifting_list = [i for i in chars if ' т' in i]

    # Тип топлива заполянем, если среди слов нашлись конкретные названия
    if chars.count(' Бензин') != 0:
        fuel = 'Бензин'
    elif chars.count(' Дизель') != 0:
        fuel = 'Дизель'

    # Переходим от списков, созданных генератором, к значениям
    capacity_l_val, capacity_sm_val, power_val, lifting_val = None, None, None, None
    capacity_res, capacity_l_res, capacity_sm_res, power_res, lifting_res = None, None, None, None, None

    # Пробуем заполнить значения

    # По объему заполняем или значение сантиметров, или литров
    if capacity_sm_list:
        capacity_sm = capacity_sm_list[0]
        capacity_sm_val = re.findall(r'\d+ ?\d*', capacity_sm)
        if capacity_sm_val:
            capacity_res = int(capacity_sm_val[0].replace(' ', ''))
    elif capacity_l_list:
        capacity_l = capacity_l_list[0]
        capacity_l_val = re.findall(r'\d+\.+\d+', capacity_l)
        if capacity_l_val:
            capacity_res = float(capacity_l_val[0])

    # Лошадиные силы
    if power_list:
        power = power_list[0]
        power_val = re.findall(r'\d+', power)
        if power_val:
            power_res = int(power_val[0])

    # Грузоподъемность
    if lifting_list:
        lifting = lifting_list[0]
        lifting_val = re.findall(r'\d+\.+\d+', lifting)
        if lifting_val:
            lifting_res = float(lifting_val[0])

    # Функция всегда вернет 5 значений (возможно, пустые)
    return (motor_string, capacity_res, power_res, fuel, lifting_res)


if __name__ == "__main__":
    # descr1 = 'Городской\n2.2 л\u2009/\u2009131 л.с.'
    descr2 = 'изотермический фургон\nг/п 3.0 т\n0.02 л\u2009/\u2009136 л.с.\u2009/\u2009Бензин'
    # descr3 = '12.0 л\u2009/\u2009430 л.с.\u2009/\u2009Дизель\n2-х местная с 2 спальными'
    # descr4 = '110 см³\u2009/\u200911 л.с.\u2009/\u20094 такта\n1 цилиндр'
    #
    # descr6 = '1 см³\u2009/\u20092 такта\n2 передачи'
    # descr7 = '200 см³\u2009/\u20094 такта\nВариатор'
    descr8 = '2 см³\u2009/\u200912 л.с.\u2009/\u20092 такта'
    descr10 = '1 600 см³\u2009/\u200957 л.с.\u2009/\u20094 такта\n4 цилиндра / рядное\nПолуавтомат'
    # descr11 = '565 см³\u2009/\u200957 л.с.\u2009/\u20092 такта\n2 цилиндра'
    # descr12 = '20 000 см³'
    descr13 = '250 см³\u2009/\u200920 л.с.\n1 цилиндр / рядное\n5 прямых и задняя'
    # descr14 = 'колесный трактор\n1000 л.с.'
    # descr15 = 'гусеничный трактор\n3.9 л\u2009/\u2009125 л.с.'
    # descr16 = 'комбайн\n6.4 л\u2009/\u2009258 л.с.'

    mot, cap, pow, lif, fuel = parse_description(descr10)
    print(mot)
    print(cap)
    print(pow)
    print(lif)
    print(fuel)
