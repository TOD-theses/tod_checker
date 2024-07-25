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
        if transaction in self._transactions_cache:
            return self._transactions_cache[transaction]["blockNumber"]
        tx = self._rpc.fetch_transaction(transaction)
        block_number = tx["blockNumber"]
        if block_number not in self._blocks_cache:
            self.download_block(block_number)

        return block_number

    def download_block(self, block_number: int):
        block = self._rpc.fetch_block_with_transactions(block_number)
        self._blocks_cache[block_number] = block
        for tx in self._blocks_cache[block_number]["transactions"]:
            self._transactions_cache[tx["hash"]] = tx

    def get_transaction(self, transaction: str):
        return self._transactions_cache[transaction]

    def get_block(self, block_number: int):
        return self._blocks_cache[block_number]
