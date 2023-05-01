from typing import Protocol, runtime_checkable

from aiogram import Dispatcher
from aiogram.filters import StateFilter


@runtime_checkable
class ConditionBase(Protocol):
    def check(self):
        raise NotImplementedError

    def register(self, dispatcher: Dispatcher, state_filter: StateFilter, callback):
        raise NotImplementedError
