from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from core.db import users, orders
from core.localisation.texts import messages
from core.storage import storage
from handlers.new_order.create import place_order
from loader import dp, bot
from utils import callback_templates, navigation
from utils.Payment_methods.aaio.methods import get_payment_url, check_payment_status
from utils.Payment_methods.aaio.payment_statuses import current_payment_status_translated
from utils.keyboards.payment_methods import card_payment
from utils.states import Payment


@dp.callback_query(F.data == 'payment_method_card', Payment.choosing_method)
async def _(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    chat_id = query.message.chat.id
    key = StorageKey(bot.id, chat_id, user_id)
    lang = users.get_user_lang(user_id)
    data: dict = await storage.get_data(key)
    total_amount: float = data['total_amount']
    internal_order_id = data['internal_order_id']
    data['service_msg_ids'] = []

    payment_url = await get_payment_url(internal_order_id, total_amount, lang)
    await query.answer()

    kb = card_payment(lang, payment_url, internal_order_id)
    await query.message.answer(messages.payment_by_card[lang].format(order_id=internal_order_id),
                               reply_markup=kb.as_markup())
    await state.set_state(None)
    await query.message.delete()


template = callback_templates.check_payment()


@dp.callback_query(F.data.startswith(template))
async def _(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    lang = users.get_user_lang(user_id)
    internal_order_id = query.data.replace(template, '')
    data = orders.get_last_order_info(user_id)
    status = await check_payment_status(user_id, internal_order_id)
    status_msg_ids = []

    if data and internal_order_id == data['internal_order_id']:
        if not status:
            await query.answer()
            return

        if status != 'success':
            text = (f'{messages.current_payment_status[lang]}:\n\n'
                    f'{current_payment_status_translated[status][lang]}')

            msg = await query.message.answer(text)
            status_msg_ids.append(msg.message_id)
            await query.answer()
            return

        hot_order = data['hot_order']
        await place_order(user_id, internal_order_id, hot_order, data, payment_method='card')
        message = f'{messages.order_is_created[lang].format(order_id=internal_order_id)}'
        orders.reset_last_order_info(user_id)

        await query.message.answer(message)
        await query.message.delete()
        await navigation.return_to_menu(user_id, state)
        if status_msg_ids:
            await bot.delete_messages(user_id, status_msg_ids)

    else:
        message = messages.some_error_try_again[lang]
        await query.message.answer(message)

    await query.answer()
