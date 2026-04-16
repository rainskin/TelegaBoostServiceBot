welcome = {
    'ru': "<b>Добро пожаловать!</b>\n\n"
          "🚀 Здесь вы сможете заказать услуги "
          "по продвижению вашего телеграм канала или бота, а также приобрести <b>⭐️ Telegram звезды</b> по очень выгодной цене!\n\n"
          "Всегда рады ответить на ваши вопросы!\n"
          "Контакт поддержки (с 10 до 20 по GMT/UTC+3):\n"
          "💬 {support_contact}",
    'en': "<b>Welcome!</b>\n\n"
          "🚀 Here you can order promotion services "
          "for your Telegram channel or bot, as well as purchase <b>⭐️ Telegram Stars</b> at a very attractive price!\n\n"
          "We are always happy to answer your questions!\n"
          "Support contact (10:00–20:00 GMT/UTC+3):\n"
          "💬 {support_contact}",
}

support_contact = {'ru': "💬 <b>Контакт службы поддержки:</b> {support_contact}",
                   'en': "💬 <b>Support contact bot:</b> {support_contact}"}

balance_recharge_limits = {
    'ru': "<b>ДОСТУПНЫЕ СПОСОБЫ ОПЛАТЫ</b>\n\n"
          "<b>1. ⭐ Телеграм звёзды</b>\n"
          "<b>2. 💳 Банковская карта</b>\n"
          "<i>    Только Ру карты</i>\n"
          "<i>    СБП недоступен (в работе)</i>\n\n",

    'en': "<b>AVAILABLE PAYMENT METHODS</b>\n\n"
          "<b>1. ⭐ Telegram Stars</b>\n"
          "<b>2. 💳 Bank card</b>\n"
          "<i>    Only Ru cards</i>\n"
          "<i>    SBP is not available (in progress)</i>\n\n"
}

balance_recharge_commission_info = {
    'ru': "<b>Комиссия на пополнение:</b> {topup_commission}%\n"
          "_____\n"
          "<b>От 500 руб</b> можно пополнить баланс <b>без комиссии</b> через поддержку: {support_contact}",

    'en': "<b>Top-up commission:</b> {topup_commission}%\n"
          "_____\n"
          "<b>From 500 RUB</b> you can top up your balance <b>without commission</b> via support: {support_contact}",
}
balance_recharge_input_amount = {'ru': "Минимальная сумма для пополнения - "
                                       "<b>{minimal_recharge_amount} {currency}</b>\n\n"
                                       "Укажите желаемую сумму пополнения",
                                 'en': "Minimum amount for top-up - "
                                       "<b>{minimal_recharge_amount} {currency}</b>\n\n"
                                       "Enter the desired top-up amount"}

balance_recharge_wrong_amount = {'ru': "Введите число в формате:\n"
                                       "<b>100</b> или <b>100.50</b>",
                                 'en': "Enter a number in the format:\n"
                                       "<b>350</b> or <b>490.50</b>"}

balance_recharge_amount_too_small = {'ru': "Сумма пополнения должна быть не менее "
                                           "<b>{minimal_recharge_amount} {currency}</b>\n\n"
                                           "Укажите новую сумму пополнения",
                                     'en': "The top-up amount must be at least "
                                           "<b>{minimal_recharge_amount} {currency}</b>\n\n"
                                           "Please specify a new top-up amount"}
balance_recharge_accept_amount = {'ru': "Пополнить баланс на <b>{amount} {currency}?</b>",
                                  'en': "Top up your balance with <b>{amount} {currency}?</b>"}

balance_recharge_accept_amount_with_commission = {
    'ru': "Будет зачислено <b>{amount} {currency}</b>\n\n"
          "Пополнить баланс?\n\n"
          "<i>Если хотите изменить сумму пополнения,"
          "отправьте ее следующим сообщением</i>",

    'en': "<b>{amount} {currency}</b> will be credited\n\n"
          "Top up the balance?\n\n"
          "<i>If you want to change the top-up amount,"
          "send it in the next message</i>",
}

balance_recharge_already_paid = {'ru': "<b>Ошибка.</b>\n\n"
                                       "Этот счет уже был оплачен. Проверьте баланс",
                                 'en': "<b>Error.</b>\n\n"
                                       "This invoice has already been paid. Please check your balance"}

balance_recharge_successfully_paid = {
    'ru': "Баланс успешно пополнен на <b>{amount} {currency}</b>",
    'en': "The balance has been successfully replenished with <b>{amount} {currency}</b>"}

