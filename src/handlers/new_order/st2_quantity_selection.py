import math

from aiogram import types, F
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from core.db import users
from core.localisation.texts import messages
from core.storage import storage
from loader import dp, bot
from utils import states
from utils.keyboards import navigation_kb


@dp.message(F.content_type == ContentType.TEXT, states.NewOrder.choosing_quantity)
async def _(msg: types.Message, state: FSMContext):
    user_id = msg.from_user.id
    lang = await users.get_user_lang(user_id)
    chat_id = msg.chat.id
    key = StorageKey(bot.id, chat_id, user_id)
    data = await storage.get_data(key)
    min_value = data['min_value']
    max_value = data['max_value']
    rate = data['rate']
    old_rate = data['old_rate']
    service_msg_ids: list = data['service_msg_ids']

    try:
        value = int(msg.text)
    except ValueError as e:
        service_msg = await msg.answer(
            messages.value_is_not_number[lang].format(min_value=min_value, max_value=max_value))
        service_msg_ids.append(service_msg.message_id)
        await storage.update_data(key, service_msg_ids=service_msg_ids)
        return

    if not is_valid_quantity(value, min_value, max_value):

        service_msg = await msg.answer(messages.wrong_quantity[lang].format(min_value=min_value, max_value=max_value))
        service_msg_ids.append(service_msg.message_id)

    else:
        total_amount = get_amount_by_rate_and_quantity(rate, value)
        amount_without_commission = get_amount_by_rate_and_quantity(old_rate, value)
        profit = total_amount - amount_without_commission
        currency = 'RUB'
        service_msg = await msg.answer(messages.valid_quantity[lang].format(total_cost=total_amount, currency=currency),
                                       reply_markup=navigation_kb.order_navigation(lang).as_markup())
        if service_msg_ids:
            await bot.delete_messages(chat_id, service_msg_ids)
            service_msg_ids = []

        service_msg_ids.append(service_msg.message_id)
        await storage.update_data(key, quantity=value, total_amount=total_amount, amount_without_commission=amount_without_commission, profit=profit)

    await storage.update_data(key, service_msg_ids=service_msg_ids)


def is_valid_quantity(value: int, min_value: int, max_value: int):
    return min_value <= value <= max_value

def get_amount_by_rate_and_quantity(rate: int, quantity: int):
    return round((quantity * rate / 1000), 2)


@dp.message(F.content_type == ContentType.TEXT, states.NewOrder.choosing_subscription_posts)
async def _(msg: types.Message, state: FSMContext):
    user_id = msg.from_user.id
    lang = await users.get_user_lang(user_id)
    chat_id = msg.chat.id
    key = StorageKey(bot.id, chat_id, user_id)
    data = await storage.get_data(key)
    service_msg_ids: list = data['service_msg_ids']
    subscription_posts_min = data.get('subscription_posts_min', 1)

    try:
        posts = int(msg.text)
    except ValueError:
        service_msg = await msg.answer(
            messages.subscription_posts_is_not_number[lang].format(min_value=subscription_posts_min)
        )
        service_msg_ids.append(service_msg.message_id)
        await storage.update_data(key, service_msg_ids=service_msg_ids)
        return

    if posts < subscription_posts_min:
        service_msg = await msg.answer(
            messages.wrong_subscription_posts[lang].format(min_value=subscription_posts_min)
        )
        service_msg_ids.append(service_msg.message_id)
        await storage.update_data(key, service_msg_ids=service_msg_ids)
        return

    service_msg = await msg.answer(messages.ask_subscription_min[lang].format(min_value=data['min_value']))
    service_msg_ids.append(service_msg.message_id)
    await storage.update_data(key, subscription_posts=posts, service_msg_ids=service_msg_ids)
    await state.set_state(states.NewOrder.choosing_subscription_min)


