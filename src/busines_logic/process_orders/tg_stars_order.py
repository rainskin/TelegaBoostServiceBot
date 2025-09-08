from core.db import admin, orders as orders_db
from core.db.main_orders_que import orders_queue
from core.db.models.order_item import OrderItem
from enums.orders.order_status import OrderStatus


def process_tg_stars_order(order_item: OrderItem):
    print(f"Skipping non-standard service type for order {order_item.internal_order_id}")
    order_item.order_status = OrderStatus.CANCELED
    order_item.deleted = True
    orders_queue.update(order_item)
    admin.remove_order_from_execution_queue(order_item.internal_order_id)
    orders_db.remove_not_accepted_order(order_item.user_id, order_item.internal_order_id)


def calculate_price_rub(stars: int) -> int:
    """
    Рассчитывает цену в рублях, прибыль и маржу за заданное количество звёзд,
    с учётом курса доллара к рублю.
    """
    # Таблица диапазонов: (минимум звёзд, цена за 1 звезду в рублях)
    price_ranges = admin.get_tg_stars_price_ranges_in_rub()

    price_per_star = price_ranges[0][1]
    for min_stars, rub_price in price_ranges:
        if stars >= min_stars:
            price_per_star = rub_price
        else:
            break

    total_price = int(stars * price_per_star)
    print(f'Calculated price for {stars} stars: {total_price} RUB (Price per star: {price_per_star} RUB)')
    return total_price
