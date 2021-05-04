import config
import asyncio
import re

from aiogram import Bot, Dispatcher, executor, types
from sqlighter import SQLighter

from crypto import Crypto
# инициализируем бота
bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot)

db = SQLighter('new_db.db')
first_cr = Crypto()
custom_portfolio = {}

prev_prices = first_cr.get_list()
crypto_current = first_cr.get_list()
for i in range(len(crypto_current[0])):
    crypto_current[0][i] = crypto_current[0][i].lower()


def emoji_mes(result, message, index):
    if result[1][index] > prev_prices[1][index]:
        message += '📈' + '\n'
    elif result[1][index] < prev_prices[1][index]:
        message += '📉' + '\n'
    else:
        message += '🚦' + '\n'
    return message


def print_coin(result, message, s, index):
    if db.is_subscribed(s[1], result[0][index].lower()):
        message += result[0][index] + ' - ' + result[1][index][1:] + '$'
        message = emoji_mes(result, message, index)
    return message


@dp.message_handler(commands=['start'])
async def subscribe(message: types.Message):
    custom_portfolio[message.from_user.id] = {}
    await message.answer('Добро пожаловать в клуб верующих в код! Для того, чтобы подписаться на ежечасную ' +
                         'сводку по криптовалюте напишите "/{cryptocurrency_name}", например "/bitcoin". ' +
                         'Для того, чтобы отписаться от сводки по данной валюте, повторите описанную команду. ' +
                         'Командами /set и /my_portfolio можно работать со своим криптопортфелем. ' +
                         'Применение функции /set симулирует покупку криптовалюты в указанном размере USD. ' +
                         'На основе симуляции можно узнать, как изменился бы ваш портфель, если бы вы купили валюты ' +
                         'в момент написания /set. Пока не реализована функция обновления уже установленной валюты, ' +
                         'поэтому для одной валюты /set можно писать один раз (работают валюты из топ 100 coingecko).')


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


@dp.message_handler(commands=['my_portfolio'])
async def print_portfolio(message: types.Message):
    ans_message = ''
    sum = 0
    new_cr = Crypto()
    crypto_current1 = new_cr.get_list()
    for i in range(len(crypto_current1[0])):
        crypto_current1[0][i] = crypto_current1[0][i].lower()
    for i in custom_portfolio[message.from_user.id].keys():
        index = crypto_current1[0].index(i)
        ans_message += i
        ans_message += ': ' + str(int(custom_portfolio[message.from_user.id][i] * float(crypto_current1[1][index][1:].replace(',', '')) * 100) / 100) + '$\n'
        sum += int(custom_portfolio[message.from_user.id][i] * float(crypto_current1[1][index][1:].replace(',', '')) * 1000) / 1000
    sum = int(sum * 1000) / 1000
    await message.answer(ans_message + 'Common: ' + str(sum) + '$')


@dp.message_handler(commands=['set'])
async def set_portfolio(message: types.Message):
    msg = re.findall(r'.+', message.text)
    msg[0].replace(',', '.')
    msg_ar = msg[0].replace(',', '.').split()
    if msg_ar[1].lower() in crypto_current[0]:
        index = crypto_current[0].index(msg_ar[1].lower())
        crypto_price = float(crypto_current[1][index][1:].replace(',', ''))
        custom_portfolio[message.from_user.id][msg_ar[1].lower()] = float(msg_ar[2]) / crypto_price
        print(custom_portfolio)
        await message.answer('Значение успешно установлено')
    else:
        await message.answer('Валюта не найдена')


async def scheduled(wait_for):
    while True:
        await asyncio.sleep(wait_for)
        cr = Crypto()
        subscriptions = db.get_subscriptions()
        global prev_prices
        result = cr.get_list()
        for s in subscriptions:
            message = ''
            iter = [0, 5, 1, 6, 4]
            for i in iter:
                message = print_coin(result, message, s, i)
            print(message)
            if message != '':
                await bot.send_message(s[1], message, disable_notification=True)

        prev_prices = result


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(scheduled(120))  # пока что оставим 120 секунд (в качестве теста)
    executor.start_polling(dp, skip_updates=True)
