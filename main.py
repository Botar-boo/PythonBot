import asyncio
import config
import re

from aiogram import Bot, Dispatcher, executor, types
from collections import defaultdict
from sqlighter import SQLighter

from crypto import Crypto

# Инициализируем бота
TOKEN = os.getenv("token")
bot = Bot(TOKEN)

dp = Dispatcher(bot)

db = SQLighter('new_db.db')
# Инициализурем первый парсинг сайта для корректной дальнейшей работы
first_cr = Crypto()
# Порфтели всех пользователей
custom_portfolio = {}

# Инициализируем цены для того, чтобы в дальнейшем отслеживать их изменение
prev_prices = first_cr.get_list()
crypto_current = first_cr.get_list()


# Переводим названия всех валют в нижний регистр
def make_lower(crypto_cur):
    for i in range(len(crypto_cur[0])):
        crypto_cur[0][i] = crypto_cur[0][i].lower()
    return crypto_cur


# Инициализируем crypto_cur, парся сайт
def initialize(crypto_cur, lower):
    new_cr = Crypto()
    crypto_cur = new_cr.get_list()
    if lower:
        crypto_cur = make_lower(crypto_cur)
    return crypto_cur


# Парсим сообщение пользователя
def process_message(message):
    msg = re.findall(r'.+', message)
    msg[0].replace(',', '.')
    return msg[0].replace(',', '.').split(' ')


# Добавляем эмоджи к сообщению пользователя в зависимости от изменения валюты
def emoji_mes(result, message, index):
    if result[1][index] > prev_prices[1][index]:
        message += '📈' + '\n'
    elif result[1][index] < prev_prices[1][index]:
        message += '📉' + '\n'
    else:
        message += '🚦' + '\n'
    return message


# Печатаем все про монету,на которую подписан пользователь
def print_coin(result, message, s, index):
    if db.is_subscribed(s[1], result[0][index].lower()):
        message += result[0][index] + ' - ' + result[1][index][1:] + '$'
        message = emoji_mes(result, message, index)
    return message


# Приветствие
@dp.message_handler(commands=['start'])
async def subscribe(message: types.Message):
    await message.answer('Добро пожаловать в клуб верующих в код! Для того, чтобы подписаться на ежечасную ' +
                         'сводку по криптовалюте напишите "/{cryptocurrency_name}", например "/bitcoin". ' +
                         'Для того, чтобы отписаться от сводки по данной валюте, повторите описанную команду. ' +
                         'Чтобы ЗАПУСТИТЬ свой криптопорфтель, напишите /start_game {num in USD}. ' +
                         'Командами /buy, /sell и /my_portfolio можно работать со своим криптопортфелем. ' +
                         'Применение функции /buy симулирует покупку криптовалюты в указанном размере USD. ' +
                         'Применение функции /sell симулирует продажу криптовалюты в указанном размере USD' +
                         '(работают валюты из топ 100 coingecko).')


# Подписка на валюты, соответствующие командам
@dp.message_handler(commands=['bitcoin', 'xrp', 'ethereum', 'cardano', 'tether'])
async def subscribe_cryptocurrency(message: types.Message):
    if not db.subscriber_exists(message.from_user.id):
        db.add_subscriber(message.from_user.id)
    if not db.is_subscribed(message.from_user.id, message.text[1:]):
        db.update_cryptocurrency_subscription(message.from_user.id, message.text[1:], 1)
        await message.answer("Вы успешно подписаны на " + message.text[1:])
    else:
        db.update_cryptocurrency_subscription(message.from_user.id, message.text[1:], 0)
        await message.answer("Вы успешно отписаны с " + message.text[1:])


# Вывод всего портфеля
@dp.message_handler(commands=['my_portfolio'])
async def print_portfolio(message: types.Message):
    ans_message = ''
    total = 0
    global crypto_current
    crypto_current = initialize(crypto_current, True)
    # Пробегаемся по всем валютам в портфеле и выводим кол-во USD, лежащих в них
    for coin_name, coin_amount in custom_portfolio[message.from_user.id].items():
        if coin_name != 'USD':
            index = crypto_current[0].index(coin_name)
            ans_message += coin_name
            ans_message += ': ' + ("{:.2f}".format(coin_amount *
                                                   float(crypto_current[1][index][1:].replace(',', '')))) + '$\n'
            total += coin_amount * float(crypto_current[1][index][1:].replace(',', ''))
        else:
            ans_message += 'USD: ' + ("{:.2f}".format(coin_amount)) + '$\n'
            total += coin_amount
    total = "{:.2f}".format(total)
    await message.answer(ans_message + 'Common: ' + total + '$')


