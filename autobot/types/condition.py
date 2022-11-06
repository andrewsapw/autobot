from typing import Protocol, runtime_checkable
from aiogram import F


@runtime_checkable
class ConditionBase(Protocol):
    def check(self):
        raise NotImplemented


class CallbackCondition(ConditionBase):
    def __init__(self, data) -> None:
        super().__init__()
        self.data = data

    def check(self):
        return F.data == self.data


class MessageCondition(ConditionBase):
    text: str

    def __init__(self, text) -> None:
        super().__init__()
        self.text = text

    def check(self):
        return F.text.regexp(self.text)


class ElseCondition(ConditionBase):
    def __init__(self, target):
        self.target = target

    def check(self):
        return lambda _: True


class AlwaysCondition(ConditionBase):
    def __init__(self, target):
        self.target = target

    def check(self):
        return lambda _: True
