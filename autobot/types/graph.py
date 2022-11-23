from typing import Any, Callable, Coroutine

import networkx as nx
from aiogram import Dispatcher, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardMarkup,
)
from attrs import define, field

from autobot import logger
from autobot.types.condition import AlwaysCondition, ConditionBase, ElseCondition
from autobot.utils.answer import answer

Callback = Callable[[Message | CallbackQuery, FSMContext], Coroutine[Any, Any, Any]]


@define
class State:
    """State representation

    Attributes:
        name (str): state name + node name in network graph
        text (str): text of the message bot will send when entering this state
        reply_markup (ReplyKeyboardMarkup | InlineKeyboardMarkup | None): buttons markup. See aiogram [documentation](https://docs.aiogram.dev/en/dev-3.x/api/types/inline_keyboard_button.html)
        command (str, optional): command that will trigger state (for example: `start`)
        post_call (Callback, optional): awaitable function. Will be called after this state callback execution
        callback (Callback): awaitable function. Automatically build from state info.
    """

    name: str = field()
    text: str = field()
    reply_markup: ReplyKeyboardMarkup | InlineKeyboardMarkup | None = field()  # buttons
    has_back_button: bool = field(default=False)
    command: str | None = field(default=None)

    post_call: Callback | None = field(default=None)
    callback: Callback = field(init=False)  # function called when entering this state
    in_states = field(factory=list)

    back_buttons = field(factory=dict)
    last_back_button = field(factory=dict)

    def add_in_state(self, state: "State"):
        self.in_states.append(state.name)
        return self

    def build_markup(self, prev_state: str):
        if not self.has_back_button:
            return self.reply_markup

        if prev_state in self.in_states:
            # if previous state is one of the predecessors
            # then make back button from previous state and add it to self.back_buttons
            button = InlineKeyboardButton(text="Назад", callback_data=prev_state)
            self.back_buttons[prev_state] = button
            self.last_back_button = button
        elif prev_state in self.back_buttons:
            button = self.back_buttons[prev_state]
            self.last_back_button = button
        else:
            button = self.last_back_button

        if self.reply_markup is None:
            markup = InlineKeyboardMarkup(inline_keyboard=[[button]])
        elif isinstance(self.reply_markup, InlineKeyboardMarkup):
            markup = self.reply_markup.inline_keyboard.append([button])
        else:
            raise ValueError(
                "Can't set inline back button and reply buttons at the same time!"
            )

        return markup

    async def callback(self, data: Message | CallbackQuery, state: FSMContext):
        prev_state = await state.get_state()

        # adding back button to self.reply_markup if needed
        markup = self.build_markup(prev_state=prev_state)

        # store message
        if isinstance(data, Message) and prev_state is not None:
            text = data.text
            await state.update_data({prev_state: text})

        current_state = await state.get_state()
        logger.debug(f"Current state: {current_state}")

        await answer(state=state, message=data, reply_markup=markup, text=self.text)
        await state.set_state(self.name)

        logger.debug(f"State is set to {self.name} (prev_state is {prev_state})")

    async def handle(self, data: Message | CallbackQuery, state: FSMContext):
        """Handle bot update. Triggered on user's message or inline button trigger.

        Args:
            data (Message | CallbackQuery): update data
            state (FSMContext): current bot state
        """
        await self.callback(data, state)
        if self.post_call is not None:
            await self.post_call(data, state)

    def register(self, dispatcher: Dispatcher):
        """Register state. Initializes command trigger.

        Args:
            dispatcher (Dispatcher): aiogram dispatcher
        """
        if self.command is not None:
            self.register_command(
                dispatcher=dispatcher, command=self.command, callback=self.callback
            )

    def register_command(self, dispatcher: Dispatcher, command: str, callback):
        """Register command trigger"""
        logger.debug(f"Register command {command}")
        dispatcher.message.register(callback, Command(command))


@define
class Transition:
    """Transition (or edge) representation

    Attributes:
        from_state (State): source state (aka node)
        to_state (State): target state (aka node)
        conditions (list[ConditionBase]): conditions that triggers this transition

    Raises:
        TypeError: condition type not supported
    """

    from_state: State
    to_state: State
    conditions: list[ConditionBase]

    def register(self, G: nx.DiGraph, dispatcher: Dispatcher):
        """Register transition in graph structure

        Args:
            G (nx.DiGraph): _description_
            dispatcher (Dispatcher): _description_

        Raises:
            TypeError: condition type is not supported
        """
        from_state = self.from_state
        to_state = self.to_state

        state_filter = StateFilter(from_state.name)
        for condition in self.conditions:
            if isinstance(condition, (ElseCondition, AlwaysCondition)):
                target = condition.target
                target_callback = G.nodes[target]["data"].handle
                condition.register(
                    dispatcher=dispatcher,
                    state_filter=state_filter,
                    callback=target_callback,
                )
                if isinstance(condition, AlwaysCondition):
                    from_state.post_call = target_callback
                    G.nodes[self.from_state.name]["data"] = from_state
            elif isinstance(condition, ConditionBase):
                condition.register(
                    dispatcher=dispatcher,
                    state_filter=state_filter,
                    callback=to_state.handle,
                )
            else:
                raise TypeError(f"Condition type {type(condition)} is not supported")

        # register possible back button
        dispatcher.callback_query.register(
            from_state.callback, StateFilter(to_state.name), F.data == from_state.name
        )
