welcome = {'ru': "Здесь можно заказать накрутку для телеграма.",
           'en': 'Here you can order subscribers, views and other services for telegram.'}

lang_is_changed = {'ru': "Язык успешно изменен",
                   'en': "Language changed successfully"}

change_lang = {'ru': "Выберите ваш язык",
               'en': "Select your language"}

plans = {'ru': "Выбери, что тебя интересует:",
         'en': 'Choose what interests you:'}

main_menu = {'ru': "🏠 <b>Главное меню:</b>",
             'en': '🏠 <b>Main menu:</b>'}

active_orders = {'ru': 'Ваши текущие заказы',
                 'en': 'Your current orders'}

no_active_orders = {'ru': "Нет активных заказов",
                    'en': "No active orders"}

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


def get_plan_info_text(lang: str, name, description: str, rate, min_count, max_count, canceling_is_available):
    currency = 'RUB'
    canceling_is_available = plan_info['canceling_is_available'][lang] if canceling_is_available else \
        plan_info['canceling_is_not_available'][lang]
    print(name, '\n' in name)
    print(description.startswith('\n'), description)

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
