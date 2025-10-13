import uuid

from yookassa.domain.response import PaymentResponse

from utils.payment_methods.yookassa import config
from src import config as main_config
from yookassa import Configuration, Payment

Configuration.account_id = config.SHOP_ID
Configuration.secret_key = config.API_KEY


async def create_payment(value: float) -> PaymentResponse:
    payment = Payment.create({
        "amount": {
            "value": value,
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": main_config.BOT_URL
        },
        "capture": True,
        "description": ""
    }, uuid.uuid4())

    return payment


async def get_payment_by_id(payment_id: str) -> PaymentResponse:
    payment = Payment.find_one(payment_id)
    return payment



