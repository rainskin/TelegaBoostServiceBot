import requests
from requests.auth import HTTPBasicAuth
from config import SWORK_API_URL, SWORK_SHOP_ID, SWORK_API_KEY


async def get(order_id: str) -> str | None:
    response = None
    try:
        response = requests.get(
            f"{SWORK_API_URL}/status",
            params={'order_id': order_id},
            auth=HTTPBasicAuth(SWORK_SHOP_ID, SWORK_API_KEY),
        )
        response.raise_for_status()
        return response.json().get('status')

    except requests.exceptions.HTTPError as e:
        if response and response.status_code == 404:
            print(f"Order '{order_id}' not found.")
            return None
        raise Exception(f"HTTP error {response.status_code if response else 'unknown'}: response: {response.json()}")

    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed: {e}") from e
