import click

from autobot.app import dispatcher, bot
from autobot.core import parse_config
from autobot import logger


@click.command()
@click.argument("config", type=click.Path(exists=True))
def main(config):
    logger.info("Parsing config...")
    parse_config(config)
    logger.info("Starting bot...D")
    dispatcher.run_polling(bot)


if __name__ == "__main__":
    main()
