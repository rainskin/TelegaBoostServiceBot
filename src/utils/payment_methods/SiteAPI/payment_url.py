import hmac
import hashlib
import base64
import json

import config
from core.env import env


async def generate_payment_token(telegram_id, order_id, amount_rubles):
    """
    Generates a secure token for the payment page URL.
    """
    secret_key = config.SWORK_API_KEY

    payload = {
        "telegram_id": telegram_id,
        "order_id": order_id,
        "amount": amount_rubles
    }

    # Serialize and encode the payload
    message = json.dumps(payload, sort_keys=True).encode('utf-8')
    b64_payload = base64.urlsafe_b64encode(message).decode('utf-8')

    # Create the HMAC signature
    signature = hmac.new(
        secret_key.encode('utf-8'),
        b64_payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    # Combine signature and payload to form the final token
    token = f"{signature}.{b64_payload}"

    return token


async def get(user_id: int, order_id: str, amount: float):

    token = await generate_payment_token(user_id, order_id, amount)

    # Example of how to construct the full URL
    base_url = config.DOMAIN_BASE_URL
    full_url = f"{base_url}/top-up/{token}/"
    return full_url

