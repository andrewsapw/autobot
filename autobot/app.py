from aiogram import Bot, Dispatcher
import click
from .settings import settings, BOT_TOKEN


bot = Bot(token=BOT_TOKEN)
dispatcher = Dispatcher()

