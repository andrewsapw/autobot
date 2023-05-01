from aiogram import Dispatcher
from aiogram.filters import StateFilter

from autobot.types.state import State

from .condition import ConditionBase


class ElseCondition(ConditionBase):
    """Triggers transition if no other conditions is satisfied"""

    def __init__(self, from_state: State, to_state: State):
        self.from_state = from_state
        self.to_state = to_state

    def check(self):
        return lambda _: True

    def register(self, dispatcher: Dispatcher, handler):
        state_filter = StateFilter(self.from_state.name)
        dispatcher.callback_query.register(handler, state_filter, self.check())
        dispatcher.message.register(handler, state_filter, self.check())
