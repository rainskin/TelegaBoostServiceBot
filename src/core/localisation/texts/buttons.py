import config

categories = {
    'callbacks': ['views', 'subscribers', 'premium_subscribers', 'boosts', 'boosts_18', 'reactions', 'bot_launches',
                  'vk', 'twitch',
                  'referrals'],
    'ru': ['👁 Просмотры', '👥 Подписчики', '⭐️ Премиум подписчики', '⚡️ Бусты', '⚡️ Бусты для 18+ каналов',
           '👍🏻❤️‍🔥 Реакции', '🤖 Запуски бота',
           'Вконтакте', 'Твич', '🎮 Рефералы в бота'],
    'en': ['👁 Views', '👥 Subscribers', '⭐️ Premium Subscribers', '⚡️ Boosts', '⚡️ Boosts for 18+ channels',
           '👍🏻❤️‍🔥 Reactions',
           '🤖 Bot launches "/start"', 'Vk', 'Twitch', '🎮 Bot referrals'],
}
buy_stars_button = {
    'callback': 'buy_stars',
    'ru': '⭐️ Купить Звезды',
    'en': '⭐️ Buy Stars'
}
hot_offers = {'callback': 'hot_offers',
              'ru': '🔥 Горячее предложение',
              'en': '🔥 Hot offers'}

balance_recharge = {'callback': 'balance_recharge',
                    'ru': '💵 Пополнить баланс',
                    'en': '💵 Balance recharge'}

current_orders = {'callback': 'current_orders',
                  'ru': '♻️ Активные заказы',
                  'en': '♻️ Current orders'}

orders_history = {'callback': 'archive_orders',
                  'ru': '📋 История заказов',
                  'en': '📋 History of orders'}

support = {'url': config.SUPPORT_BOT_URL,
           'ru': '💬 Поддержка',
           'en': '💬 Support'}

referrals = {'callback': 'referrals',
             'ru': '👥 Рефералы',
             'en': '👥 Referrals'}

new_order = {'callback': 'new_order',
             'ru': '➕ Новый заказ',
             'en': '➕ New order'}

cancel_order = {
    'ru': 'Отменить',
    'en': 'Cancel'
}

admin_cancel_broken_order = {
    'ru': 'Отменить заказ и вернуть средства',
    'en': 'Cancel order and refund',
}

change_language = {'callbacks': ['change_language'],
                   'ru': ['🇷🇺 Поменять язык'],
                   'en': ['🇬🇧 Change language']}

navigation_menu = {'callbacks': ['back_to_menu', 'back'],
                   'ru': ['🏠 Вернуться в меню', '⬅️ Назад'],
                   'en': ['🏠 Back to menu', '⬅️ Back']}

to_continue = {'callback': 'to_continue',
               'ru': 'Продолжить ➡️',
               'en': 'Continue ➡️'}

yes_or_no = {'callbacks': ['yes', 'no'],
             'ru': ['Да', 'Нет'],
             'en': ['Yes', 'No']}

make_order_button = {'callback': 'make_order',
                     'ru': '☑️ ОФОРМИТЬ ЗАКАЗ',
                     'en': '☑️ MAKE ORDER'}

back_to_categories = {'callback': 'back_to_categories',
                      'ru': '⬅️ Назад к категориям',
                      'en': '⬅️ Back to categories'}

payment_method_card = {'callback': 'payment_method_card',
                       'ru': '💳 Банковская карта',
                       'en': '💳 Bank card'}

payment_method_internal_balance = {'callback': 'payment_method_internal_balance',
                                   'ru': '💲 Оплатить с баланса',
                                   'en': '💲 Pay from balance'}

payment_method_telegram_stars = {'callback': 'payment_method_telegram_stars',
                                 'ru': '⭐️ Telegram Stars',
                                 'en': '⭐️ Telegram Stars'}

card_pay = {'ru': '💳ОПЛАТИТЬ',
            'en': '💳PAY'}

check_pay = {'ru': '⏳ ПРОВЕРИТЬ ОПЛАТУ',
             'en': '⏳ CHECK PAYMENT'}

telegram_star_pay = {'ru': ' Оплатить {amount} ⭐️',
                     'en': ' Pay {amount} ⭐️'}
views_and_subscribers_special_offer = {'name': {
    'ru': '👤Подписчики + 👁 просмотры',
    'en': '👤Subscribers + 👁 views', },
    'info': {
        'ru': 'Описание',
        'en': 'Information'}
}

twenty_boosts_30_days = {'name': {
    'ru': '🔥 20 бустов (25-30 дн) 22% скидка',
    'en': '🔥 20 boosts (25-30 d) 22% discount',
},
    'info': {
        'ru': '<b>!!!ТОЛЬКО ДЛЯ НОВЫХ ПОЛЬЗОВАТЕЛЕЙ</b>!!!\n\n'
              'Бусты на закрытые и открытые каналы.\n'
              'Буст держится 25-30 дней\n\n'
              'Старая цена - 576 руб\n'
              '<b>Скидка 22%</b>',
        'en': '<b>!!!FOR NEW USERS ONLY</b>!!!\n\n'
              'Boosts for closed and open channels.\n'
              'The boost lasts 25-30 days\n\n'
              'Old price - 576 rub\n'
              '<b>22% Discount</b>'
    }
}
