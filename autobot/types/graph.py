from dataclasses import dataclass
from typing import Any, Callable, Coroutine

from aiogram.fsm.context import FSMContext
from aiogram.handlers import BaseHandler
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardMarkup,
)
from pydantic import BaseModel

from autobot import logger
from autobot.utils.answer import answer
from autobot.utils.callback import construct_callback

from .condition import ConditionBase

Callback = Callable[[Message | CallbackQuery, FSMContext], Coroutine[Any, Any, Any]]


@dataclass
class Handler(BaseHandler[Message | CallbackQuery]):
    name: str
    text: str
    back_button = None
    reply_markup = None
    node_state = None

    _data = {}

    async def handle(self) -> Any:
        data = self.data
        state = data["state"]
        message = self.event

        if "back_state" not in self._data:
            self._data["back_state"] = await state.get_state()

        if self.back_button:
            button = InlineKeyboardButton(
                text="Назад", callback_data=self._data["back_state"]
            )
            if self.reply_markup is None:
                markup = InlineKeyboardMarkup(inline_keyboard=[[button]])
            else:
                if isinstance(self.reply_markup, InlineKeyboardMarkup):
                    markup = self.reply_markup.inline_keyboard.append([button])
                else:
                    raise ValueError(
                        "Can't set inline back button and reply buttons at the same time!"
                    )
        else:
            markup = self.reply_markup

        current_state = await state.get_state()
        logger.debug(f"Current state: {current_state}")
        await answer(state=state, message=message, reply_markup=markup, text=self.text)

        await state.set_state(self.node_state)
        logger.debug(
            f"State is set to {self.node_state} (prev_state is {self._data['back_state']})"
        )


@dataclass
class State:
    name: str
    text: str
    reply_markup: ReplyKeyboardMarkup | InlineKeyboardMarkup | None

    command: str | None = None
    add_back_button: bool = False

    callback_handler: Callback | None = None
    post_call: Callback | None = None

    @property
    def callback(self) -> Callback:
        if self.callback_handler is None:
            self.callback_handler = construct_callback(
                send_text=self.text,
                reply_markup=self.reply_markup,
                node_state=self.name,
                back_button=self.add_back_button,
            )
        return self.callback_handler

    async def handle(self, data: Message | CallbackQuery, state: FSMContext):
        await self.callback(data, state)

        logger.debug(f"Post call is {self.post_call}")
        if self.post_call is not None:
            await self.post_call(data, state)

    class Config:
        arbitrary_types_allowed = True
        underscore_attrs_are_private = True


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
