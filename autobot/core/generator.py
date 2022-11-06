from typing import Callable

from aiogram import Dispatcher, F
from aiogram.filters import Command, Filter, StateFilter
from aiogram.fsm.state import State
from aiogram.handlers import BaseHandler, CallbackQueryHandler, MessageHandler

from autobot.logger import logger
from autobot.types.condition import (
    AlwaysCondition,
    CallbackCondition,
    ConditionBase,
    MessageCondition,
)
from autobot.types.graph import State


def make_state() -> State:
    raise NotImplemented


def construct_transitions(
    dispatcher: Dispatcher,
    conditions: list[ConditionBase],
    callback: Callable,
    from_state: State,
    to_state: State,
) -> list[BaseHandler]:
    message_filters: list[Filter] = []
    callback_filters: list[Filter] = []

    state_filter = StateFilter(from_state.name)
    for condition in conditions:
        if isinstance(condition, MessageCondition):
            dispatcher.message.register(callback, state_filter, condition.check())
        elif isinstance(condition, CallbackCondition):
            dispatcher.callback_query.register(
                callback, state_filter, condition.check()
            )
        elif isinstance(condition, AlwaysCondition):
            from_state.post_call = to_state.callback
        else:
            raise TypeError(f"Condition of type {type(condition)} is not supported")

    logger.debug(f"Register back button to {from_state}")
    dispatcher.callback_query.register(
        from_state.callback, StateFilter(to_state.name), F.data == from_state.name
    )

    handlers = []
    if message_filters:
        handlers.append(MessageHandler(callback=callback, filters=message_filters))  # type: ignore

    if callback_filters:
        handlers.append(CallbackQueryHandler(callback=callback, filters=callback_filters))  # type: ignore

    return handlers


def register_command(dispatcher: Dispatcher, command: str, callback):
    logger.debug(f"Register command {command}")
    dispatcher.message.register(callback, Command(command))


def callback_handler():
    return CallbackQueryHandler
