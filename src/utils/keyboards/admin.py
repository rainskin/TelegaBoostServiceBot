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


def orders_page(page: int, total_pages: int):
    """Inline navigation for the administrative order list."""
    builder = InlineKeyboardBuilder()
    if total_pages <= 1:
        return builder

    if page > 1:
        builder.button(text='← Назад', callback_data=f'admin_orders_page:{page - 1}')
    builder.button(text=f'{page}/{total_pages}', callback_data='admin_orders_page:current')
    if page < total_pages:
        builder.button(text='Вперёд →', callback_data=f'admin_orders_page:{page + 1}')
    builder.adjust(3 if 1 < page < total_pages else 2)
    return builder


def manual_balance_confirmation():
    builder = InlineKeyboardBuilder()
    builder.button(text='✅ Подтвердить', callback_data='admin_confirm_balance_deposit')
    builder.button(text='❌ Отменить', callback_data='admin_cancel_balance_deposit')
    return builder.adjust(2)
