import re
from html import escape

from aiogram import types
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext

import config
from busines_logic.referrals_managment import register_new_referral
from core.db import users, promo
from core.db.main_orders_queue import orders_queue
from core.localisation.lang import default_language
from core.localisation.texts import messages
from loader import dp, bot
from utils import commands
from utils.keyboards import navigation_kb
from utils.navigation import return_to_menu
from utils.order_presentation import format_order_card


ORDER_PAYLOAD_RE = re.compile(r'^order_([A-Za-z0-9_-]+)$')


async def _send_admin_order_card(msg: types.Message, internal_order_id: str) -> bool:
    order = await orders_queue.get_document(internal_order_id)
    if not order:
        await msg.answer(f'Заказ с внутренним ID <code>{escape(internal_order_id)}</code> не найден.')
        return True
    for card_part in format_order_card(order):
        await msg.answer(card_part)
    return True


@dp.message(Command('start'))
async def handle_start(msg: types.Message, command: CommandObject, state: FSMContext):
    user_id = msg.from_user.id

    if msg.chat.type != 'private':
        return

    start_link_args = command.args
    match = ORDER_PAYLOAD_RE.fullmatch(start_link_args or '')
    if match and user_id == config.ADMIN_ID:
        await _send_admin_order_card(msg, match.group(1))
        return

    user_lang_code = msg.from_user.language_code
    lang = default_language(user_lang_code)
    if await users.is_new(user_id):

        name = msg.from_user.full_name
        username = msg.from_user.username
        await users.register(user_id, username, name, lang)
        promo_name = 'balance_for_new_users'
        await msg.answer(messages.welcome[lang].format(support_contact=config.SUPPORT_BOT_URL))
        await msg.answer(messages.change_lang[lang], reply_markup=navigation_kb.select_lang().as_markup())

        if start_link_args and start_link_args.startswith('ref'):
            inviter_id = int(start_link_args.replace('ref', ''))
            await register_new_referral(inviter_id, user_id)

        if not await promo.is_completed(promo_name):
            await promo.add_participant(promo_name, user_id)
            await msg.answer(messages.promo_activated[lang])
    else:
        if await users.is_inactive_user(user_id):
            await users.set_active_status(user_id, True)
        await return_to_menu(user_id, state)

    await commands.set_commands(lang, bot)