manual_balance_deposit_received = {
    'ru': '➕Вам начислен баланс: <b>{amount} руб</b>',
    'en': '➕Your balance has been credited: <b>{amount} RUB</b>',
}

balance_recharge_invoice_title = {
    'ru': "Пополнение баланса",
    'en': "Top up balance"}

balance_recharge_invoice_description = {
    'ru': "Для пополнения баланса на {amount} {currency} нажмите на кнопку ниже",
    'en': "To top up your balance with {amount} {currency}, click the button below"}

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

your_balance = {'ru': "💰 <b>Ваш баланс:</b> {amount:.2f} {currency}",
                'en': '💰 <b>Current balance:</b> {amount:.2f} {currency}'}

not_enough_money = {'ru': "Недостаточно средств на балансе\n"
                          "Доступно {current_balance:.2f} {currency}",
                    'en': "Insufficient funds on balance\n"
                          "Available {current_balance:.2f} {currency}"}
order_is_paid = {'ru': "💰 <b>Заказ {internal_order_id} </b> успешно оплачен\n\n",
                 'en': "💰 <b>Order {internal_order_id} </b> has been successfully paid\n\n"}

order_is_created = {'ru': "✅ <b>Заказ {order_id} оформлен</b>\n\n",
                    'en': "✅ <b>Order {order_id} has been placed</b>\n\n"}

order_was_canceled = {
    'ru': 'Заказ <b>{internal_order_id}</b> был отменен. Возвращено на баланс: {amount:.2f} {currency}',
    'en': 'Order <b>{internal_order_id}</b> has been canceled. Returned to balance: {amount:.2f} {currency}'}

# orders_is_created = {'ru': "✅ <b>Заказы {order_ids} оформлены</b>\n\n",
#                      'en': "✅ <b>Orders {order_ids} has been placed</b>\n\n"}

take_order_into_work = {'ru': "✅ <b>Заказ {internal_order_id}</b> передан в работу\n\n",
                        'en': "✅ <b>Order {internal_order_id}</b> sent to work\n\n"}

take_orders_into_work = {'ru': "✅ <b>Заказы {order_ids} переданы в работу</b>\n\n",
                         'en': "✅ <b>Orders {order_ids} sent to work</b>\n\n"}

spent_amount_from_balance = {'ru': "<b>Списано:</b> {total_amount:.2f} {currency}\n"
                                   "<b>Остаток</b>: {current_balance:.2f} {currency}",

                             'en': "<b>Spent:</b> {total_amount:.2f} {currency}\n"
                                   "<b>Current balance</b>: {current_balance:.2f} {currency}"}

# tg stars

tg_stars_enter_quantity = {
    'ru': 'Введи количество звезд: от <b>50</b> до <b>1000000</b> (1 млн)',
    'en': 'Enter the number of stars: from <b>50</b> to <b>1000000</b> (1M)',
}

tg_stars_enter_username = {
    'ru': 'Вы выбрали ⭐️<b>{quantity} звезд.</b>\n\n'
          'Теперь укажите @username',
    'en': 'You selected ⭐️<b>{quantity} stars.</b>\n\n'
          'Now enter the @username',
}

tg_stars_wrong_amount = {
    'ru': 'Укажите целое число от 50 до 1000000 (1 млн) без пробелов и других символов.',
    'en': 'Please enter the whole number from 50 to 1000000 (1M) without spaces and other symbols'
}

tg_stars_not_correct_amount = {
    'ru': 'Допустимо только целое число от 50 до 1000000 (1 млн).',
    'en': 'Only an integer from 50 to 1000000 (1M) is allowed.',
}

tg_stars_invalid_username = {
    'ru': '<b>Некорректное имя пользователя.</b>\n'
          'Пожалуйста, введите действительное имя пользователя:\n\n'
          '<i>5-32 символов. Допускаются только латинские буквы, цифры и символ подчеркивания</i>',
    'en': '<b>Invalid username.</b>\n'
          'Please enter a valid username:\n\n'
          '<i>5-32 characters. Only Latin letters, digits, and underscores are allowed</i>',
}

tg_stars_confirmation_text = {
    'ru': '⭐️ <b>{quantity} звезд</b> для @{username}\n'
          '💵 <b>Итоговая цена:</b> {total_price:.2f} {currency}\n\n'
          'Нажмите <b>Да</b>, чтобы подтвердить или <b>Нет</b>, чтобы отменить',
    'en': '⭐️ <b>{quantity} stars</b> for @{username}\n'
          '💵 <b>Total price:</b> {total_price:.2f} {currency}\n\n'
          'Press <b>Yes</b> to confirm or <b>No</b> to cancel',
}
tg_stars_order_completed = {
    'ru': '✅ Заказ <b>{internal_order_id}</b> успешно выполнен!\n\n'
          '⭐️ <b>{amount}</b>  > > >  @{username}',
    'en': '✅ Order <b>{internal_order_id}</b> has been successfully completed!\n\n'
          '⭐️ <b>{amount}</b>  > > >  @{username}',
}

