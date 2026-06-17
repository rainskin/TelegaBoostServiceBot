import html
import json
from typing import List, Dict, Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import aiohttp

import config
import asyncio
from core.db import users
from loader import bot

API_TOKEN = config.API_TOKEN
BASE_URL = config.BASE_URL

MAX_TELEGRAM_MESSAGE_LENGTH = 3900
DEFAULT_PROVIDER_SERVICE_TYPE = 'Default'
SUBSCRIPTIONS_PROVIDER_SERVICE_TYPE = 'Subscriptions'
SUPPORTED_PROVIDER_SERVICE_TYPES = {
    DEFAULT_PROVIDER_SERVICE_TYPE,
    SUBSCRIPTIONS_PROVIDER_SERVICE_TYPE,
}
PROVIDER_ORDER_KEY_SEPARATOR = ':'
_reported_unknown_service_types = set()


class ProviderOrderCreateError(Exception):
    def __init__(
            self,
            status_code: int,
            provider_message: str,
            formatted_body: str,
            request_url_redacted: str,
            content_type: str | None = None,
    ):
        super().__init__(provider_message)
        self.status_code = status_code
        self.provider_message = provider_message
        self.formatted_body = formatted_body
        self.request_url_redacted = request_url_redacted
        self.content_type = content_type


def _redact_api_key(url: str) -> str:
    split = urlsplit(url)
    query = parse_qsl(split.query, keep_blank_values=True)
    redacted_query = [
        (key, '***' if key.lower() == 'key' else value)
        for key, value in query
    ]

    return urlunsplit(
        (split.scheme, split.netloc, split.path, urlencode(redacted_query), split.fragment)
    )


def _format_response_body(response_text: str) -> str:
    try:
        parsed_response = json.loads(response_text)
        return json.dumps(parsed_response, ensure_ascii=False, indent=2)
    except json.JSONDecodeError:
        return response_text


def _build_api_url(method: str, params: dict[str, Any]) -> str:
    return f"{BASE_URL}{method}&{urlencode(params)}"


def build_provider_order_key(provider_service_type: str, provider_order_id: str | int) -> str:
    return f'{provider_service_type}{PROVIDER_ORDER_KEY_SEPARATOR}{provider_order_id}'


def parse_provider_order_key(provider_order_key: str) -> tuple[str, str]:
    if PROVIDER_ORDER_KEY_SEPARATOR not in provider_order_key:
        return DEFAULT_PROVIDER_SERVICE_TYPE, str(provider_order_key)

    provider_service_type, provider_order_id = provider_order_key.split(PROVIDER_ORDER_KEY_SEPARATOR, 1)
    if provider_service_type not in SUPPORTED_PROVIDER_SERVICE_TYPES or not provider_order_id:
        return DEFAULT_PROVIDER_SERVICE_TYPE, str(provider_order_key)

    return provider_service_type, provider_order_id


def _resolve_provider_order_identity(backend_order_key: str, order_info: dict | None = None) -> tuple[str, str]:
    raw_provider_order_id = str((order_info or {}).get('backend_order_id') or backend_order_key)
    parsed_service_type, parsed_provider_order_id = parse_provider_order_key(raw_provider_order_id)
    explicit_service_type = (order_info or {}).get('provider_service_type')

    if explicit_service_type in SUPPORTED_PROVIDER_SERVICE_TYPES:
        if parsed_service_type == explicit_service_type:
            return explicit_service_type, parsed_provider_order_id
        return explicit_service_type, raw_provider_order_id

    return parse_provider_order_key(str(backend_order_key))


def _extract_provider_error_message(response_text: str) -> str | None:
    try:
        payload = json.loads(response_text)
    except json.JSONDecodeError:
        return None

    if isinstance(payload, dict):
        parts: list[str] = []
        for key, value in payload.items():
            if isinstance(value, list):
                value_text = '; '.join(str(item) for item in value)
            elif isinstance(value, dict):
                value_text = '; '.join(f'{nested_key}: {nested_value}' for nested_key, nested_value in value.items())
            else:
                value_text = str(value)
            parts.append(f'{key}: {value_text}')
        if parts:
            return ' | '.join(parts)

    if isinstance(payload, list):
        return '; '.join(str(item) for item in payload)

    if payload:
        return str(payload)

    return None


async def _send_admin_log(message: str) -> None:
    for start in range(0, len(message), MAX_TELEGRAM_MESSAGE_LENGTH):
        escaped_message = html.escape(message[start:start + MAX_TELEGRAM_MESSAGE_LENGTH])
        await bot.send_message(
            chat_id=config.ADMIN_ID,
            text=f'<pre>{escaped_message}</pre>',
        )


def is_supported_provider_service_type(service_type: str | None) -> bool:
    return service_type in SUPPORTED_PROVIDER_SERVICE_TYPES


