from transliterate import translit, get_available_language_codes


def transliterate2(name):
    return translit(name, 'ru')


if __name__ == "__main__":
    text = "Renault"
    print(translit(text, 'ru'))