tg_stars_order_invalid_username = {
    'ru': '❌ Заказ <b>{internal_order_id}</b> отменен.\n'
          '<i>Неверно указан юзернейм для получения звезд.</i>\n\n'
          'Средства <b>вернулись на баланс</b>',
    'en': '❌ Order <b>{internal_order_id}</b> has been canceled.\n'
          '<i>The username for receiving stars was entered incorrectly.</i>\n\n'
          'The funds have <b>been returned to the balance</b>',
}

not_accepted_order = {
    'ru': '<b>Заказы, ожидающие подтверждения:</b>',
    'en': '<b>Orders awaiting confirmation:</b>',
}

not_accepted_order_status = {
    'ru': '<b>Заказ {order_id}</b>\n\n'
          '<b>Ссылка:</b> {url}\n'
          '<b>Количество:</b> {quantity}\n'
          '<b>Сумма:</b> {total_amount}',

    'en': '<b>Order {order_id}</b>\n\n'
          '<b>Link:</b> {url}\n'
          '<b>Quantity:</b> {quantity}\n'
          '<b>Amount:</b> {total_amount}',
}

action_is_not_available = {
    'ru': 'Это действие не возможно выполнить сейчас',
    'en': 'This action cannot be performed at this time'
}

canceling_not_accepted_order_is_not_available = {
    'ru': 'Невозможно выполнить. Заказ уже отменён или началось выполнение',
    'en': 'Unable to complete. The order has already been canceled or fulfillment has begun'
}
cancel_action = {
    'ru': 'Действие отменено',
    'en': 'Action cancelled',
}

action_cannot_be_performed = {
    'ru': 'Данное действие не может быть выполнено',
    'en': 'This action cannot be performed',
}

cancel_order = {
    'ru': 'Вы действительно хотите отменить заказ <b>{order_id}</b> ?',
    'en': 'Are you sure you want to cancel order <b>{order_id}</b> ?',
}

order_successfully_canceled = {
    'ru': 'Заказ отменён, средства вернулись на баланс',
    'en': 'The order was cancelled, the funds were returned to the balance',
}

# unpaid orders

unpaid_order_was_deleted = {
    'ru': '🗑 Ваш неоплаченный заказ <b>{internal_order_id}</b> был удалён.',
    'en': '🗑 Your unpaid <b>{internal_order_id}</b> order was deleted '
}

unpaid_order_failed_to_do = {
    'ru': 'Не удалось выполнить действие для заказа <b>{internal_order_id}</b>\n\n'
          '<b>Текущий статус:</b> {status}',
    'en': 'Failed to perform the action for order <b>{internal_order_id}</b>\n\n'
          '<b>Current status:</b> {status}',
}

unpaid_order_was_deleted_early = {
    'ru': 'Этот заказ уже был удален',
    'en': "This order was deleted early"
}

active_orders = {'ru': 'Заказы в работе',
                 'en': 'Orders in progres'}

no_active_orders = {'ru': "Нет заказов в работе",
                    'en': "No orders in progress"}

receiving_information_about_current_orders = {
    'ru': 'Получаю информацию  заказах в работе...',
    'en': 'Processing information about about orders in progress...'
}

receiving_information_about_archive_orders = {
    'ru': 'Обрабатываю информацию о прошлых заказах...',
    'en': 'Processing information about past orders...'
}

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

maintenance_mode = {
    'ru': '⚠️ Сейчас это действие выполнить невозможно - система находится на техническом обслуживании.\n'
          'Примерное время работ: 10 минут.\n\n',
    'en': '⚠️ This action cannot be performed at the moment – the system is under maintenance.\n'
          'Estimated downtime: 10 minutes.\n\n',
}


def get_plan_info_text(lang: str, name, description: str, service_info: dict, hot_offer=False):
    currency = 'RUB'

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

    return msg


ask_quantity = {'ru': 'Укажите желаемое количество от <b>{min_value}</b> до <b>{max_value}</b>',
                'en': 'Indicate the desired quantity from <b>{min_value}</b> to <b>{max_value}</b> '}

