import re
import requests


# Номер, с которого начинается название валюты
name_start_point = 22


# Класс, с помощью которого будем считывать данные сайта
class Crypto:

    def __init__(self):
        # Получаем код сайта
        self.response = requests.get('https://www.coingecko.com/en')

    def get_list(self):
        # Вытаскиваем числа, отвечающие за капитализацию, цену и дневной оборот
        numbers = re.findall(r'[$]\d+.\d+', self.response.text)
        prices = []
        for i in range(len(numbers)):
            # Выбираем из них, содержащие цену
            if i % 3 == 0:
                prices.append(numbers[i])
            # Вытаскиваем названия монет
        names = re.findall(r'coin-name" data-text=\'\w+', self.response.text)
        names = [names[i][name_start_point:-1]+ names[i][-1] for i in range(len(names))]
        return names, prices
