def parse_name(name_text):
    # Обезопасимся, если не сможем заполнить:
    name_marka, name_model = None, None

    # Делим строку на слова по пробелам
    words = name_text.split(' ')
    # Марка - это всегда первое слово
    name_marka = words.pop(0)
    # Модель - это остальные (кроме первого) слова
    name_model = ' '.join(words)

    # Возвращаем марку и модель
    return name_marka, name_model


if __name__ == "__main__":
    name_text = 'ТМЗ (Туламашзавод) Муравей'
    print(parse_name(name_text))
