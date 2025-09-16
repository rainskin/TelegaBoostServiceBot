from enum import Enum


class OrderStatus(str, Enum):
    UNPAID = 'unpaid'
    PAID = 'paid'
    PENDING = 'pending'
    AWAITING = 'awaiting'
    IN_PROGRESS = 'in_progress'
    PARTIAL = 'partial'
    COMPLETED = 'completed'
    CANCELED = 'canceled'
    FAIL = 'fail'
