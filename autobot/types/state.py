
from aiogram.types import InlineKeyboardMarkup
from attrs import define, field




@define(frozen=True)
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
    reply_markup: InlineKeyboardMarkup | None = field()  # buttons
    command: str | None = field(default=None)
    back_button: bool = field(default=False)

    # post_call: Callback | None = field(default=None)
    # callback: Callback | None = field(
    #     default=None
    # )  # function called when entering this state

    # async def handle(self, data: Message | CallbackQuery, state: FSMContext):
    #     """Handle bot update. Triggered on user's message or inline button trigger.

    #     Args:
    #         data (Message | CallbackQuery): update data
    #         state (FSMContext): current bot state
    #     """
    #     try:
    #         await self.callback(data, state) # type: ignore
    #     except TypeError:
    #         raise ValueError("State.callback can't be None")

    #     if self.post_call is not None:
    #         await self.post_call(data, state)