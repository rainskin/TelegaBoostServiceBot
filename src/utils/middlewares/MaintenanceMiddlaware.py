from aiogram import BaseMiddleware, types
from aiogram.types import CallbackQuery
from typing import Callable, Dict, Any

from core.db import admin, users
from core.localisation.texts import messages


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
    user_id = query.from_user.id
    lang = users.get_user_lang(user_id)
    text = messages.maintenance_mode[lang]
    await query.answer(text, show_alert=True)
