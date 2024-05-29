from typing import Dict

from core.localisation.texts import messages


def get_order_status_text(lang: str, orders: Dict[str, dict]) -> str:
    order_ids, orders_info = [], []
    msgs = []
    for order_id, order_info in orders.items():
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
