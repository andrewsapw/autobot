from typing import Sequence

from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from jinja2 import Environment

from autobot.logger import logger
from autobot.types import State
from autobot.utils.answer import answer

jinja_env = Environment()


def construct_callback(state: State, prev_states: Sequence[str] = ()):
    # message_template = jinja_env.from_string(state.text)

    async def callback(data: Message | CallbackQuery, fms_state: FSMContext):
        prev_state = await fms_state.get_state()

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

        current_state = await fms_state.get_state()
        logger.debug(f"Current state: {current_state}")

        context = await fms_state.get_data()
        text = message_template.render(context)
        await answer(state=fms_state, message=data, reply_markup=markup, text=text)

        await fms_state.set_state(state.name)
        logger.debug(f"State is set to {state}")
        

    return callback
