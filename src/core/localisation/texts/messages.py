welcome = {'ru': "<b>Добро пожаловать!</b>\n\n"
                 "⭐️ Здесь вы сможете заказать услуги "
                 "по продвижению вашего телеграм канала или бота\n"
                 "💯 Личная база аккаунтов позволяет обеспечивать <b>отличную цену</b> и оперативное выполнение\n\n"
                 "Всегда рады ответить на ваши вопросы!\n"
                 "Наш бот поддержки (с 10 до 20 по МСК):\n"
                 "💬 {support_contact}",
           'en': "<b>Welcome!</b>\n\n"
                 "⭐️ Here you can order services"
                 "to promote your telegram channel or bot\n"
                 "💯 Personal account database allows us to provide the <b>good price</b> and prompt execution\n\n"
                 "We are always happy to answer your questions!\n"
                 "Our support bot (from 10 to 20 Moscow time):\n"
                 "💬 {support_contact}"}

promo_activated = {'ru': "<b>Бонус активирован.</b>\n"
                         "Средства успешно начислены на ваш баланс",
                   'en': '<b>Bonus has been activated.</b>\n'
                         'Funds have been successfully added to your balance'}

lang_is_changed = {'ru': "Язык успешно изменен",
                   'en': "Language changed successfully"}

change_lang = {'ru': "Выберите ваш язык",
               'en': "Select your language"}

plans = {'ru': "Выбери, что тебя интересует:",
         'en': 'Choose what interests you:'}

main_menu = {'ru': "🏠 <b>Главное меню:</b>",
             'en': '🏠 <b>Main menu:</b>'}

your_balance = {'ru': "💰 <b>Ваш баланс:</b> {amount} {currency}",
                'en': '💰 <b>Current balance:</b> {amount} {currency}'}

not_enough_money = {'ru': "Недостаточно средств на балансе\n"
                          "Доступно {current_balance} {currency}",
                    'en': "Insufficient funds on balance\n"
                          "Available {current_balance} {currency}"}
order_is_created = {'ru': "✅ <b>Заказ {order_id} оформлен</b>\n\n"
                          "<b>Списано:</b> {total_amount} {currency}\n"
                          "<b>Остаток</b>: {current_balance} {currency}",

                    'en': "✅ <b>Order {order_id} has been placed</b>\n\n"
                          "<b>Spent:</b> {total_amount} {currency}\n"
                          "<b>Current balance</b>: {current_balance} {currency}"}

orders_is_created = {'ru': "✅ <b>Заказы {order_ids} оформлены</b>\n\n"
                           "<b>Списано:</b> {total_amount} {currency}\n"
                           "<b>Остаток</b>: {current_balance} {currency}",

                     'en': "✅ <b>Orders {order_ids} has been placed</b>\n\n"
                           "<b>Spent:</b> {total_amount} {currency}\n"
                           "<b>Current balance</b>: {current_balance} {currency}"}

active_orders = {'ru': 'Ваши текущие заказы',
                 'en': 'Your current orders'}

no_active_orders = {'ru': "Нет активных заказов",
                    'en': "No active orders"}

history_of_orders = {'ru': "История заказов",
                     'en': "History of orders"}

no_history_of_orders = {'ru': "<b>История заказов пуста.</b>\n\n"
                              "Если уже сделали заказ, проверьте активные заказы",
                        'en': "<b>Order history is empty.</b>\n\n"
                              "If you have already placed an order, check your active orders"}

get_plans = {'ru': "Доступные тарифы:",
             'en': "Available rates:"}

plan_info = {
    'price_rate': {
        'ru': 'Цена за 1000 выполнений',
        'en': 'Price per 1000 executions'},

    'min_count':
        {'ru': 'Минимальное количество',
         'en': 'Min count'},

    'max_count': {
        'ru': 'Максимальное количество',
        'en': 'Max count'},

    'canceling_is_available': {
        'ru': 'Отмена: есть ✅',
        'en': 'Cancel is available ✅'},

    'canceling_is_not_available': {
        'ru': 'Отмена: нет',
        'en': 'Cancel is not available'
    }
}

hot_offer_msg = {
    'price': {
        'ru': 'Стоимость',
        'en': 'Price',
    },
}


def get_plan_info_text(lang: str, name, description: str, service_info: dict, hot_offer=False):
    currency = 'RUB'
    if not hot_offer:
        rate = service_info['rate']
        min_count = service_info['min_count']
        max_count = service_info['max_count']
        canceling_is_available = service_info['canceling_is_available']
        canceling_is_available = plan_info['canceling_is_available'][lang] if canceling_is_available else \
            plan_info['canceling_is_not_available'][lang]

        if description.startswith('\n'):
            description = description[1:]

        name += '\n\n' if description else '\n'
        description += '\n\n' if description else '\n'

        msg = (f'<b>{name}</b>'
               f'{description}'
               f'<b>{plan_info["price_rate"][lang]}:</b> {rate} {currency}\n\n'
               f'<b>{plan_info["min_count"][lang]}:</b> {min_count}\n'
               f'<b>{plan_info["max_count"][lang]}:</b> {max_count}\n\n'
               f'{canceling_is_available}')

    else:
        price: float = service_info['price']
        msg = (f'<b>{name}</b>\n\n'
               f'{description}\n\n'
               f'<b>{hot_offer_msg["price"][lang]}:</b> {round(price)} {currency}')
    return msg


