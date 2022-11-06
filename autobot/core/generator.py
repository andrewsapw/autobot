from typing import Any, Awaitable, Callable, Coroutine
from aiogram.handlers import MessageHandler, CallbackQueryHandler, BaseHandler

from aiogram.filters.callback_data import CallbackData
from aiogram.filters.text import Text
from aiogram.filters import Filter, Command, StateFilter
from aiogram.types import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    Message,
    CallbackQuery,
    InlineKeyboardButton,
)
from aiogram.fsm.state import State
from aiogram.fsm.context import FSMContext
from aiogram import Bot, F, Dispatcher

from autobot.types.condition import ConditionBase, MessageCondition, CallbackCondition
from autobot.types.graph import State

from autobot.utils import answer
from autobot import logger


def make_state() -> State:
    raise NotImplemented


Callback = Callable[[Message | CallbackQuery, FSMContext], Awaitable[Any]]


def construct_callback(
    send_text: str,
    node_state: str,
    reply_markup: InlineKeyboardMarkup | None = None,
    back_button: bool = False,
) -> Callback:
    _data = {}

    async def callback(data: Message | CallbackQuery, state: FSMContext):
        if "back_state" not in _data:
            _data["back_state"] = await state.get_state()

        if back_button:
            button = InlineKeyboardButton(
                text="Назад", callback_data=_data["back_state"]
            )
            if reply_markup is None:
                markup = InlineKeyboardMarkup(inline_keyboard=[[button]])
            else:
                markup = reply_markup.inline_keyboard.append([button])
        else:
            markup = reply_markup
            

        current_state = await state.get_state()
        logger.debug(f"Current state: {current_state}")
        await answer(
            state=state, message=data, reply_markup=markup, text=send_text
        )

        await state.set_state(node_state)
        logger.debug(f"State is set to {node_state}")

    callback.state_name = node_state
    return callback


def construct_transitions(
    dispatcher: Dispatcher,
    conditions: list[ConditionBase],
    callback: Callable,
    from_state: str,
    back_button: bool = False,
) -> list[BaseHandler]:
    message_filters: list[Filter] = []
    callback_filters: list[Filter] = []

    state_filter = StateFilter(from_state)
    for condition in conditions:
        if isinstance(condition, MessageCondition):
            f = F.text.regexp(condition.text)
            dispatcher.message.register(callback, state_filter, f)
        elif isinstance(condition, CallbackCondition):
            f = CallbackData.filter(F.data == condition.data)
            dispatcher.callback_query.register(callback, state_filter, f)
        else:
            raise TypeError(f"Condition of type {type(condition)} is not supported")

    dispatcher.callback_query.register(callback, state_filter, f)

    handlers = []
    if message_filters:
        handlers.append(MessageHandler(callback=callback, filters=message_filters))  # type: ignore

    if callback_filters:
        handlers.append(CallbackQueryHandler(callback=callback, filters=callback_filters))  # type: ignore

    return handlers


def register_command(dispatcher: Dispatcher, command: str, callback: Callback):
    logger.debug(f"Register command {command}")
    dispatcher.message.register(callback, Command(command))


def callback_handler():
    return CallbackQueryHandler
