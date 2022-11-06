from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    Message,
    ReplyKeyboardRemove,
    ReplyKeyboardMarkup,
)


async def answer(
    state: FSMContext, message: Message | CallbackQuery, text: str, reply_markup=None
):
    if isinstance(message, CallbackQuery):
        if message.message is not None:
            sent_message = await message.message.edit_text(
                text=text,
                reply_markup=reply_markup,
            )
        else:
            sent_message = await bot.send_message(
                chat_id=message.from_user.id, text=text, reply_markup=reply_markup
            )

    else:
        data = await state.get_data()
        data.get("last_query_message", None)

        # Удаление старой клавиатуры - пока убрал (смотрится не очень :( )

        # if last_query_message is not None and not isinstance(
        #     reply_markup, ReplyKeyboardRemove
        # ):

        #     try:
        #         await bot.edit_message_reply_markup(
        #             chat_id=message.chat.id,
        #             message_id=last_query_message,
        #             reply_markup=None,
        #         )
        #     except aiogram.exceptions.TelegramBadRequest:
        #         logger.warning(
        #             f"Ошибка при редактировании сообщения {last_query_message}"
        #         )

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
