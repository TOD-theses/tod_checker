from typing import Sequence
from typing_extensions import override, Self

from tod_checker.currency_changes.currency_change import CURRENCY_TYPE, CurrencyChange
from tod_checker.currency_changes.events.event import CurrencyChangeEvent


class ERC777SentEvent(CurrencyChangeEvent):
    def __init__(
        self,
        sender: str,
        to: str,
        amount: int,
        token_address: str,
    ) -> None:
        super().__init__()
        self.sender = sender
        self.to = to
        self.value = amount
        self.token_address = token_address

    @override
    @staticmethod
    def signature() -> str:
        # Sent(address indexed operator,address indexed from,address indexed to,uint256 amount,bytes data,bytes operatorData)
        # https://www.4byte.directory/event-signatures/?bytes_signature=0x06b541ddaa720db2b10a4d0cdac39b8d360425fc073085fac19bc82614677987
        return "06b541ddaa720db2b10a4d0cdac39b8d360425fc073085fac19bc82614677987"

    @override
    @classmethod
    def can_decode(cls, topics: Sequence[str], data: str) -> bool:
        return len(topics) == 4 and topics[0] == cls.signature()

    @override
    @classmethod
    def decode(cls, topics: Sequence[str], data: str, storage_address: str) -> Self:
        return cls(
            topics[2][-40:], topics[3][-40:], int(data[:64], 16), storage_address
        )

    @override
    def get_currency_changes(self) -> Sequence[CurrencyChange]:
        return [
            CurrencyChange(
                type=CURRENCY_TYPE.ERC777,
                currency_identifier=self.token_address,
                owner=self.sender,
                change=-self.value,
            ),
            CurrencyChange(
                type=CURRENCY_TYPE.ERC777,
                currency_identifier=self.token_address,
                owner=self.to,
                change=self.value,
            ),
        ]


class ERC777MintedEvent(CurrencyChangeEvent):
    def __init__(
        self,
        to: str,
        amount: int,
        token_address: str,
    ) -> None:
        super().__init__()
        self.to = to
        self.value = amount
        self.token_address = token_address

    @override
    @staticmethod
    def signature() -> str:
        # Minted(address indexed operator, address indexed to, uint256 amount, bytes data, bytes operatorData)
        # https://www.4byte.directory/event-signatures/?bytes_signature=0x2fe5be0146f74c5bce36c0b80911af6c7d86ff27e89d5cfa61fc681327954e5d
        return str("0x2fe5be0146f74c5bce36c0b80911af6c7d86ff27e89d5cfa61fc681327954e5d")

    @override
    @classmethod
    def can_decode(cls, topics: Sequence[str], data: str) -> bool:
        return len(topics) == 3 and topics[0] == cls.signature()

    @override
    @classmethod
    def decode(cls, topics: Sequence[str], data: str, storage_address: str) -> Self:
        return cls(topics[2][-40:], int(data[:64], 16), storage_address)

    @override
    def get_currency_changes(self) -> Sequence[CurrencyChange]:
        return [
            CurrencyChange(
                type=CURRENCY_TYPE.ERC777,
                currency_identifier=self.token_address,
                owner=self.to,
                change=self.value,
            ),
        ]


class ERC777BurnedEvent(CurrencyChangeEvent):
    def __init__(
        self,
        to: str,
        amount: int,
        token_address: str,
    ) -> None:
        super().__init__()
        self.holder = to
        self.value = amount
        self.token_address = token_address

    @override
    @staticmethod
    def signature() -> str:
        # Minted(address indexed operator, address indexed from, uint256 amount, bytes data, bytes operatorData)
        # https://www.4byte.directory/event-signatures/?bytes_signature=0xa78a9be3a7b862d26933ad85fb11d80ef66b8f972d7cbba06621d583943a4098
        return str("0xa78a9be3a7b862d26933ad85fb11d80ef66b8f972d7cbba06621d583943a4098")

    @override
    @classmethod
    def can_decode(cls, topics: Sequence[str], data: str) -> bool:
        return len(topics) == 3 and topics[0] == cls.signature()

    @override
    @classmethod
    def decode(cls, topics: Sequence[str], data: str, storage_address: str) -> Self:
        return cls(topics[2][-40:], int(data[:64], 16), storage_address)

    @override
    def get_currency_changes(self) -> Sequence[CurrencyChange]:
        return [
            CurrencyChange(
                type=CURRENCY_TYPE.ERC777,
                currency_identifier=self.token_address,
                owner=self.holder,
                change=-self.value,
            ),
        ]
