from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardMarkup,
)

from autobot.logger import logger
from autobot.utils.answer import answer


def construct_callback(
    send_text: str,
    node_state: str,
    reply_markup: ReplyKeyboardMarkup | InlineKeyboardMarkup | None = None,
    back_button: bool = False,
):
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
                if isinstance(reply_markup, InlineKeyboardMarkup):
                    markup = reply_markup.inline_keyboard.append([button])
                else:
                    raise ValueError(
                        "Can't set inline back button and reply buttons at the same time!"
                    )
        else:
            markup = reply_markup

        current_state = await state.get_state()
        logger.debug(f"Current state: {current_state}")
        await answer(state=state, message=data, reply_markup=markup, text=send_text)

        await state.set_state(node_state)
        logger.debug(
            f"State is set to {node_state} (prev_state is {_data['back_state']})"
        )

    callback.state_name = node_state
    return callback
