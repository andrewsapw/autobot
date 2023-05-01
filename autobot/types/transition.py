from aiogram import F
from aiogram.filters import StateFilter
from attrs import define, field

from autobot.types.conditions import (
    ConditionBase,
    AlwaysCondition,
    ElseCondition,
)
from autobot.types.state import State


@define
class Transition:
    """Transition (or edge) representation

    Attributes:
        from_state (State): source state (aka node)
        to_state (State): target state (aka node)
        conditions (list[ConditionBase]): conditions that triggers this transition

    Raises:
        TypeError: condition type not supported
    """

    from_state: str = field()
    to_state: str = field()
    conditions: list[ConditionBase]