value_is_not_number = {'ru': 'Вы должны указать число от <b>{min_value}</b> до <b>{max_value}</b>',
                       'en': 'You must indicate the number from <b>{min_value}</b> to <b>{max_value}</b> '}

wrong_quantity = {
    'ru': 'Неверное значение. Укажите количество в промежутке от <b>{min_value}</b> до <b>{max_value}</b>',
    'en': 'Incorrect value. Enter the quantity between <b>{min_value}</b> and <b>{max_value}</b> '}

valid_quantity = {
    'ru': '💴 <b> Стоимость составит:</b> {total_cost:.2f} {currency}\n'
          'Если готовы продолжить, нажмите на кнопку ниже\n\n'
          '<i>Или введите новое количество для повторного расчёта стоимости</i>',
    'en': '💴 <b>Total cost will be:</b> {total_cost:.2f} {currency}\n'
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
          '<b>💴 Сумма: </b> {total_amount:.2f} {currency}\n\n'
          '<i>Если хотите изменить ссылку, отправьте новую ссылку в следующем сообщении</i>\n\n'
          '➕ Для <b>оформления заказа</b> нажмите на соответствующую кнопку ниже',

    'en': '✔️<b>URL accepted.</b>\n\n'
          'Please check the order details\n\n'
          '<b>🔗 URL:</b> {url}\n'
          '<b>🧮 Quantity: </b> {quantity}\n'
          '<b>💴 Total: </b> {total_amount:.2f} {currency}\n\n'
          '<i>If you want to change the URL, send the new URL in the next message</i>\n\n'
          '➕ To <b>place the order</b>, click the corresponding button below'
}

confirm_order_payment = {
    'ru': '<b>Сумма заказа:</b> {total_amount:.2f} {currency}\n\n'
          '<b>💵 Ваш текущий баланс {current_balance:.2f} {currency}</b>',
    'en': '<b>Order price:</b> {total_amount:.2f} {currency}\n\n'
          '<b>💵 Your current balance {current_balance:.2f} {currency}</b>'}

available_payment_methods = {
    'ru': 'Выберите способ оплаты',
    'en': 'Select a payment method'
}

payment_by_card = {
    'ru': '<i>ID транзакции: {transaction_id}</i>\n\n'
          'Для пополнения баланса на <b>{amount} {currency}</b> оплатите выставленный счет, '
          'нажав на кнопку <b>💳ОПЛАТИТЬ</b>\n\n'
          'После оплаты нажмите кнопку\n<b>⏳ ПРОВЕРИТЬ ОПЛАТУ</b>',
    'en': '<i>Transaction ID: {transaction_id}</i>\n\n'
          'To top up your balance with <b>{amount} {currency}</b>, '
          'pay the issued invoice by clicking the <b>💳PAY</b> button\n\n'
          'After payment, click the\n<b>⏳ CHECK PAYMENT</b> button'
}
current_payment_status = {
    'ru': '<b>Текущий статус платежа</b>',
    'en': '<b>Current payment status</b>',
}

cannot_check_payment_status = {
    'ru': '<b>Не удалось проверить статус платежа.</b>\n'
          'Если оплата была совершена, обратитесь в поддержку - /support',
    'en': '<b>Failed to check payment status.</b>\n'
          'If the payment was made, contact support - /support',
}

some_error_try_again = {
    'ru': '<b>❗️ Возникла какая-то ошибка.</b>\n'
          'Попробуйте, пожалуйста, заново.\n'
          'Если проблема сохраняется, обратитесь в поддержку',
    'en': '<b>❗️ Some error occurred.</b>\n'
          'Please try again.\n'
          'If the problem persists, contact support',
}

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

about_referral_system = {
    'ru': 'Приглашай пользователей по своей ссылке и<b> зарабатывай {reward_percent}%</b> от каждого пополнения баланса.\n\n'
          '<b>Твоя реф. ссылка:</b> {link}',
    'en': 'Invite users using your link<b> and earn {reward_percent}%</b> from each balance replenishment.\n\n'
          '<b>Your ref. link:</b> {link}'}

referral_statistics = {
    'ru': '📊 [ТВОЯ СТАТИСТИКА]\n\n'
          '<b>Приглашено пользователей:</b> {referral_amount} \n'
          '<b>Заработано</b> {total_earned} {currency}',
    'en': '📊 [YOUR STATS]\n\n'
          '<b>Invited users </b> {referral_amount} \n'
          '<b>Earned:</b> {total_earned} {currency}'}


def translate_order_status_key(key: str, lang: str) -> str:
    return translate_status_key[key][lang]


def translate_current_order_status(status: str, lang: str) -> str:
    return current_order_status[status][lang]
