from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

import loader
from core.db.main_orders_queue import MainOrdersQueue
from core.db.models.order_item import OrderItem
from enums.orders.order_status import OrderStatus
from enums.orders.service_type import ServiceType
from handlers.admin_panel import cmd_admin
from handlers.cmd_start import ORDER_PAYLOAD_RE
from utils.keyboards.admin import orders_page
from utils.order_presentation import TELEGRAM_MESSAGE_LIMIT, format_order_card, short_html


def _order_document() -> dict:
    return OrderItem(
        internal_order_id='42_N001',
        user_id=42,
        service_type=ServiceType.STANDARD,
        url='https://example.test',
        quantity=10,
        amount_without_commission=10.0,
        total_amount=12.5,
        profit=2.5,
        creation_date='19-07-2026 10:00:00',
    ).dict() | {'_id': 'mongo-id'}


def test_order_card_escapes_all_values_and_respects_telegram_limit():
    parts = format_order_card({
        'internal_order_id': '42_N001',
        'provider_error_message': '&' * 5000,
        'metadata': {'provider': '<provider error>'},
        'order_status': OrderStatus.PAID,
        'empty_value': '',
    })

    rendered = ''.join(parts)
    assert len(parts) > 1
    assert all(len(part) <= TELEGRAM_MESSAGE_LIMIT for part in parts)
    assert '&amp;' in rendered
    assert '&lt;provider error&gt;' in rendered
    assert 'paid' in rendered
    assert '<code></code>' in rendered


def test_order_card_handles_an_empty_document():
    assert format_order_card({}) == ['<b>Полная карточка заказа</b>']


def test_short_html_never_breaks_an_html_entity_when_truncating():
    assert short_html('&' * 10, max_length=5) == '&amp;…'


def test_only_valid_order_payloads_are_recognized():
    assert ORDER_PAYLOAD_RE.fullmatch('order_42_N001')
    assert not ORDER_PAYLOAD_RE.fullmatch('order_')
    assert not ORDER_PAYLOAD_RE.fullmatch('order_bad payload')


def test_orders_keyboard_has_correct_boundary_navigation():
    first_page = orders_page(page=1, total_pages=3).as_markup()
    middle_page = orders_page(page=2, total_pages=3).as_markup()
    last_page = orders_page(page=3, total_pages=3).as_markup()

    assert [button.callback_data for button in first_page.inline_keyboard[0]] == [
        'admin_orders_page:current', 'admin_orders_page:2'
    ]
    assert [button.callback_data for button in middle_page.inline_keyboard[0]] == [
        'admin_orders_page:1', 'admin_orders_page:current', 'admin_orders_page:3'
    ]
    assert [button.callback_data for button in last_page.inline_keyboard[0]] == [
        'admin_orders_page:2', 'admin_orders_page:current'
    ]


class _Cursor:
    def __init__(self, documents):
        self.documents = documents

    async def to_list(self, length):
        assert length == 5
        return self.documents


class _Collection:
    def __init__(self, documents):
        self.documents = documents
        self.pipeline = None

    def aggregate(self, pipeline):
        self.pipeline = pipeline
        return _Cursor(self.documents)

    async def count_documents(self, query):
        assert query == {}
        return 7


@pytest.mark.asyncio
async def test_queue_page_uses_date_sort_and_strips_mongo_id(monkeypatch):
    collection = _Collection([_order_document()])
    monkeypatch.setattr(loader, 'db', {'main_orders_queue': collection})

    orders, total = await MainOrdersQueue().get_page(page=0, page_size=5)

    assert total == 7
    assert orders[0].internal_order_id == '42_N001'
    assert collection.pipeline[0]['$addFields']['_creation_date_for_sort']['$dateFromString']['format'] == '%d-%m-%Y %H:%M:%S'
    assert collection.pipeline[2] == {'$skip': 0}
    assert collection.pipeline[4] == {'$project': {'_id': 0, '_creation_date_for_sort': 0}}


@pytest.mark.asyncio
@pytest.mark.parametrize('user_id, callback_data', [(2, 'admin_orders_page:1'), (1, 'admin_orders_page:current')])
async def test_orders_page_callback_rejects_unauthorized_or_invalid_pages(monkeypatch, user_id, callback_data):
    monkeypatch.setattr(cmd_admin.config, 'ADMIN_ID', 1)
    query = SimpleNamespace(
        from_user=SimpleNamespace(id=user_id),
        data=callback_data,
        answer=AsyncMock(),
        message=SimpleNamespace(edit_text=AsyncMock()),
    )

    await cmd_admin.show_orders_page(query)

    query.answer.assert_awaited_once()
    query.message.edit_text.assert_not_awaited()