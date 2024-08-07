from typing import Sequence
from typing_extensions import override, Self
from eth_abi.abi import decode

from tod_checker.currency_changes.currency_change import CURRENCY_TYPE, CurrencyChange
from tod_checker.currency_changes.events.event import CurrencyChangeEvent


class ERC1155TransferSingleEvent(CurrencyChangeEvent):
    def __init__(
        self,
        sender: str,
        to: str,
        value: int,
        token_id: str,
        token_address: str,
    ) -> None:
        super().__init__()
        self.sender = sender
        self.to = to
        self.value = value
        self.token_id = token_id
        self.token_address = token_address

    @override
    @staticmethod
    def signature() -> str:
        # TransferSingle(address indexed _operator, address indexed _from, address indexed _to, uint256 _id, uint256 _value)
        # https://www.4byte.directory/event-signatures/?bytes_signature=0xc3d58168c5ae7397731d063d5bbf3d657854427343f4c083240f7aacaa2d0f62
        return str("0xc3d58168c5ae7397731d063d5bbf3d657854427343f4c083240f7aacaa2d0f62")

    @override
    @classmethod
    def can_decode(cls, topics: Sequence[str], data: str) -> bool:
        return len(topics) == 4 and topics[0] == cls.signature()

    @override
    @classmethod
    def decode(cls, topics: Sequence[str], data: str, storage_address: str) -> Self:
        id, value = decode(["uint256", "uint256"], bytes.fromhex(data))
        return cls(
            topics[2][-40:],
            topics[3][-40:],
            int(value, 16),
            hex(id),
            storage_address,
        )

    @override
    def get_currency_changes(self) -> Sequence[CurrencyChange]:
        id = f"{self.token_address}-{self.token_id}"
        changes = []
        if int(self.sender, 16) != 0:
            changes.append(
                CurrencyChange(
                    type=CURRENCY_TYPE.ERC1155,
                    currency_identifier=id,
                    owner=self.sender,
                    change=-self.value,
                )
            )
        if int(self.to, 16) != 0:
            changes.append(
                CurrencyChange(
                    type=CURRENCY_TYPE.ERC1155,
                    currency_identifier=id,
                    owner=self.to,
                    change=self.value,
                )
            )
        return changes


class ERC1155TransferBatchEvent(CurrencyChangeEvent):
    def __init__(
        self,
        sender: str,
        to: str,
        values: Sequence[int],
        token_ids: Sequence[str],
        token_address: str,
    ) -> None:
        super().__init__()
        self.sender = sender
        self.to = to
        self.values = values
        self.token_ids = token_ids
        self.token_address = token_address

    @override
    @staticmethod
    def signature() -> str:
        # TransferBatch(address indexed _operator, address indexed _from, address indexed _to, uint256[] _ids, uint256[] _values)
        # https://www.4byte.directory/event-signatures/?bytes_signature=0x4a39dc06d4c0dbc64b70af90fd698a233a518aa5d07e595d983b8c0526c8f7fb
        return "4a39dc06d4c0dbc64b70af90fd698a233a518aa5d07e595d983b8c0526c8f7fb"

    @override
    @classmethod
    def can_decode(cls, topics: Sequence[str], data: str) -> bool:
        return len(topics) == 4 and topics[0] == cls.signature()

    @override
    @classmethod
    def decode(cls, topics: Sequence[str], data: str, storage_address: str) -> Self:
        ids, values = decode(["uint256[]", "uint256[]"], bytes.fromhex(data))
        ids = [hex(id) for id in ids]
        values = [int(value, 16) for value in values]
        return cls(topics[2][-40:], topics[3][-40:], values, ids, storage_address)

    @override
    def get_currency_changes(self) -> Sequence[CurrencyChange]:
        changes = []
        for value, token_id in zip(self.values, self.token_ids):
            id = f"{self.token_address}-{token_id}"
            if int(self.sender, 16) != 0:
                changes.append(
                    CurrencyChange(
                        type=CURRENCY_TYPE.ERC1155,
                        currency_identifier=id,
                        owner=self.sender,
                        change=-value,
                    )
                )
            if int(self.to, 16) != 0:
                changes.append(
                    CurrencyChange(
                        type=CURRENCY_TYPE.ERC1155,
                        currency_identifier=id,
                        owner=self.to,
                        change=value,
                    )
                )
        return changes
