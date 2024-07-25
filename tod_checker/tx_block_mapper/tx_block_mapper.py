from typing import Iterable
from tod_checker.rpc.rpc import RPC
from tod_checker.types.types import BlockWithTransactions, TxData


class TransactionBlockMapper:
    def __init__(self, rpc: RPC) -> None:
        self._rpc = rpc
        self._transactions_cache: dict[str, TxData] = dict()
        self._blocks_cache: dict[int, BlockWithTransactions] = dict()

    def download_blocks_for_transactions(self, transactions: Iterable[str]) -> set[int]:
        return set(self.download_block_for_transaction(tx) for tx in transactions)

    def download_block_for_transaction(self, transaction: str):
        tx = self._rpc.fetch_transaction(transaction)
        self._transactions_cache[transaction] = tx
        block = tx["blockNumber"]
        if block not in self._blocks_cache:
            self.download_block(block)

        return block

    def download_block(self, block: int):
        self._blocks_cache[block] = self._rpc.fetch_block_with_transactions(block)

    def get_transaction(self, transaction: str):
        return self._transactions_cache[transaction]

    def get_block(self, block_number: int):
        return self._blocks_cache[block_number]
