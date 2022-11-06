from typing import Protocol, runtime_checkable


@runtime_checkable
class ConditionBase(Protocol):
    def check(self):
        raise NotImplemented


class CallbackCondition(ConditionBase):
    def __init__(self, data) -> None:
        super().__init__()
        self.data = data


class MessageCondition(ConditionBase):
    text: str

    def __init__(self, text) -> None:
        super().__init__()
        self.text = text
