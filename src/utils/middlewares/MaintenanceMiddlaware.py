from aiogram import BaseMiddleware, types
from aiogram.types import CallbackQuery
from typing import Callable, Dict, Any

from core.db import admin


class CallbackMaintenanceMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Any],
            query: CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:

        if admin.is_maintenance_mode():
            await show_maintenance_alert_as_query_answer(query)
            return

        return await handler(query, data)


async def show_maintenance_alert_as_query_answer(query: types.CallbackQuery):
    text = ("⚠️ Сейчас это действие выполнить невозможно - система находится на техническом обслуживании.\n"
            "Примерное время работ: 10 минут.\n\n")
    await query.answer(text, show_alert=True)
