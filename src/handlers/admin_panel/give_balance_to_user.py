import asyncio
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from html import escape
from uuid import uuid4

from aiogram import F, types
from aiogram.fsm.context import FSMContext
from pymongo import ReturnDocument

import config
from core.db import users
from core.db.models.transaction_item import TransactionItem
from core.db.transactions import transactions
from enums.transaction_type import TransactionType
from core.localisation.texts import messages
from loader import bot, dp
from utils import states
from utils.keyboards import admin as admin_kb
from utils.methods import safe_delete_callback_message

ADMIN_GIVE_BALANCE_CALLBACK = 'admin_give_balance'
ADMIN_CONFIRM_DEPOSIT_CALLBACK = 'admin_confirm_balance_deposit'
ADMIN_CANCEL_DEPOSIT_CALLBACK = 'admin_cancel_balance_deposit'

# Защита от двойного клика/параллельной обработки подтверждения в рамках процесса.
_manual_deposit_lock = asyncio.Lock()


async def _is_admin(user_id: int) -> bool:
    return user_id == config.ADMIN_ID


def _format_amount(amount: float) -> str:
    if float(amount).is_integer():
        return str(int(amount))
    return f'{amount:.2f}'


def _build_user_link(user_doc: dict) -> str:
    user_id = user_doc.get('id')
    username = user_doc.get('username')
    name = user_doc.get('name') or username or f'ID {user_id}'
    safe_name = escape(name)

    if username:
        return f'<a href="https://t.me/{username}">{safe_name}</a>'
    return f'<a href="tg://user?id={user_id}">{safe_name}</a>'


def _parse_user_id(text: str) -> int | None:
    value = (text or '').strip()
    if not value.isdigit():
        return None

    user_id = int(value)
    if user_id <= 0:
        return None

    return user_id


def _parse_amount(text: str) -> float | None:
    normalized = (text or '').strip().replace(',', '.')

    try:
        amount = Decimal(normalized)
    except InvalidOperation:
        return None

    if amount <= 0:
        return None

    amount = amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return float(amount)


async def _build_confirmation_text(target_user: dict, amount: float) -> str:
    user_link = _build_user_link(target_user)
    formatted_amount = _format_amount(amount)
    return (
        f'Начислить <b>{formatted_amount} руб.</b> пользователю {user_link}?\n\n'
        f'ID: <code>{target_user.get("id")}</code>'
    )


async def notification_to_user(user_id: int, amount: float):
    lang = await users.get_user_lang(user_id) or 'ru'
    amount_text = _format_amount(amount)
    text = messages.manual_balance_deposit_received[lang].format(amount=amount_text)

    try:
        await bot.send_message(user_id, text)
    except Exception as e:
        print(f'[manual_deposit] Failed to notify user {user_id}: {e}')


async def _apply_manual_deposit(
    *,
    admin_id: int,
    target_user: dict,
    amount: float,
    operation_id: str,
) -> tuple[float, bool]:
    existing_transaction = await transactions.collection.find_one(
        {'meta.manual_deposit_operation_id': operation_id},
        {'balance_after': 1}
    )
    if existing_transaction:
        balance_after = round(float(existing_transaction.get('balance_after') or 0), 2)
        return balance_after, True

    new_user_doc = await users.collection.find_one_and_update(
        {'id': target_user['id']},
        {'$inc': {'balance': round(amount, 2)}},
        return_document=ReturnDocument.AFTER,
        projection={'balance': 1}
    )

    if not new_user_doc:
        raise ValueError('Пользователь не найден при начислении')

    balance_after = round(float(new_user_doc.get('balance', 0.0)), 2)

    meta = {
        'source': 'admin_manual_deposit',
        'manual': True,
        'manual_deposit_operation_id': operation_id,
        'admin_id': admin_id,
        'target_user_id': target_user.get('id'),
        'target_username': target_user.get('username'),
        'target_name': target_user.get('name'),
        'credited_at_utc': datetime.now(timezone.utc).isoformat(),
    }

    transaction_item = TransactionItem(
        user_id=target_user['id'],
        transaction_type=TransactionType.DEPOSIT,
        amount=round(amount, 2),
        balance_after=balance_after,
        meta=meta,
    )

    transaction_data = (
        transaction_item.model_dump() if hasattr(transaction_item, 'model_dump') else transaction_item.dict()
    )

    result = await transactions.collection.update_one(
        {'meta.manual_deposit_operation_id': operation_id},
        {'$setOnInsert': transaction_data},
        upsert=True
    )

    if result.upserted_id is None:
        # Если в момент между проверкой и записью кто-то уже создал транзакцию,
        # откатываем инкремент баланса, чтобы не было двойного начисления.
        await users.collection.update_one({'id': target_user['id']}, {'$inc': {'balance': -round(amount, 2)}})
        existing_transaction = await transactions.collection.find_one(
            {'meta.manual_deposit_operation_id': operation_id},
            {'balance_after': 1}
        )
        if existing_transaction:
            return round(float(existing_transaction.get('balance_after') or 0), 2), True
        raise RuntimeError('Не удалось завершить начисление: операция уже существовала, но без данных транзакции')

    return balance_after, False