@dp.message(F.content_type == ContentType.TEXT, states.NewOrder.choosing_subscription_min)
async def _(msg: types.Message, state: FSMContext):
    user_id = msg.from_user.id
    lang = await users.get_user_lang(user_id)
    chat_id = msg.chat.id
    key = StorageKey(bot.id, chat_id, user_id)
    data = await storage.get_data(key)
    service_msg_ids: list = data['service_msg_ids']
    min_value = data['min_value']

    try:
        subscription_min = int(msg.text)
    except ValueError:
        service_msg = await msg.answer(messages.subscription_min_is_not_number[lang].format(min_value=min_value))
        service_msg_ids.append(service_msg.message_id)
        await storage.update_data(key, service_msg_ids=service_msg_ids)
        return

    if subscription_min < min_value:
        service_msg = await msg.answer(messages.wrong_subscription_min[lang].format(min_value=min_value))
        service_msg_ids.append(service_msg.message_id)
        await storage.update_data(key, service_msg_ids=service_msg_ids)
        return

    service_msg = await msg.answer(messages.ask_subscription_max[lang].format(max_value=data['max_value']))
    service_msg_ids.append(service_msg.message_id)
    await storage.update_data(key, subscription_min=subscription_min, service_msg_ids=service_msg_ids)
    await state.set_state(states.NewOrder.choosing_subscription_max)


@dp.message(F.content_type == ContentType.TEXT, states.NewOrder.choosing_subscription_max)
async def _(msg: types.Message, state: FSMContext):
    user_id = msg.from_user.id
    lang = await users.get_user_lang(user_id)
    chat_id = msg.chat.id
    key = StorageKey(bot.id, chat_id, user_id)
    data = await storage.get_data(key)
    service_msg_ids: list = data['service_msg_ids']
    max_value = data['max_value']
    subscription_min = data['subscription_min']

    try:
        subscription_max = int(msg.text)
    except ValueError:
        service_msg = await msg.answer(messages.subscription_max_is_not_number[lang].format(max_value=max_value))
        service_msg_ids.append(service_msg.message_id)
        await storage.update_data(key, service_msg_ids=service_msg_ids)
        return

    if subscription_max > max_value:
        service_msg = await msg.answer(messages.wrong_subscription_max[lang].format(max_value=max_value))
        service_msg_ids.append(service_msg.message_id)
        await storage.update_data(key, service_msg_ids=service_msg_ids)
        return

    if subscription_min >= subscription_max:
        service_msg = await msg.answer(messages.subscription_min_greater_than_max[lang])
        service_msg_ids.append(service_msg.message_id)
        await storage.update_data(key, service_msg_ids=service_msg_ids)
        return

    subscription_posts = data['subscription_posts']
    quantity = calculate_subscription_quantity(subscription_posts, subscription_min, subscription_max)
    total_amount = get_amount_by_rate_and_quantity(data['rate'], quantity)
    amount_without_commission = get_amount_by_rate_and_quantity(data['old_rate'], quantity)
    profit = total_amount - amount_without_commission
    currency = 'RUB'

    service_msg = await msg.answer(
        messages.valid_subscription_quantity[lang].format(
            posts=subscription_posts,
            min_views=subscription_min,
            max_views=subscription_max,
            quantity=quantity,
            total_cost=total_amount,
            currency=currency,
        ),
        reply_markup=navigation_kb.order_navigation(lang).as_markup(),
    )
    if service_msg_ids:
        await bot.delete_messages(chat_id, service_msg_ids)
        service_msg_ids = []

    service_msg_ids.append(service_msg.message_id)
    await storage.update_data(
        key,
        subscription_max=subscription_max,
        quantity=quantity,
        total_amount=total_amount,
        amount_without_commission=amount_without_commission,
        profit=profit,
        service_msg_ids=service_msg_ids,
    )


def calculate_subscription_quantity(posts: int, min_views: int, max_views: int) -> int:
    return math.ceil(posts * ((min_views + max_views) / 2))
