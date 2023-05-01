from typing import Any, Callable, Coroutine

from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    Message,
)
from attrs import Factory, define



CallbackType = Callable[[Message | CallbackQuery, FSMContext], Coroutine[Any, Any, Any]]


@define
class Callback:
    _functions: list[CallbackType] = Factory(list)

    def add_callback(self, callback: CallbackType):
        # assert isinstance(callback, CallbackType)
        self._functions.append(callback)

    async def handle(self, message: Message | CallbackQuery, state: FSMContext):
        for callback in self._functions:
            await callback(message, state)