@dp.callback_query(F.data == ADMIN_GIVE_BALANCE_CALLBACK)
async def start_manual_balance_flow(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    if not await _is_admin(user_id):
        await query.answer()
        return

    await state.clear()
    await state.set_state(states.AdminStates.waiting_for_balance_user_id)

    await query.message.answer('Введите ID пользователя, которому нужно начислить баланс:')
    await query.answer()


@dp.message(states.AdminStates.waiting_for_balance_user_id)
async def take_target_user_id(msg: types.Message, state: FSMContext):
    if not await _is_admin(msg.from_user.id):
        return

    target_user_id = _parse_user_id(msg.text)
    if target_user_id is None:
        await msg.answer('ID должен быть положительным числом. Попробуйте снова:')
        return

    target_user = await users.collection.find_one({'id': target_user_id}, {'id': 1, 'username': 1, 'name': 1})
    if not target_user:
        await msg.answer('Пользователь с таким ID не найден в базе. Введите другой ID:')
        return

    await state.update_data(target_user=target_user)
    await state.set_state(states.AdminStates.waiting_for_balance_amount)

    await msg.answer('Введите сумму начисления в рублях (например, 50 или 50.25):')


@dp.message(states.AdminStates.waiting_for_balance_amount)
async def take_balance_amount(msg: types.Message, state: FSMContext):
    if not await _is_admin(msg.from_user.id):
        return

    amount = _parse_amount(msg.text)
    if amount is None:
        await msg.answer('Сумма должна быть числом больше 0. Пример: 50 или 50.25')
        return

    data = await state.get_data()
    target_user = data.get('target_user')
    if not target_user:
        await state.clear()
        await msg.answer('Не удалось получить данные пользователя. Начните заново через /admin.')
        return

    operation_id = str(uuid4())
    await state.update_data(amount=amount, operation_id=operation_id)
    await state.set_state(states.AdminStates.waiting_for_balance_confirmation)

    confirmation_text = await _build_confirmation_text(target_user, amount)
    await msg.answer(confirmation_text, reply_markup=admin_kb.manual_balance_confirmation().as_markup())


@dp.callback_query(
    F.data == ADMIN_CONFIRM_DEPOSIT_CALLBACK,
    states.AdminStates.waiting_for_balance_confirmation,
)
async def confirm_balance_deposit(query: types.CallbackQuery, state: FSMContext):
    admin_id = query.from_user.id
    if not await _is_admin(admin_id):
        await query.answer()
        return

    async with _manual_deposit_lock:
        data = await state.get_data()
        target_user = data.get('target_user')
        amount = data.get('amount')
        operation_id = data.get('operation_id')

        if not target_user or not amount or not operation_id:
            await state.clear()
            await query.message.answer('Не хватает данных для начисления. Начните заново через /admin.')
            await query.answer()
            return

        try:
            balance_after, already_processed = await _apply_manual_deposit(
                admin_id=admin_id,
                target_user=target_user,
                amount=float(amount),
                operation_id=operation_id,
            )
        except Exception as e:
            await query.message.answer(f'Ошибка при начислении: {e}')
            await query.answer()
            return

        user_link = _build_user_link(target_user)
        amount_text = _format_amount(float(amount))

        if already_processed:
            await query.message.answer(
                f'Операция уже была выполнена ранее.\n'
                f'Пользователь: {user_link}\n'
                f'Баланс после операции: <b>{balance_after:.2f} руб.</b>'
            )
        else:
            await query.message.answer(
                f'Готово. Начислено <b>{amount_text} руб.</b> пользователю {user_link}.\n'
                f'Новый баланс: <b>{balance_after:.2f} руб.</b>'
            )
            await notification_to_user(target_user.get('id'), float(amount))

        await state.clear()
        await safe_delete_callback_message(query)
        await query.answer('Начисление обработано')


@dp.callback_query(
    F.data == ADMIN_CANCEL_DEPOSIT_CALLBACK,
    states.AdminStates.waiting_for_balance_confirmation,
)
async def cancel_balance_deposit(query: types.CallbackQuery, state: FSMContext):
    if not await _is_admin(query.from_user.id):
        await query.answer()
        return

    await state.clear()
    await query.message.answer('Начисление отменено.')
    await safe_delete_callback_message(query)
    await query.answer('Отменено')







