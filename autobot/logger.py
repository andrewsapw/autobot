import logging
import sys
from typing import Callable, Awaitable

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from loguru import logger


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists.
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

TGProcessor = Callable[[Message | CallbackQuery, FSMContext], Awaitable]
logging.getLogger("aiogram").setLevel(logging.ERROR)
