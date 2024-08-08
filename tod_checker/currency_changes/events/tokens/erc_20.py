from typing import Sequence
from typing_extensions import override, Self

from tod_checker.currency_changes.currency_change import CURRENCY_TYPE, CurrencyChange
from tod_checker.currency_changes.events.event import CurrencyChangeEvent, Event


class ERC20TransferEvent(CurrencyChangeEvent):
    def __init__(
        self,
        sender: str,
        to: str,
        value: int,
        token_address: str,
    ) -> None:
        super().__init__()
        self.sender = sender
        self.to = to
        self.value = value
        self.token_address = token_address

    @override
    @staticmethod
    def signature() -> str:
        # Transfer(address indexed _from, address indexed _to, uint256 _value)
        # https://www.4byte.directory/event-signatures/?bytes_signature=0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef
        return "ddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

    @override
    @classmethod
    def can_decode(cls, topics: Sequence[str], data: str) -> bool:
        return len(topics) == 3 and topics[0] == cls.signature()

    @override
    @classmethod
    def decode(cls, topics: Sequence[str], data: str, storage_address: str) -> Self:
        return cls(topics[1][-40:], topics[2][-40:], int(data, 16), storage_address)

    @override
    def get_currency_changes(self) -> Sequence[CurrencyChange]:
        return [
            CurrencyChange(
                type=CURRENCY_TYPE.ERC20,
                currency_identifier=self.token_address,
                owner=self.sender,
                change=-self.value,
            ),
            CurrencyChange(
                type=CURRENCY_TYPE.ERC20,
                currency_identifier=self.token_address,
                owner=self.to,
                change=self.value,
            ),
        ]


class ERC20ApprovalEvent(Event):
    def __init__(
        self,
        owner: str,
        spender: str,
        value: int,
        token_address: str,
    ) -> None:
        super().__init__()
        self.owner = owner
        self.spender = spender
        self.value = value
        self.token_address = token_address

    @override
    @staticmethod
    def signature() -> str:
        # Approval(address indexed _owner, address indexed _spender, uint256 _value)
        # https://www.4byte.directory/event-signatures/?bytes_signature=0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925
        return "8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925"

    @override
    @classmethod
    def can_decode(cls, topics: Sequence[str], data: str) -> bool:
        return len(topics) == 3 and topics[0] == cls.signature()

    @override
    @classmethod
    def decode(cls, topics: Sequence[str], data: str, storage_address: str) -> Self:
        return cls(topics[1][-40:], topics[2][-40:], int(data, 16), storage_address)