# Симулирование покупки валюты
@dp.message_handler(commands=['buy'])
async def buy_portfolio(message: types.Message):
    msg_ar = process_message(message.text)
    global crypto_current
    crypto_current = initialize(crypto_current, True)
    if msg_ar[1].lower() in crypto_current[0]:
        index = crypto_current[0].index(msg_ar[1].lower())
        crypto_price = float(crypto_current[1][index][1:].replace(',', ''))
        # Обработка случаев
        if float(msg_ar[2]) > custom_portfolio[message.from_user.id]['USD']:
            await message.answer('Недостаточно USD')
        else:
            custom_portfolio[message.from_user.id][msg_ar[1].lower()] += float(msg_ar[2]) / crypto_price
            custom_portfolio[message.from_user.id]['USD'] -= float(msg_ar[2])
            await message.answer('Монета успешно приобретена')
    else:
        await message.answer('Валюта не найдена')


# Симулирование продажи валют
@dp.message_handler(commands=['sell'])
async def sell_portfolio(message: types.Message):
    msg_ar = process_message(message.text)
    global crypto_current
    crypto_current = initialize(crypto_current, True)
    if msg_ar[1].lower() in crypto_current[0]:
        index = crypto_current[0].index(msg_ar[1].lower())
        crypto_price = float(crypto_current[1][index][1:].replace(',', ''))
        # Обработка случаев
        if float(msg_ar[2]) > (custom_portfolio[message.from_user.id][msg_ar[1].lower()] * crypto_price):
            await message.answer('Недостаточно валюты')
        else:
            if msg_ar[1].lower() not in custom_portfolio[message.from_user.id]:
                await message.answer('Вы еще не покупали эту монету')
            else:
                custom_portfolio[message.from_user.id][msg_ar[1].lower()] -= float(msg_ar[2]) / crypto_price
                custom_portfolio[message.from_user.id]['USD'] += float(msg_ar[2])
                await message.answer('Монета успешно продана')
    else:
        await message.answer('Валюта не найдена')


# Начало работы с портфелем
@dp.message_handler(commands=['start_game'])
async def start_portfolio(message: types.Message):
    msg_ar = process_message(message.text)
    if len(msg_ar) == 1:
        await message.answer('Введите команду в следующем формате: /{start_game 1000},'
                             ' где 1000 - желаемое начальное вложение в USD')
    else:
        custom_portfolio[message.from_user.id] = defaultdict(float)
        custom_portfolio[message.from_user.id]['USD'] = float(msg_ar[1])
        await message.answer('Портфель успешно создан. Чтобы просмотреть свой портфель, пропишите /{my_portfolio}')


# Проверка цены валюты
@dp.message_handler(commands=['check'])
async def check_value(message: types.Message):
    msg_ar = process_message(message.text)
    global crypto_current
    crypto_current = initialize(crypto_current, True)
    if msg_ar[1].lower() in crypto_current[0]:
        await message.answer('Цена ' + msg_ar[1] + ' = ' +
                             crypto_current[1][crypto_current[0].index(msg_ar[1].lower())][1:] + '$')
    else:
        await message.answer('Данная монета не найдена на coingecko')


# Работа с неопределенными ранее сообщениями
@dp.message_handler()
async def other_messages(message: types.Message):
    await message.answer('Пожалуйста, проверьте правильность написания команды')


# Сообщение по подписке
async def scheduled(wait_for):
    while True:
        await asyncio.sleep(wait_for)
        subscriptions = db.get_subscriptions()
        global prev_prices, crypto_current
        crypto_current = initialize(crypto_current, False)
        for s in subscriptions:
            message = ''
            coins = [crypto_current[0].index('Bitcoin'), crypto_current[0].index('Tether'),
                     crypto_current[0].index('Ethereum'), crypto_current[0].index('Cardano'),
                     crypto_current[0].index('XRP')]
            for coin in coins:
                message = print_coin(crypto_current, message, s, coin)
            if message:
                await bot.send_message(s[1], message, disable_notification=True)

        prev_prices = crypto_current


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(scheduled(10))  # пока что оставим 120 секунд (в качестве теста)
    executor.start_polling(dp, skip_updates=True)
