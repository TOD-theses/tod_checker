from dataclasses import dataclass
from typing import Generic, Sequence, TypeVar, TypedDict

TxData = TypedDict(
    "TxData",
    {
        "accessList": Sequence[dict],
        "blobVersionedHashes": Sequence[str],
        "blockHash": str,
        "blockNumber": int,
        "chainId": int,
        "data": bytes | str,
        "from": str,
        "gas": int,
        "gasPrice": int,
        "maxFeePerBlobGas": int,
        "maxFeePerGas": int,
        "maxPriorityFeePerGas": int,
        "hash": str,
        "input": str,
        "nonce": int,
        "r": str,
        "s": str,
        "to": str,
        "transactionIndex": int,
        "type": int | str,
        "v": int,
        "value": int,
        "yParity": int,
    },
)


class BlockWithTransactions(TypedDict):
    baseFeePerGas: int
    difficulty: int
    extraData: str
    gasLimit: int
    gasUsed: int
    hash: str
    logsBloom: str
    miner: str
    mixHash: str
    nonce: str
    number: int
    parentHash: str
    receiptsRoot: str
    sha3Uncles: str
    size: int
    stateRoot: str
    timestamp: int
    totalDifficulty: int
    transactions: Sequence[TxData]
    transactionsRoot: str
    uncles: Sequence[str]
    withdrawals: Sequence[dict]
    withdrawalsRoot: str
    parentBeaconBlockRoot: str
    blobGasUsed: int
    excessBlobGas: int

    # ExtraDataToPOAMiddleware replaces extraData w/ proofOfAuthorityData
    proofOfAuthorityData: str


class AccountState(TypedDict, total=False):
    balance: str
    code: str
    nonce: int
    storage: dict[str, str]


WorldState = dict[str, AccountState]


class AccountStateDiff(TypedDict, total=False):
    balance: int
    code: int
    nonce: int
    storage: dict[str, int]


WorldStateDiff = dict[str, AccountStateDiff]


class TxPrestate(TypedDict):
    txHash: str
    result: WorldState


class PrePostState(TypedDict):
    pre: WorldState
    post: WorldState


class TxStateDiff(TypedDict):
    txHash: str
    result: PrePostState


T = TypeVar("T")


@dataclass
class TxScenarioBundle(Generic[T]):
    tx_a_normal: T
    tx_a_reverse: T
    tx_b_normal: T
    tx_b_reverse: T


@dataclass
class TxBundle(Generic[T]):
    tx_a: T
    tx_B: T


# (type, addr) or ('storage', addr, slot)
StateKey = tuple[str, str, str] | tuple[str, str]
