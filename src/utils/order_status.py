from typing import Dict


def get_order_status_text(orders: Dict[str, dict]) -> str:
    order_ids, orders_info = [], []
    msgs = []
    for order_id, order_info in orders.items():
        order_ids.append(order_id)

        order_info_str = []
        for key, value in order_info.items():
            order_info_str.append(f'<b>{key}</b>: {value}')

        orders_info.append('\n'.join(order_info_str))

    for order_id, order_info in zip(order_ids, orders_info):
        msg = f'<b>order {order_id}</b>\n\n{order_info}'
        msgs.append(msg)

    r = '\n\n'.join(msgs)
    return r
