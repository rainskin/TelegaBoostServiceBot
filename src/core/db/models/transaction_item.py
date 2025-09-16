from datetime import datetime

from pydantic import BaseModel
from typing import Optional
from pydantic.dataclasses import dataclass
from enums.orders.order_status import OrderStatus
from enums.orders.service_type import ServiceType
from enums.transaction_type import TransactionType


class TransactionItem(BaseModel):
    user_id: int
    transaction_type: TransactionType
    amount: float
    currency: str
    balance_after: float
    timestamp: Optional[datetime]
    meta: dict

    def __init__(
        self,
        user_id: int,
        transaction_type: TransactionType,
        amount: float,
        balance_after: float,
        timestamp: datetime = None,
        currency: str = 'RUB',
        meta: dict = None,
    ):
        # передаём все аргументы в pydantic.BaseModel
        super().__init__(
            user_id=user_id,
            transaction_type=transaction_type,
            amount=amount,
            currency=currency,
            balance_after=balance_after,
            timestamp=timestamp,
            meta=meta or {},
        )

