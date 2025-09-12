from loader import dp
from utils.middlewares.MaintenanceMiddlaware import CallbackMaintenanceMiddleware


def setup():
    dp.callback_query.middleware(CallbackMaintenanceMiddleware())
