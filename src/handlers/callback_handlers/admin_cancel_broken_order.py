import config
from aiogram import F, types

from core.db.main_orders_queue import orders_queue
from loader import dp
from utils import callback_templates
from handlers.callback_handlers.cancel_order import cancel_not_accepted_order_by_internal_order_id

template = callback_templates.admin_cancel_broken_order()


@dp.callback_query(F.data.startswith(template))
async def _(query: types.CallbackQuery):
    if query.from_user.id != config.ADMIN_ID:
        await query.answer()
        return

    internal_order_id = query.data.replace(template, '')
    order_item = await orders_queue.get(internal_order_id)

    if not order_item:
        await query.answer()
        await query.message.edit_reply_markup(reply_markup=None)
        await query.message.answer(f'Заказ {internal_order_id} не найден или уже был очищен.')
        return

    is_canceled, amount = await cancel_not_accepted_order_by_internal_order_id(
        order_item.user_id,
        internal_order_id,
        provider_error_message=order_item.provider_error_message,
        send_user_notification=True,
    )

    if not is_canceled:
        await query.answer()
        await query.message.edit_reply_markup(reply_markup=None)
        await query.message.answer(f'Заказ {internal_order_id} уже был обработан ранее.')
        return

    await query.answer()
    await query.message.edit_reply_markup(reply_markup=None)
    await query.message.answer(
        f'Заказ {internal_order_id} отменен. Пользователю возвращено {amount:.2f} RUB.'
    )
