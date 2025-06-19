from aiogram import F, types, Bot
from aiogram.filters import Command
from aiogram.types import LabeledPrice

from core.db.admin import build_payment_info, admin
from handlers.new_order.st4_make_order import get_internal_order_id
from loader import bot, dp
from utils import states
from utils.Payment_methods.telegram_stars.methods import send_invoice


@dp.callback_query(F.data == 'payment_method_telegram_stars', states.Payment.choosing_method)
async def _(query: types.CallbackQuery):
    user_id = query.from_user.id

    internal_order_id = await get_internal_order_id(user_id)
    payment_id = f'S{internal_order_id}'
    amount = 1
    payment_info = build_payment_info(user_id, amount, 'XTR', payment_id, balance_recharge=True)
    admin.save_payment(payment_id, payment_info)
    await send_invoice(user_id, amount)
    await query.answer()


@dp.pre_checkout_query()
async def pre_checkout_query_handler(pre_checkout_query: types.PreCheckoutQuery):
    # Here you can add any checks before confirming the payment
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message(F.successful_payment)
async def _ (msg: types.Message):
    await msg.answer(f'{msg.successful_payment.invoice_payload}'
                     f' {msg.successful_payment.telegram_payment_charge_id}', message_effect_id='5104841245755180586')


@dp.message(Command('refund'))
async def refund(msg: types.Message):
    await bot.refund_star_payment(msg.from_user.id, refund_id)


refund_id = '333'