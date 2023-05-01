from typing import Any, Sequence
from aiogram.handlers import CallbackQueryHandler, MessageHandler, BaseHandler
from aiogram.methods import SendMessage, EditMessageText
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from autobot.utils.answer import answer
from autobot.types.state import State


class AutoCallbackHandler(CallbackQueryHandler):
    async def handle(self) -> Any:
        state = self.data["state"]


class AutoMessageHandler(MessageHandler):
    _callbacks = []

    async def handle(self) -> Any:
        state: FSMContext = self.data["state"]

        for c in self._callbacks:
            await self.event.answer("Hello!")
            await self.event.answer("Hello2!")


def construct_handler(state: State, prev_states: Sequence[str] = ()):
    # message_template = jinja_env.from_string(state.text)

    class AutoHandler(BaseHandler):
        _callbacks = []
        _prev_states = []

        async def handle(self) -> None:
            fsm_state: FSMContext = self.data["state"]
            prev_state = await fsm_state.get_state()

            if state.back_button and prev_state in prev_states:
                button = InlineKeyboardButton(text="Назад", callback_data=prev_state)
                if state.reply_markup is None:
                    markup = InlineKeyboardMarkup(inline_keyboard=[[button]])
                else:
                    if isinstance(state.reply_markup, InlineKeyboardMarkup):
                        markup = state.reply_markup.inline_keyboard.append([button])
                    else:
                        raise ValueError(
                            "Can't set inline back button and reply buttons at the same time!"
                        )
            else:
                markup = state.reply_markup

            current_state = await fsm_state.get_state()
            context = await fsm_state.get_data()
            await answer(
                state=fsm_state, message=self.event, reply_markup=None, text=state.text
            )

        @classmethod
        def add_callback(cls, callback):
            cls._callbacks.append(callback)
            return cls

    return AutoHandler
