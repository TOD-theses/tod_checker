from typing import Sequence
from typing_extensions import Self
from abc import abstractmethod

from tod_checker.currency_changes.currency_change import CurrencyChange


class Event:
    @staticmethod
    @abstractmethod
    def signature() -> str:
        pass

    @classmethod
    @abstractmethod
    def can_decode(cls, topics: Sequence[str], data: str) -> bool:
        pass

    @classmethod
    @abstractmethod
    def decode(cls, topics: Sequence[str], data: str, storage_address: str) -> Self:
        pass


class CurrencyChangeEvent(Event):
    @abstractmethod
    def get_currency_changes(self) -> Sequence[CurrencyChange]:
        pass
