from typing import Dict

from core.db import orders
from core.localisation.texts import messages


def get_order_status_text(user_id: int, lang: str, _orders: Dict[str, dict], current_orders=False) -> str:

    order_ids, orders_info = [], []
    msgs = []

    for order_id, order_info in _orders.items():
        additional_order_info = orders.get_order_info(user_id, order_id, current_orders)

        for _key, _value in additional_order_info.items():
            order_info[_key] = _value

        order_ids.append(order_id)

        order_info_str = []
        for key, value in order_info.items():
            if key == 'status':
                value = messages.translate_current_order_status(value, lang)
            key = messages.translate_order_status_key(key, lang)

            order_info_str.append(f'<b>{key}</b>: {value}')

        orders_info.append('\n'.join(order_info_str))

    for order_id, order_info in zip(order_ids, orders_info):
        msg = f'<u>ORDER #{order_id}</u>\n{order_info}'
        msgs.append(msg)

    r = '\n\n'.join(msgs)
    return r
