STANDARD_ORDER = {'ru': '📋 Заказ <b>{internal_order_id}</b>\n\n'
                        '<b>Услуга:</b> {service_name}\n'
                        '<b>Количество:</b> {quantity}\n'
                        '<b>Ссылка:</b> {url}\n\n'
                        '<b>Сумма заказа:</b> {total_amount:.2f} {currency}',
                  'en': "📋 Order <b>{internal_order_id}</b>\n\n"
                        "<b>Service:</b> {service_name}\n"
                        "<b>Quantity:</b> {quantity}\n"
                        "<b>Link:</b> {url}\n\n"
                        "<b>Total price:</b> {total_amount:.2f} {currency}"}

TG_STARS_ORDER = {'ru': '📋 Заказ <b>{internal_order_id}</b>\n\n'
                        '<b>Услуга:</b> {service_name}\n'
                        '<b>Количество:</b> {quantity}\n'
                        '<b>Юзернейм:</b> @{username}\n\n'
                        '<b>Сумма заказа:</b> {total_amount:.2f} {currency}',
                  'en': "📋 Order <b>{internal_order_id}</b>\n\n"
                        "<b>Service:</b> {service_name}\n"
                        "<b>Quantity:</b> {quantity}\n"
                        "<b>Username:</b> @{username}\n\n"
                        "<b>Total price:</b> {total_amount:.2f} {currency}"}
