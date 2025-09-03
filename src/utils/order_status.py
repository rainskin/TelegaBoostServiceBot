
from typing import Dict

from core.db import orders
from core.localisation.texts import messages
from core.localisation.texts.messages import translate_status_key


def get_order_status_text(user_id: int, lang: str, _orders: Dict[str, dict]) -> str:

    internal_order_ids, backend_order_ids, orders_info = [], [], []
    msgs = []

    for backend_order_id, order_info in _orders.items():
        additional_order_info = orders.get_order_info(user_id, backend_order_id, current_orders=True)
        if not additional_order_info:
            additional_order_info = orders.get_order_info(user_id, backend_order_id, current_orders=False)

        for _key, _value in additional_order_info.items():
            order_info[_key] = _value

        backend_order_ids.append(backend_order_id)

        order_info_str = []
        for key, value in order_info.items():
            if key == 'status':
                value = messages.translate_current_order_status(value, lang)
            if key == 'charge':
                continue
            if key == 'internal_order_id':
                internal_order_ids.append(value)
            if key == 'total_amount':
                key = 'charge'
            if key in translate_status_key.keys():
                key = messages.translate_order_status_key(key, lang)
            else:
                continue
            order_info_str.append(f'<b>{key}</b>: {value}')

        orders_info.append('\n'.join(order_info_str))

    for backend_order_id, order_info in zip(internal_order_ids, orders_info):
        msg = f'<u>ORDER #{backend_order_id}</u>\n{order_info}'
        msgs.append(msg)

    r = '\n\n'.join(msgs)
    return r

