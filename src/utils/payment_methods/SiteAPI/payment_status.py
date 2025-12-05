import requests
import json

import config

async def get(order_id: str):
    # Request Headers
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": config.DOMAIN_API_KEY
    }

    # Request Body
    payload = {
        "order_id": order_id
    }

    try:
        url = f'{config.DOMAIN_BASE_URL}/api/v1/get_payment_status'
        response = requests.post(url, headers=headers, data=json.dumps(payload), verify=False)
        print(response)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        r = response.json().get('status').lower()
        return r

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
