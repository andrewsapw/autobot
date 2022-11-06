import pytest

from autobot.core import parser

def test_parser_simple():
    parser.parse_config("examples/configs/simple.yaml")
