from autobot.core import parser
from autobot.app import G


def test_parser_simple():
    g = parser.parse_config(G, "examples/configs/simple.yaml")

    assert len(g.nodes()) > 0
    assert len(g.edges()) > 0
