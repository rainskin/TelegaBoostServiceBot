from .users import users
from .orders import orders
from .admin import admin
from .promo import promo
from .transactions import transactions

async def init():
    await promo.init()
    await transactions.init()
    await admin.init()
