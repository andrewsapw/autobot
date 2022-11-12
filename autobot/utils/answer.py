from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)


async def answer(
    state: FSMContext,
    message: Message | CallbackQuery,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    """Core function for handling answer functionality.

    Receives import context and tries to answer beautifully:
        - if callback event received, then try to update previous message (to keep message history clean)

    Also, keeps last message with inline keyboard in history.

    Args:
        state (FSMContext): current bot state
        message (Message | CallbackQuery): update received
        text (str): text to send to the user
        reply_markup (InlineKeyboardMarkup, optional): buttons to send with message. Defaults to None.

    Raises:
        ValueError: message is None
    """
    if isinstance(message, CallbackQuery):
        if message.message is not None:
            sent_message = await message.message.edit_text(
                text=text,
                reply_markup=reply_markup,
            )
        else:
            raise ValueError(f"Message if None")

    else:
        data = await state.get_data()
        data.get("last_query_message", None)
        sent_message = await message.answer(text=text, reply_markup=reply_markup)

    if isinstance(reply_markup, ReplyKeyboardRemove) or isinstance(
        reply_markup, ReplyKeyboardMarkup
    ):
        await state.update_data(last_query_message=None)
        return

    if reply_markup is not None and isinstance(sent_message, Message):
        await state.update_data(last_query_message=sent_message.message_id)
    else:
        await state.update_data(last_query_message=None)
