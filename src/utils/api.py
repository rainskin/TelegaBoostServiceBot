from typing import List, Dict, Any

import aiohttp

import config
import requests
import asyncio
from core.db import users
from loader import bot

API_TOKEN = config.API_TOKEN
BASE_URL = config.BASE_URL


# async def make_request(url: str, user_id: int) -> Any:
#     try:
#         response = requests.get(url)
#         response.raise_for_status()
#         return response.json()
#     except requests.RequestException as e:
#         error_message = "HTTP request failed: An error occurred while processing your request. Обратитесь в поддержку, пожалуйста"
#         await bot.send_message(chat_id=user_id, text=error_message)
#         return None
#     except ValueError as e:
#         error_message = "Failed to decode JSON response: An error occurred while processing the response. Обратитесь в поддержку, пожалуйста"
#         await bot.send_message(chat_id=user_id, text=error_message)
#         return None


# Универсальная обертка с ретраями
async def make_request(url: str, user_id: int, retries: int = 3, cooldown: int = 5) -> Any:
    for attempt in range(1, retries + 1):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    response.raise_for_status()
                    return await response.json()

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            # Если это не последняя попытка — ждем и пробуем еще раз
            if attempt < retries:
                await asyncio.sleep(cooldown * attempt)  # задержка растёт
                continue

            error_message = (
                f"❌ Ошибка HTTP-запроса (попытка {attempt}/{retries}).\n"
                f"Ошибка: {str(e)}"
            )
            await bot.send_message(chat_id=config.ADMIN_ID, text=error_message)
            return None

        except Exception as e:
            error_message = (
                f"❌ Непредвиденная ошибка при обработке запроса.\n"
                f"Ошибка: {str(e)}"
            )
            await bot.send_message(chat_id=config.ADMIN_ID, text=error_message)
            return None


async def get_account_balance():
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


# async def create_new_order(user_id: int, service_id: str, link: str, quantity: int):
#     method = 'add'
#     service_id = service_id
#     quantity = str(quantity)
#     url = (f'{BASE_URL}{method}&'
#            f'service={service_id}&'
#            f'link={link}'
#            f'&quantity={quantity}&'
#            f'key={API_TOKEN}')
#
#     response = await make_request(url, user_id)
#     order_id: int = response['order']
#     return order_id

async def create_new_order(user_id: int, service_id: str, link: str, quantity: int) -> int | None:
    method = 'add'
    url = (
        f"{BASE_URL}{method}&"
        f"service={service_id}&"
        f"link={link}&"
        f"quantity={quantity}&"
        f"key={API_TOKEN}"
    )

    response = await make_request(url, user_id)

    if response is None:
        return None  # если все ретраи упали — возвращаем None, дальше решаешь как обработать

    try:
        order_id: int = response['order']
        return order_id
    except KeyError:
        error_message = "⚠️ API вернул неожиданный ответ при создании заказа"
        await bot.send_message(chat_id=config.ADMIN_ID, text=error_message)
        return None

async def main():
    service = await get_order_statuses(['169337601'], config.ADMIN_ID)
    print(service)


# asyncio.run(main())


# order_ids = [70117436, 111]
# print(f'{type(get_orders_status(order_ids, 1111123))}, {get_orders_status(order_ids, 1111123)}')
