import random

import pytest

from autobot.app import G
from autobot.core import parser
from autobot.types.conditions.condition import (
    AlwaysCondition,
    CallbackCondition,
    ElseCondition,
    MessageCondition,
)


@pytest.fixture
def transition_generator(random_word):
    possible_conditions = {
        "message": {"message": [r".+", r"\d+"]},
        "data": {"data": ["state1", "state2"]},
        "else": {"else": "state1"},
        "always": {"always": True},
    }

    def func(n: int, filter_name: str | None = None):
        conditions_names = list(possible_conditions.keys())
        if filter_name is not None:
            conditions_names = list(
                filter(lambda x: x == filter_name, conditions_names)
            )

        for _ in range(n):
            condition = random.choice(conditions_names)
            yield {
                "from": random_word(1),
                "to": random_word(5),
                "conditions": possible_conditions[condition],
            }

    return func


def test_parser_simple(simple_config: str):
    g = parser.parse_config(G, simple_config)

    assert len(g.nodes()) > 0
    assert len(g.edges()) > 0


def test_parse_multiple_transitions(transition_generator):
    for t in transition_generator(15):
        c = parser.parse_transitions(t)

        c_dict = t["conditions"]
        if "message" in c_dict:
            assert any([isinstance(i, MessageCondition) for i in c])
        if "data" in c_dict:
            assert any([isinstance(i, CallbackCondition) for i in c])
        if "else" in c_dict:
            assert any([isinstance(i, ElseCondition) for i in c])
        if "always" in c_dict:
            assert any([isinstance(i, AlwaysCondition) for i in c])


def test_parse_message_conditions(transition_generator):
    for t in transition_generator(10, "message"):
        c: list[MessageCondition] = parser.parse_transitions(t)  # type: ignore
        assert all([isinstance(i, MessageCondition) for i in c])
        for f, cond in zip(t["conditions"]["message"], c):
            assert f == cond.text


def test_parse_callback_conditions(transition_generator):
    for t in transition_generator(10, "data"):
        c: list[CallbackCondition] = parser.parse_transitions(t)  # type: ignore
        assert all([isinstance(i, CallbackCondition) for i in c])
        for f, cond in zip(t["conditions"]["data"], c):
            assert f == cond.data


def test_parse_else_conditions(transition_generator):
    for t in transition_generator(10, "else"):
        c: list[ElseCondition] = parser.parse_transitions(t)  # type: ignore
        assert len(c) == 1
        assert t["conditions"]["else"] == c[0].target


def test_parse_always_conditions(transition_generator):
    for t in transition_generator(10, "always"):
        c: list[AlwaysCondition] = parser.parse_transitions(t)  # type: ignore  # type: ignore
        print(t, c[0])
        assert len(c) == 1
        assert t["to"] == c[0].target