ask_quantity = {'ru': 'Укажите желаемое количество от <b>{min_value}</b> до <b>{max_value}</b>',
                'en': 'Indicate the desired quantity from <b>{min_value}</b> to <b>{max_value}</b> '}

value_is_not_number = {'ru': 'Вы должны указать число от <b>{min_value}</b> до <b>{max_value}</b>',
                       'en': 'You must indicate the number from <b>{min_value}</b> to <b>{max_value}</b> '}

wrong_quantity = {
    'ru': 'Неверное значение. Укажите количество в промежутке от <b>{min_value}</b> до <b>{max_value}</b>',
    'en': 'Incorrect value. Enter the quantity between <b>{min_value}</b> and <b>{max_value}</b> '}

valid_quantity = {
    'ru': '💴 <b> Стоимость составит:</b> {total_cost} {currency}\n'
          'Если готовы продолжить, нажмите на кнопку ниже\n\n'
          '<i>Или введите новое количество для повторного расчёта стоимости</i>',
    'en': '💴 <b>Total cost will be:</b> {total_cost} {currency}\n'
          "If you're ready to continue, click the button below\n\n"
          '<i>Or enter a new quantity to recalculate the cost</i>'}

ask_url = {
    'ru': 'Укажите ссылку\n\n',
    'en': 'Input the URL'}

incorrect_url = {
    'ru': 'Укажите корректную ссылку. Пример:\n\n'
          '<b>https://site.com</b>\n',
    'en': 'Input correct URL. Example:\n\n'
          '<b>https://site.com</b>\n'}

correct_url = {
    'ru': '✔️<b>Ссылка принята.</b>\n\n'
          'Проверьте, пожалуйста, данные заказа\n\n'
          '<b>🔗 Ссылка:</b> {url}\n'
          '<b>🧮 Количество: </b> {quantity}\n'
          '<b>💴 Сумма: </b> {total_amount} {currency}\n\n'
          '<i>Если хотите изменить ссылку, отправьте новую ссылку в следующем сообщении</i>\n\n'
          '➕ Для <b>оформления заказа</b> нажмите на соответствующую кнопку ниже',

    'en': '✔️<b>URL accepted.</b>\n\n'
          'Please check the order details\n\n'
          '<b>🔗 URL:</b> {url}\n'
          '<b>🧮 Quantity: </b> {quantity}\n'
          '<b>💴 Total: </b> {total_amount} {currency}\n\n'
          '<i>If you want to change the URL, send the new URL in the next message</i>\n\n'
          '➕ To <b>place the order</b>, click the corresponding button below'
}
correct_url_hot_order = {
    'ru': '✔️<b>Ссылка принята.</b>\n\n'
          '<i>Если хотите изменить ссылку, отправьте новую ссылку в следующем сообщении</i>\n\n'
          '➕ Для <b>оформления заказа</b> нажмите на соответствующую кнопку ниже',
    'en': '✔️<b>URL accepted.</b>\n\n'
          '<i>If you want to change the URL, send the new URL in the next message</i>\n\n'
          '➕ To <b>place the order</b>, click the corresponding button below',
}

select_payment_method = {
    'ru': '<b>Сумма заказа:</b> {total_amount} {currency}\n\n'
          '<b>💳 Выберите способ оплаты</b>',
    'en': '<b>Order price:</b> {total_amount} {currency}\n\n'
          '<b>💳 Select a Payment Method</b>'}

translate_status_key = {
    'charge': {
        'ru': 'Сумма',
        'en': 'Spent',
    },
    'start_count': {
        'ru': 'Стартовое значение',
        'en': 'Start count',
    },
    'status': {
        'ru': 'Статус',
        'en': 'Status',
    },
    'remains': {
        'ru': 'Остаток',
        'en': 'Remains',
    },
    'currency': {
        'ru': 'Валюта',
        'en': 'Currency',
    },
    'date': {
        'ru': 'Дата создания',
        'en': 'Date',
    },
    'service_id': {
        'ru': 'ID услуги',
        'en': 'Service ID',
    },
    'quantity': {
        'ru': 'Количество',
        'en': 'Quantity',
    },
    'url': {
        'ru': 'Ссылка',
        'en': 'URL',
    },

}

current_order_status = {
    'In progress': {
        'ru': '🔹 Выполняется',
        'en': '🔹 In progress',
    },
    'Completed': {
        'ru': '✅ Завершён',
        'en': '✅ Completed',
    },
    'Awaiting': {
        'ru': '⌛️ Ожидание',
        'en': '⌛️ Awaiting',
    },
    'Canceled': {
        'ru': '❌ Отменён',
        'en': '❌ Canceled',
    },
    'Fail': {
        'ru': '🚫 Ошибка',
        'en': '🚫 Fail',
    },
    'Partial': {
        'ru': '🟡 Частично',
        'en': '🟡 Partial',
    },
}


def translate_order_status_key(key: str, lang: str) -> str:
    return translate_status_key[key][lang]


def translate_current_order_status(status: str, lang: str) -> str:
    return current_order_status[status][lang]
