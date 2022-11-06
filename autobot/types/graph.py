from pydantic import BaseModel
from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                            ReplyKeyboardMarkup)

from .condition import ConditionBase


class State(BaseModel):
    name: str
    text: str
    command: str | None = None
    reply_markup: ReplyKeyboardMarkup | InlineKeyboardMarkup | None
    add_back_button: bool = False

    def __call__(self):
        raise NotImplemented

    class Config:
        arbitrary_types_allowed = True


class Transition(BaseModel):
    from_state: State
    to_state: State
    conditions: list[ConditionBase]


    class Config:
        arbitrary_types_allowed = True


class Graph(BaseModel):
    states: list[State]
    transition: list[Transition]

    def plot(self):
        raise NotImplemented
