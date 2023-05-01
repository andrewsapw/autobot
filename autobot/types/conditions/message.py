from aiogram import Dispatcher, F
from aiogram.filters import StateFilter

from autobot.types.state import State
from .condition import ConditionBase


class MessageCondition(ConditionBase):
    """Triggers transition on message sent"""

    def __init__(self, from_state: State, to_state: State, text: str) -> None:
        self.from_state = from_state
        self.to_state = to_state
        self.text = text

    def check(self):
        return F.text.regexp(self.text)

    def register(self, dispatcher: Dispatcher, handler):
        state_filter = StateFilter(self.from_state.name)
        dispatcher.message.register(handler, state_filter, self.check())
