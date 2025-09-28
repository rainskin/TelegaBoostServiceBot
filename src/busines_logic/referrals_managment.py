import asyncio

from core.db import users, admin
from core.db.models.transaction_item import TransactionItem
from core.db.transactions import transactions
from enums.transaction_type import TransactionType
from loader import bot


async def register_new_referral(inviter_id: int, referral_id: int):
    users.add_referral(inviter_id, referral_id)
    users.assign_inviter(referral_id, inviter_id)
    referral = await bot.get_chat(referral_id)

    await bot.send_message(inviter_id, f'Вы успешно пригласили пользователя {referral.full_name}')
    await asyncio.sleep(10)


async def add_referral_reward(inviter_id: int, deposit_amount: float, referral_id: int, payment_id: str):
    referral_deposit_reward_percent = admin.get_referral_deposit_reward()
    referral_reward = await get_referral_reward(deposit_amount, referral_deposit_reward_percent)
    user_balance = users.get_balance(inviter_id)

    meta = {
        "referral_id": referral_id,
        "payment_id": payment_id,
        "note": ''
    }
    transaction_item = TransactionItem(
        user_id=inviter_id,
        transaction_type=TransactionType.REFERRAL_REWARD,
        amount=-referral_reward,
        balance_after=round((user_balance + referral_reward), 2),
        meta=meta
    )
    await transactions.save(transaction_item)
    users.add_balance(inviter_id, referral_reward)
    users.increment_referrals_reward(inviter_id, referral_reward)

    formatted_referral_reward = f'{referral_reward:.2f}'
    msg_text = f'Вам начислено <b>{formatted_referral_reward} руб.</b> Вознаграждение за пополнение рефералом.'
    await bot.send_message(inviter_id, msg_text)


async def get_referral_reward(amount: float, percentage: int):
    return amount / 100 * percentage
