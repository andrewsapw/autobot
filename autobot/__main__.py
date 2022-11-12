import click

from autobot import logger
from autobot.app import G
from autobot.core.parser import parse_config


@click.command()
@click.argument("config", type=click.Path(exists=True))
def main(config):
    logger.info("Parsing config...")
    parse_config(G, config)
    logger.info("Starting bot...D")
    G.run()


if __name__ == "__main__":
    main()
