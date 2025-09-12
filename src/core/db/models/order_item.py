from pydantic import BaseModel
from typing import Optional
from pydantic.dataclasses import dataclass
from enums.orders.order_status import OrderStatus
from enums.orders.service_type import ServiceType


class OrderItem(BaseModel):
    creation_date: Optional[str]
    updated_at: Optional[str]
    internal_order_id: str
    backend_order_id: Optional[int]
    user_id: int
    service_type: ServiceType
    service_id: Optional[int]
    service_name: Optional[str]
    url: str
    quantity: int
    amount_without_commission: float
    total_amount: float
    profit: float
    canceling_is_available: Optional[bool]
    order_status: OrderStatus = OrderStatus.UNPAID
    deleted: bool = False
    is_money_returned: bool = False

    def __init__(
        self,
        internal_order_id: str,
        user_id: int,
        service_type: ServiceType,
        url: str,
        quantity: int,
        amount_without_commission: float,
        total_amount: float,
        profit: float,
        creation_date: Optional[str] = None,
        updated_at: Optional[str] = None,
        backend_order_id: Optional[int] = None,
        service_id: Optional[int] = None,
        service_name: Optional[str] = None,
        canceling_is_available: Optional[bool] = None,
        order_status: OrderStatus = OrderStatus.UNPAID,
        deleted: bool = False,
        is_money_returned: bool = False,
    ):
        # передаём все аргументы в pydantic.BaseModel
        super().__init__(
            creation_date=creation_date,
            updated_at=updated_at,
            internal_order_id=internal_order_id,
            backend_order_id=backend_order_id,
            user_id=user_id,
            service_type=service_type,
            service_id=service_id,
            service_name=service_name,
            url=url,
            quantity=quantity,
            amount_without_commission=amount_without_commission,
            total_amount=total_amount,
            profit=profit,
            canceling_is_available=canceling_is_available,
            order_status=order_status,
            deleted=deleted,
            is_money_returned=is_money_returned,
        )

