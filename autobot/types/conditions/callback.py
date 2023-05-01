from aiogram import Dispatcher, F
from aiogram.filters import StateFilter

from autobot.types.handler import BaseHandler
from autobot.types.state import State
from .condition import ConditionBase


class CallbackCondition(ConditionBase):
    """Triggers transition on inline button pressed"""

    def __init__(self, from_state: State, to_state: State, data: str) -> None:
        self.from_state = from_state
        self.to_state = to_state
        self.data = data

    def check(self):
        return F.data == self.data

    def register(self, dispatcher: Dispatcher, handler: BaseHandler):
        state_filter = StateFilter(self.from_state.name)
        dispatcher.callback_query.register(handler, state_filter, self.check())  # type: ignore
