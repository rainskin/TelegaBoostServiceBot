from typing import List, Dict, Any

import config
import requests

from core.db import users
from loader import bot

API_TOKEN = config.API_TOKEN
BASE_URL = config.BASE_URL


async def make_request(url: str, user_id: int) -> Any:
    lang = users.get_user_lang(user_id)
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        error_message = "HTTP request failed: An error occurred while processing your request. Обратитесь в поддержку, пожалуйста"
        print(error_message)
        await bot.send_message(chat_id=user_id, text=error_message)
        return None
    except ValueError as e:
        error_message = "Failed to decode JSON response: An error occurred while processing the response. Обратитесь в поддержку, пожалуйста"
        print(error_message)
        await bot.send_message(chat_id=user_id, text=error_message)
        return None


async def get_balance():
    method = 'balance'
    url = f'{BASE_URL}{method}&key={API_TOKEN}'
    response = await make_request(url, config.ADMIN_ID)
    current_balance: str = response['balance']

    return round(float(current_balance), 2)


async def get_available_services(user_id: int):
    method = 'services'
    url = f'{BASE_URL}{method}&key={API_TOKEN}'
    services = await make_request(url, user_id)

    categories = []
    for i in services:
        category = i['category']
        if category not in categories:
            categories.append(category)

    return categories


async def get_tariffs(category_name, user_id: int):
    method = 'services'
    url = f'{BASE_URL}{method}&key={API_TOKEN}'
    services = await make_request(url, user_id)
    print(services)

    tariffs = []
    for service in services:
        if service['category'] == category_name:
            tariffs.append(service)

    return tariffs


async def get_service(tariff_id: int, user_id: int):
    method = 'services'
    url = f'{BASE_URL}{method}&key={API_TOKEN}'
    services = await make_request(url, user_id)

    for service in services:
        service_id = service['service']
        if service_id == tariff_id:
            return service


async def get_order_statuses(order_ids: List[str], user_id: int) -> Dict[str, dict]:
    method = 'status'
    orders_ids = ','.join(order_ids)
    url = f'{BASE_URL}{method}&orders={orders_ids}&key={API_TOKEN}'
    orders: Dict[str, dict] = await make_request(url, user_id)
    filtered_statuses = {str(order_id): status for order_id, status in orders.items() if 'error' not in status}
    return filtered_statuses


async def create_new_order(user_id: int, service_id: str, link: str, quantity: int):
    method = 'add'
    service_id = service_id
    quantity = str(quantity)
    url = (f'{BASE_URL}{method}&'
           f'service={service_id}&'
           f'link={link}'
           f'&quantity={quantity}&'
           f'key={API_TOKEN}')

    response = await make_request(url, user_id)
    order_id: int = response['order']
    print(f'оформил заказик')
    return order_id


# order_ids = [70117436, 111]
# print(f'{type(get_orders_status(order_ids, 1111123))}, {get_orders_status(order_ids, 1111123)}')