async def _report_unknown_service_types(services: list[dict]) -> None:
    unknown_services = [
        service
        for service in services
        if not is_supported_provider_service_type(service.get('type'))
    ]
    new_unknown_services = [
        service
        for service in unknown_services
        if (service.get('service'), service.get('type')) not in _reported_unknown_service_types
    ]

    if not new_unknown_services:
        return

    for service in new_unknown_services:
        _reported_unknown_service_types.add((service.get('service'), service.get('type')))

    details = '\n'.join(
        f"id={service.get('service')} type={service.get('type')} name={service.get('name')}"
        for service in new_unknown_services
    )
    await _send_admin_log(
        "⚠️ BoostTelega API вернул неизвестный тип услуги. "
        "Услуги скрыты от пользователей до добавления поддержки.\n"
        f"{details}"
    )


async def _get_supported_services(source_name: str) -> list[dict]:
    method = 'services'
    url = f'{BASE_URL}{method}&key={API_TOKEN}'
    services = await make_request(url, source_name=source_name)
    if not services:
        return []

    await _report_unknown_service_types(services)
    return [
        service
        for service in services
        if is_supported_provider_service_type(service.get('type'))
    ]


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
async def make_request(
        url: str,
        retries: int = 3,
        cooldown: int = 5,
        source_name: str = '',
        raise_http_error: bool = False,
) -> Any:
    for attempt in range(1, retries + 1):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    response_text = await response.text()

                    if response.status >= 400:
                        if attempt < retries:
                            await asyncio.sleep(cooldown * attempt)
                            continue

                        formatted_body = _format_response_body(response_text)
                        provider_message = _extract_provider_error_message(response_text)
                        redacted_url = _redact_api_key(str(response.url))

                        if raise_http_error:
                            raise ProviderOrderCreateError(
                                status_code=response.status,
                                provider_message=provider_message or f'HTTP {response.status} {response.reason}',
                                formatted_body=formatted_body,
                                request_url_redacted=redacted_url,
                                content_type=response.headers.get('Content-Type'),
                            )

                        error_message = (
                            f"❌ Ошибка HTTP-запроса во время выполнения функции {source_name}\n"
                            f"Попытка: {attempt}/{retries}\n"
                            f"URL: {redacted_url}\n"
                            f"HTTP status: {response.status} {response.reason}\n"
                            f"Content-Type: {response.headers.get('Content-Type')}\n"
                            f"Response body:\n{formatted_body}"
                        )
                        await _send_admin_log(error_message)
                        return None

                    try:
                        return json.loads(response_text)
                    except json.JSONDecodeError as e:
                        error_message = (
                            f"❌ API вернул невалидный JSON во время выполнения функции {source_name}\n"
                            f"Попытка: {attempt}/{retries}\n"
                            f"URL: {_redact_api_key(str(response.url))}\n"
                            f"HTTP status: {response.status} {response.reason}\n"
                            f"Ошибка JSON: {str(e)}\n"
                            f"Response body:\n{response_text}"
                        )
                        await _send_admin_log(error_message)
                        return None

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            # Если это не последняя попытка — ждем и пробуем еще раз
            if attempt < retries:
                await asyncio.sleep(cooldown * attempt)  # задержка растёт
                continue

            error_message = (
                f"❌ Ошибка HTTP-запроса во время выполнения функции <b>{source_name}</b>\n"
                f"(попытка {attempt}/{retries}).\n"
                f"URL: {_redact_api_key(url)}\n"
                f"Ошибка: {str(e)}"
            )
            await _send_admin_log(error_message)
            return None

        except ProviderOrderCreateError:
            raise

        except Exception as e:
            error_message = (
                f"❌ Непредвиденная ошибка при обработке запроса во время выполнения функции {source_name}\n"
                f"URL: {_redact_api_key(url)}\n"
                f"Ошибка: {str(e)}"
            )
            await _send_admin_log(error_message)
            return None


async def get_account_balance():
    method = 'balance'
    url = f'{BASE_URL}{method}&key={API_TOKEN}'
    response = await make_request(url, source_name='get_balance')
    current_balance: str = response['balance']

    return round(float(current_balance), 2)


async def get_available_categories():
    services = await _get_supported_services(source_name='get_available_services')

    categories = []
    for i in services:
        category = i['category']
        if category not in categories:
            categories.append(category)

    return categories


async def get_services_by_category(category_name):
    categories = await _get_supported_services(source_name='get_services_by_category')

    services = []
    for category in categories:
        if category['category'] == category_name:
            services.append(category)

    return services


async def get_service(service_id: int):
    services = await _get_supported_services(source_name='get_service')

    for service in services:
        _service_id = service['service']
        if _service_id == service_id:
            return service


