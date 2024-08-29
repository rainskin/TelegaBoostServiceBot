async def get_amount_minus_commission(amount: float, commission: int) -> float:
    commission_factor = commission / 100
    return round(amount * (1 - commission_factor), 2)


async def get_amount_plus_commission(amount: float, commission: int) -> float:
    commission_factor = commission / 100
    return round(amount * (1 + commission_factor), 2)





