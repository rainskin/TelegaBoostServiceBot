from unittest.mock import AsyncMock, patch, MagicMock, ANY

import pytest
from aiogram.types import CallbackQuery
from aiogram.types import Message, User, SuccessfulPayment

from core.localisation.texts import messages
from handlers.payment_processing.from_telegram_stars import handle_payment, successful_payment_handler, template # поправь путь и имя
from utils.currencies import telegram_stars

pytestmark = pytest.mark.asyncio  # включаем для всех тестов в модуле


async def test_stars_callback_creates_payment():
    # Настраиваем данные
    mock_user_id = 42
    amount = 100.0
    amount_with_commission = 105.0
    amount_in_starts = await telegram_stars.convert_to_stars(amount)  # пусть ваша реализация

    # Мокаем CallbackQuery
    query = MagicMock(spec=CallbackQuery)
    query.from_user = User(id=mock_user_id, is_bot=False, first_name="A")
    query.message = MagicMock(spec=Message)
    query.data = 'payment_method_telegram_stars'

    # Мокаем хранилища и функции
    fake_data = {'amount': amount, 'amount_with_commission': amount_with_commission}
    with patch('handlers.payment_processing.from_telegram_stars.storage.get_data', return_value=fake_data), \
            patch('handlers.payment_processing.from_telegram_stars.users.get_user_lang', return_value='ru'), \
            patch('handlers.payment_processing.from_telegram_stars.get_internal_order_id', new=AsyncMock(return_value=123)), \
            patch('handlers.payment_processing.from_telegram_stars.send_invoice',
                  new=AsyncMock(return_value=MagicMock(message_id=999))), \
            patch('handlers.payment_processing.from_telegram_stars.admin.save_payment') as mock_save, \
            patch.object(query, 'answer', new=AsyncMock()) as mock_answer, \
            patch.object(query.message, 'delete', new=AsyncMock()) as mock_delete:
        # Выполняем хендлер
        await handle_payment(query)

        # Проверяем вызовы
        mock_save.assert_called_once()
        pid, info = mock_save.call_args[0]
        assert pid == 'S123'
        assert info['amount_rub'] == amount_with_commission
        assert info['amount_original'] == amount_in_starts
        assert info['currency'] == 'XTR'
        assert info['payment_url'] == 999

        mock_answer.assert_awaited_once()
        mock_delete.assert_awaited_once()



async def test_successful_payment_handler_flow():
    # 1️⃣ Настройка окружения
    mock_user_id = 42
    mock_payment_id = 'S123'
    mock_amount_rub = 105.0
    mock_charge_id = 'tg_ch_456'
    lang = 'ru'

    # Формируем объект успешной оплаты
    payment = SuccessfulPayment(
        currency='XTR',
        total_amount=int(mock_amount_rub * 100),  # сумма в копейках
        invoice_payload=template + mock_payment_id,
        telegram_payment_charge_id=mock_charge_id,
        provider_payment_charge_id='prov_789'
    )
    msg = MagicMock(spec=Message)
    msg.from_user = User(id=mock_user_id, is_bot=False, first_name='User')
    msg.successful_payment = payment
    msg.text = 'Оплата прошла'

    # Мокаем возвращаемые данные из storage/admin
    payment_info = {'payment_url': '999', 'amount_rub': mock_amount_rub}

    with patch('handlers.payment_processing.from_telegram_stars.admin.get_payment_info',
               return_value=payment_info) as mock_get_info, \
         patch('handlers.payment_processing.from_telegram_stars.users.get_user_lang',
               return_value='ru'), \
         patch('handlers.payment_processing.from_telegram_stars.add_balance', new=AsyncMock()) as mock_add_balance, \
         patch('handlers.payment_processing.from_telegram_stars.admin.update_payment_status') as mock_update_status, \
         patch('handlers.payment_processing.from_telegram_stars.admin.move_to_successful_payments') as mock_move, \
         patch('handlers.payment_processing.from_telegram_stars.return_to_menu', new=AsyncMock()) as mock_return, \
         patch('handlers.payment_processing.from_telegram_stars.bot.delete_message', new=AsyncMock()) as mock_delete, \
         patch.object(msg, 'answer', new=AsyncMock()) as mock_answer:

        # 2️⃣ Выполнение тестируемого хендлера
        await successful_payment_handler(msg, state=AsyncMock())

        # 3️⃣ Проверки
        mock_get_info.assert_called_once_with(mock_payment_id)
        mock_add_balance.assert_awaited_once_with(mock_user_id, mock_amount_rub)
        mock_update_status.assert_called_once_with(mock_payment_id, 'successful', mock_charge_id)
        mock_move.assert_called_once_with(mock_payment_id)

        formatted_amount = f'{mock_amount_rub:.2f}'  # форматируем сумму
        msg_text = messages.balance_recharge_successfully_paid[lang].format(amount=formatted_amount, currency='RUB')
        mock_answer.assert_awaited_once_with(msg_text, message_effect_id='5104841245755180586')
        mock_return.assert_awaited_once_with(mock_user_id, ANY)
        mock_delete.assert_awaited_once_with(mock_user_id, int(payment_info['payment_url']))