async def _get_default_order_statuses(order_ids: dict[str, str]) -> Dict[str, dict]:
    if not order_ids:
        return {}

    method = 'status'
    provider_order_ids = ','.join(order_ids.values())
    url = f'{BASE_URL}{method}&orders={provider_order_ids}&key={API_TOKEN}'
    statuses: Dict[str, dict] = await make_request(url, source_name='get_order_statuses')
    if not statuses:
        return {}

    provider_to_backend_key = {
        provider_order_id: backend_order_key
        for backend_order_key, provider_order_id in order_ids.items()
    }

    return {
        provider_to_backend_key[str(provider_order_id)]: status
        for provider_order_id, status in statuses.items()
        if 'error' not in status and str(provider_order_id) in provider_to_backend_key
    }


async def _get_subscription_order_statuses(order_ids: dict[str, str]) -> Dict[str, dict]:
    statuses: Dict[str, dict] = {}

    for backend_order_key, provider_order_id in order_ids.items():
        params = {
            'id': provider_order_id,
            'key': API_TOKEN,
        }
        url = _build_api_url('subscriptionStatus', params)
        status = await make_request(url, source_name='get_subscription_order_status')
        if isinstance(status, dict) and 'error' not in status:
            statuses[backend_order_key] = status

    return statuses


async def get_order_statuses(order_ids: List[str]) -> Dict[str, dict]:
    return await get_order_statuses_for_order_records({str(order_id): {} for order_id in order_ids})


async def get_order_statuses_for_order_records(order_records: dict[str, dict]) -> Dict[str, dict]:
    grouped_order_ids: dict[str, dict[str, str]] = {
        DEFAULT_PROVIDER_SERVICE_TYPE: {},
        SUBSCRIPTIONS_PROVIDER_SERVICE_TYPE: {},
    }

    for backend_order_key, order_info in order_records.items():
        provider_service_type, provider_order_id = _resolve_provider_order_identity(
            str(backend_order_key),
            order_info,
        )
        grouped_order_ids.setdefault(provider_service_type, {})[str(backend_order_key)] = provider_order_id

    default_statuses = await _get_default_order_statuses(grouped_order_ids[DEFAULT_PROVIDER_SERVICE_TYPE])
    subscription_statuses = await _get_subscription_order_statuses(
        grouped_order_ids[SUBSCRIPTIONS_PROVIDER_SERVICE_TYPE]
    )

    return {**default_statuses, **subscription_statuses}


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

async def create_new_order(
        service_id: str,
        link: str,
        quantity: int,
        provider_service_type: str = DEFAULT_PROVIDER_SERVICE_TYPE,
        subscription_posts: int | None = None,
        subscription_min: int | None = None,
        subscription_max: int | None = None,
) -> str | None:
    method = 'add'
    params: dict[str, Any] = {
        'service': service_id,
        'link': link,
        'key': API_TOKEN,
    }

    if provider_service_type == SUBSCRIPTIONS_PROVIDER_SERVICE_TYPE:
        if None in (subscription_posts, subscription_min, subscription_max):
            await _send_admin_log(
                "⚠️ Не удалось создать Subscriptions заказ: не заполнены posts/min/max\n"
                f"service_id={service_id}\n"
                f"link={link}\n"
                f"posts={subscription_posts}, min={subscription_min}, max={subscription_max}"
            )
            return None

        params.update({
            'posts': subscription_posts,
            'min': subscription_min,
            'max': subscription_max,
        })
    elif provider_service_type == DEFAULT_PROVIDER_SERVICE_TYPE:
        params['quantity'] = quantity
    else:
        await _send_admin_log(
            "⚠️ Не удалось создать заказ: неизвестный provider service type\n"
            f"service_id={service_id}\n"
            f"type={provider_service_type}"
        )
        return None

    url = _build_api_url(method, params)

    response = await make_request(url, source_name='create_new_order', raise_http_error=True)

    if response is None:
        return None  # если все ретраи упали — возвращаем None, дальше решаешь как обработать

    response_order_id_key = 'id' if provider_service_type == SUBSCRIPTIONS_PROVIDER_SERVICE_TYPE else 'order'

    try:
        provider_order_id = response[response_order_id_key]
        return build_provider_order_key(provider_service_type, provider_order_id)
    except KeyError:
        formatted_body = _format_response_body(json.dumps(response, ensure_ascii=False))
        raise ProviderOrderCreateError(
            status_code=200,
            provider_message='API вернул неожиданный ответ при создании заказа',
            formatted_body=formatted_body,
            request_url_redacted=_redact_api_key(url),
            content_type='application/json',
        )

# async def main():
#     service = await get_order_statuses(['169337601'])
#     print(service)


# asyncio.run(main())



# order_ids = [70117436, 111]
# print(f'{type(get_orders_status(order_ids, 1111123))}, {get_orders_status(order_ids, 1111123)}')
