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
