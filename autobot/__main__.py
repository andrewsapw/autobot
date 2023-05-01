import click
from aiogram import Bot

from networkx import DiGraph

from autobot import logger
from autobot.core.parser import parse_config
from autobot.settings import BOT_TOKEN
from autobot.core.registers import register_edge, register_state
from autobot.types import State, Transition, Graph
from autobot.types.bot import AutoBot


@click.command()
@click.argument("config", type=click.Path(exists=True))
def main(config):
    logger.info("Parsing config...")

    states, transitions = parse_config(config)
    abot = AutoBot(states=states, edges=transitions)
    abot.dispatcher.run_polling(Bot(token=BOT_TOKEN))

if __name__ == "__main__":
    main()
