from aiogram.utils.keyboard import InlineKeyboardBuilder


def orders_manage():
    builder = InlineKeyboardBuilder()
    builder.button(text='Оформить все заказы', callback_data='to_take_all_orders')
    return builder.adjust(1)


def admin_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text='Заказы', callback_data='manage_orders')
    builder.button(text='🎁Начислить баланс', callback_data='admin_give_balance')
    return builder.adjust(1)


def manual_balance_confirmation():
    builder = InlineKeyboardBuilder()
    builder.button(text='✅ Подтвердить', callback_data='admin_confirm_balance_deposit')
    builder.button(text='❌ Отменить', callback_data='admin_cancel_balance_deposit')
    return builder.adjust(2)
