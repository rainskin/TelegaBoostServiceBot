import asyncio

from core.db import users, admin
from loader import bot


async def register_new_referral(inviter_id: int, referral_id: int):
    users.add_referral(inviter_id, referral_id)
    users.assign_inviter(referral_id, inviter_id)
    await bot.send_message(inviter_id, f'Вы успешно пригласили пользователя {referral_id}')
    await asyncio.sleep(10)


async def add_referral_reward(inviter_id: int, deposit_amount: float):
    referral_deposit_reward_percent = admin.get_referral_deposit_reward()
    referral_reward = await get_referral_reward(deposit_amount, referral_deposit_reward_percent)
    users.add_balance(inviter_id, referral_reward)
    users.increment_referrals_reward(inviter_id, referral_reward)

    formatted_referral_reward = f'{referral_reward:.2f}'
    msg_text = f'Вам начислено <b>{formatted_referral_reward} руб.</b> Вознаграждение за пополнение рефералом.'
    await bot.send_message(inviter_id, msg_text)


async def get_referral_reward(amount: float, percentage: int):
    return amount / 100 * percentage
