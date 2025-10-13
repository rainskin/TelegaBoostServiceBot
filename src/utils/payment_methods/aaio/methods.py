import asyncio
import hashlib
import sys
from asyncio import sleep
from urllib.parse import urlencode

import requests
from requests import ReadTimeout, ConnectTimeout

from loader import bot
from utils.payment_methods.aaio.config import MERCHANT_ID, SECRET_KEY1, API_KEY


async def check_payment_status(user_id: int, order_id: str) -> str:
    base_url = 'https://aaio.so/api/info-pay'
    params = {
        'merchant_id': MERCHANT_ID,
        'order_id': order_id
    }
    headers = {
        'Accept': 'application/json',
        'X-Api-Key': API_KEY
    }

    try:
        response = requests.post(base_url, data=params, headers=headers)
    except ConnectTimeout:
        # print('ConnectTimeout')  # Не хватило времени на подключение к сайту
        sys.exit()
    except ReadTimeout:
        # print('ReadTimeout')  # Не хватило времени на выполнение запроса
        sys.exit()

    if response.status_code in [200, 400, 401]:
        try:
            response_json = response.json()  # Парсинг результата

        except:
            print('Не удалось пропарсить ответ')
            sys.exit()

        if response_json['type'] == 'success':

            return response_json['status']  # Вывод результата
        else:
            error = response_json['message']
            if error == 'Заказ не найден':
                text = (f'<b>{error}</b>\n\n'
                        f'Перейдите по ссылке выше, чтобы оплатить заказ и завершить его оформление')
            else:
                text = (f"Ошибка: <b>{error}</b>\n\n"
                        f"Попробуйте повторить действие через некоторое время. Либо обратитесь в поддержку\n\n"
                        f"ID транзакции: {order_id}")
            await bot.send_message(user_id, text)

    else:
        print('Response code: ' + str(response.status_code))  # Вывод неизвестного кода ответа


#
# async def check_periodically(sec: float, order_id: str):
#     while True:
#         status = await check_payment_status(order_id)
#         print(status)
#         await sleep(sec)
#         if status == 'in_process':
#             print('Завершаю работу')
#             break


async def get_payment_url(order_id: str, amount: float, lang: str, currency: str = 'RUB'):
    base_payment_url = 'https://aaio.so/merchant/pay?'
    desc = 'Order Payment'  # Описание заказа
    lang = lang if (lang == 'ru' or lang == 'en') else 'en'  # Язык формы

    sign = f':'.join([
        str(MERCHANT_ID),
        str(amount),
        str(currency),
        str(SECRET_KEY1),
        str(order_id)
    ])

    params = {
        'merchant_id': MERCHANT_ID,
        'amount': amount,
        'currency': currency,
        'order_id': order_id,
        'sign': hashlib.sha256(sign.encode('utf-8')).hexdigest(),
        'desc': desc,
        'lang': lang
    }

    r = (base_payment_url + urlencode(params))
    return r
