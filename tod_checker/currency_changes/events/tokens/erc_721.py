from typing import Sequence
from typing_extensions import override, Self

from tod_checker.currency_changes.currency_change import CURRENCY_TYPE, CurrencyChange
from tod_checker.currency_changes.events.event import CurrencyChangeEvent


class ERC721TransferEvent(CurrencyChangeEvent):
    def __init__(
        self,
        sender: str,
        to: str,
        token_id: str,
        token_address: str,
    ) -> None:
        super().__init__()
        self.sender = sender
        self.to = to
        self.token_id = token_id
        self.token_address = token_address

    @override
    @staticmethod
    def signature() -> str:
        # Transfer(address indexed _from, address indexed _to, uint256 indexed _tokenId)
        # https://www.4byte.directory/event-signatures/?bytes_signature=0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef
        return "ddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

    @override
    @classmethod
    def can_decode(cls, topics: Sequence[str], data: str) -> bool:
        return len(topics) == 4 and topics[0] == cls.signature()

    @override
    @classmethod
    def decode(cls, topics: Sequence[str], data: str, storage_address: str) -> Self:
        return cls(topics[1][-40:], topics[2][-40:], topics[3], storage_address)

    @override
    def get_currency_changes(self) -> Sequence[CurrencyChange]:
        id = f"{self.token_address}-{self.token_id}"
        return [
            CurrencyChange(
                type=CURRENCY_TYPE.ERC721,
                currency_identifier=id,
                owner=self.sender,
                change=-1,
            ),
            CurrencyChange(
                type=CURRENCY_TYPE.ERC721,
                currency_identifier=id,
                owner=self.to,
                change=1,
            ),
        ]
