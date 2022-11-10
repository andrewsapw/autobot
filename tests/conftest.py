import random
import string

import pytest

from autobot.app import G
from autobot.core.parser import parse_config


@pytest.fixture
def simple_config():
    return "examples/configs/simple.yaml"


@pytest.fixture
def graph(simple_config):
    return parse_config(G, simple_config)


@pytest.fixture
def random_word():
    return lambda N: "".join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(N)
    )
