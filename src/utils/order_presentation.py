import json
from enum import Enum
from html import escape
from typing import Iterator


TELEGRAM_MESSAGE_LIMIT = 4096


def saved_value(value: object) -> str:
    """Convert a Mongo-saved value to a readable text representation."""
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, default=str)
    return str(value)


def _escaped_chunks(value: str, max_length: int) -> Iterator[str]:
    """Yield HTML-escaped chunks that are each no longer than ``max_length``."""
    chunk = ''
    for character in value:
        escaped_character = escape(character)
        if chunk and len(chunk) + len(escaped_character) > max_length:
            yield chunk
            chunk = ''
        chunk += escaped_character
    yield chunk


def short_html(value: object, max_length: int = 48, empty: str = '—') -> str:
    """Escape and shorten a value while bounding its resulting HTML length."""
    if value is None or value == '':
        return empty

    chunks = _escaped_chunks(saved_value(value), max_length)
    result = next(chunks, '')
    return f'{result}…' if next(chunks, None) is not None else result


def format_order_card(order: dict[str, object]) -> list[str]:
    """Format every saved order field into Telegram-safe HTML messages."""
    messages = []
    current = '<b>Полная карточка заказа</b>'
    suffix = '</code>'

    for field, value in order.items():
        if field == '_id':
            continue
        field_name = escape(field)
        remaining = saved_value(value)
        continuation = False
        while remaining:
            label = field_name if not continuation else f'{field_name} (продолжение)'
            prefix = f'<b>{label}:</b> <code>'
            value_limit = TELEGRAM_MESSAGE_LIMIT - len(prefix) - len(suffix)
            escaped_value = next(_escaped_chunks(remaining, value_limit))
            consumed_characters = len(next(_raw_chunks(remaining, value_limit)))
            line = f'{prefix}{escaped_value}{suffix}'
            if len(current) + len(line) + 1 > TELEGRAM_MESSAGE_LIMIT:
                messages.append(current)
                current = line
            else:
                current = f'{current}\n{line}'
            remaining = remaining[consumed_characters:]
            continuation = True
        if value == '':
            line = f'<b>{field_name}:</b> <code></code>'
            if len(current) + len(line) + 1 > TELEGRAM_MESSAGE_LIMIT:
                messages.append(current)
                current = line
            else:
                current = f'{current}\n{line}'

    messages.append(current)
    return messages


def _raw_chunks(value: str, max_escaped_length: int) -> Iterator[str]:
    """Yield raw fragments constrained by their HTML-escaped length."""
    chunk = ''
    escaped_length = 0
    for character in value:
        character_length = len(escape(character))
        if chunk and escaped_length + character_length > max_escaped_length:
            yield chunk
            chunk = ''
            escaped_length = 0
        chunk += character
        escaped_length += character_length
    if chunk:
        yield chunk