from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from core.db import users
from core.localisation.texts import messages
from core.storage import storage
from loader import dp, bot
from utils.keyboards import navigation_kb
from utils.states import NewOrder


# current_data =
#
# service_id
# "97"
# rate
# 750
# min_value
# 1
# max_value
# # 10000
# total_amount
# 111
# quantity
# 245
# service_msg_ids
# [6548, ..., ..., ..., ..., ..., ...]

@dp.callback_query(F.data == 'to_continue', NewOrder.choosing_quantity)
async def _(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    lang = users.get_user_lang(user_id)
    chat_id = query.message.chat.id
    key = StorageKey(bot.id, chat_id, user_id)
    data = await storage.get_data(key)
    service_msg_ids: list = data['service_msg_ids']
    rate = data['rate']

    await query.answer()
    msg = await query.message.answer(messages.ask_url[lang])
    service_msg_ids.append(msg.message_id)
    await state.set_state(NewOrder.waiting_for_url)
    await query.message.delete()


@dp.message(NewOrder.waiting_for_url)
async def _(msg: types.Message, state: FSMContext):
    user_id = msg.from_user.id
    lang = users.get_user_lang(user_id)
    currency = 'RUB'
    chat_id = msg.chat.id
    key = StorageKey(bot.id, chat_id, user_id)
    data = await storage.get_data(key)
    service_msg_ids: list = data['service_msg_ids']
    quantity = data['quantity']
    total_amount = data['total_amount']

    entities = msg.entities or msg.entities or msg.caption_entities or []
    text = msg.text or msg.caption
    url = _get_url_from_text(text, entities)

    if not url:
        service_msg = await msg.answer(messages.incorrect_url[lang])
        service_msg_ids.append(service_msg.message_id)
        return

    url = url[0] # first value

    msg_text = messages.correct_url[lang].format(url=url, quantity=quantity, total_amount=total_amount,
                                                 currency=currency)
    service_msg = await msg.answer(msg_text, reply_markup=navigation_kb.order_navigation(lang, make_order_btn=True).as_markup())
    service_msg_ids.append(service_msg.message_id)
    await storage.update_data(key, service_msg_ids=service_msg_ids, url=url)
    await state.set_state(NewOrder.check_details)


def _get_url_from_text(text, entities) -> list | None:
    """
    return first correct url (url type) or []
    """
    url = []
    for entity in entities:
        if entity.type == 'url':
            url.append(text[entity.offset:entity.offset + entity.length])

    return url
