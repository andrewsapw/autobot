from typing import Protocol, runtime_checkable

from aiogram import Dispatcher, F
from aiogram.filters import StateFilter


@runtime_checkable
class ConditionBase(Protocol):
    def check(self):
        raise NotImplementedError

    def register(self, dispatcher: Dispatcher, state_filter: StateFilter, callback):
        raise NotImplementedError


class CallbackCondition(ConditionBase):
    """Triggers transition on inline button pressed"""

    def __init__(self, data) -> None:
        super().__init__()
        self.data = data

    def check(self):
        return F.data == self.data

    def register(self, dispatcher: Dispatcher, state_filter: StateFilter, callback):
        dispatcher.callback_query.register(callback, state_filter, self.check())


class MessageCondition(ConditionBase):
    """Triggers transition on message sent"""

    text: str

    def __init__(self, text) -> None:
        super().__init__()
        self.text = text

    def check(self):
        return F.text.regexp(self.text)

    def register(self, dispatcher: Dispatcher, state_filter: StateFilter, callback):
        dispatcher.message.register(callback, state_filter, self.check())


class ElseCondition(ConditionBase):
    """Triggers transition if no other conditions is satisfied"""

    def __init__(self, target):
        self.target = target

    def check(self):
        return lambda _: True

    def register(self, dispatcher: Dispatcher, state_filter: StateFilter, callback):
        dispatcher.callback_query.register(callback, state_filter, self.check())
        dispatcher.message.register(callback, state_filter, self.check())


class AlwaysCondition(ConditionBase):
    """Always triggers transition. Target state will be called after from state instantly"""

    def __init__(self, target):
        self.target = target

    def check(self):
        return lambda _: True

    def register(self, dispatcher: Dispatcher, state_filter: StateFilter, callback):
        dispatcher.callback_query.register(callback, state_filter, self.check())
        dispatcher.message.register(callback, state_filter, self.check())
