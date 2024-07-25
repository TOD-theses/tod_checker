from copy import deepcopy
from dataclasses import dataclass
from typing import Literal, Sequence

from tod_checker.state_changes.comparison import StateChangesComparison
from tod_checker.types.types import PrePostState, WorldState
from tod_checker.executor.executor import TransactionExecutor
from tod_checker.state_changes.calculation import (
    overwrite_account_changes,
    sum_state_changes,
    undo_state_changes,
)
from tod_checker.state_changes.fetcher import StateChangesFetcher
from tod_checker.tx_block_mapper.tx_block_mapper import TransactionBlockMapper


@dataclass
class ChangesForTx:
    before_tx: Sequence[PrePostState]
    by_tx: PrePostState
    after_tx: Sequence[PrePostState]


@dataclass
class ReplayingStateOverrides:
    normal: WorldState
    reverse: WorldState


class ReplayDivergedException(Exception):
    def __init__(self, comparison: StateChangesComparison, *args: object) -> None:
        super().__init__(*args)
        self.comparison = comparison


class TodChecker:
    def __init__(
        self,
        simulator: TransactionExecutor,
        state_changes_fetcher: StateChangesFetcher,
        tx_block_mapper: TransactionBlockMapper,
    ) -> None:
        self._state_changes_fetcher = state_changes_fetcher
        self._tx_block_mapper = tx_block_mapper
        self.executor = simulator

    def download_data_for_transaction(self, transaction: str) -> int:
        """Download data and return block number"""
        return self._tx_block_mapper.download_block_for_transaction(transaction)

    def download_data_for_block(self, block_number: int) -> None:
        self._state_changes_fetcher.download_block(block_number)

    def is_TOD(
        self, tx_a_hash: str, tx_b_hash: str
    ) -> Literal[False] | StateChangesComparison:
        """
        Check if two transactions are TOD.
        Return False if they are not TOD, else a comparison of the transaction-order-dependent state changes by tx_b
        """
        tx_b = self._tx_block_mapper.get_transaction(tx_b_hash)
        block_b = self._tx_block_mapper.get_block(tx_b["blockNumber"])
        changes_a = self._changes_for_tx(tx_a_hash)
        changes_b = self._changes_for_tx(tx_b_hash)

        state_overrides = self._compute_state_overrides(tx_a_hash, tx_b_hash)

        changes_b_normal = self.executor.simulate_with_state_changes(
            tx_b,
            state_overrides.normal,
        )

        replay_comparison = self._compare_ignoring_gas_costs(
            changes_b.by_tx, changes_b_normal, tx_b["from"], block_b["miner"]
        )
        if replay_comparison.differences():
            raise ReplayDivergedException(
                replay_comparison,
                "The replay of transaction b is not close enough to the original",
            )

        changes_b_reverse = self.executor.simulate_with_state_changes(
            tx_b,
            state_overrides.reverse,
        )

        self._sanity_check(
            changes_a.by_tx, changes_b_normal, changes_b_reverse, tx_b["from"]
        )

        comparison = StateChangesComparison(changes_b_normal, changes_b_reverse)

        if not comparison.differences():
            return False
        return comparison

    def _compare_ignoring_gas_costs(
        self, changes_a: PrePostState, changes_b: PrePostState, sender: str, miner: str
    ):
        changes_a_copy = deepcopy(changes_a)
        changes_b_copy = deepcopy(changes_b)
        del changes_a_copy["pre"][miner.lower()]["balance"]
        del changes_b_copy["pre"][miner.lower()]["balance"]
        del changes_a_copy["pre"][sender.lower()]["balance"]
        del changes_b_copy["pre"][sender.lower()]["balance"]
        del changes_a_copy["post"][miner.lower()]["balance"]
        del changes_b_copy["post"][miner.lower()]["balance"]
        del changes_a_copy["post"][sender.lower()]["balance"]
        del changes_b_copy["post"][sender.lower()]["balance"]

        comparison = StateChangesComparison(changes_a_copy, changes_b_copy)
        return comparison

    def trace_both_scenarios(self, tx_a_hash: str, tx_b_hash: str) -> tuple[dict, dict]:
        tx_b = self._tx_block_mapper.get_transaction(tx_b_hash)
        state_overrides = self._compute_state_overrides(tx_a_hash, tx_b_hash)

        traces_normal = self.executor.simulate_with_traces(tx_b, state_overrides.normal)
        traces_reverse = self.executor.simulate_with_traces(
            tx_b, state_overrides.reverse
        )

        return (traces_normal, traces_reverse)

    def first_difference_in_traces(
        self, traces_a: dict, traces_b: dict
    ) -> tuple[dict, dict] | None:
        for step_a, step_b in zip(traces_a["structLogs"], traces_b["structLogs"]):
            if step_a != step_b:
                return step_a, step_b
        return None

    def _compute_state_overrides(
        self, tx_a_hash: str, tx_b_hash: str
    ) -> ReplayingStateOverrides:
        changes_a = self._changes_for_tx(tx_a_hash)
        changes_b = self._changes_for_tx(tx_b_hash)

        block_reverting_changes = undo_state_changes(
            [*changes_b.before_tx, changes_b.by_tx, *changes_b.after_tx]
        )["pre"]
        changes_up_to_b = sum_state_changes(changes_b.before_tx)["post"]

        state_overrides_normal = block_reverting_changes
        overwrite_account_changes(state_overrides_normal, changes_up_to_b)

        state_overrides_reverse = deepcopy(state_overrides_normal)
        overwrite_account_changes(state_overrides_reverse, changes_a.by_tx["pre"])

        return ReplayingStateOverrides(state_overrides_normal, state_overrides_reverse)

    def _changes_for_tx(self, tx_hash: str) -> ChangesForTx:
        tx = self._tx_block_mapper.get_transaction(tx_hash)
        block_changes = self._state_changes_fetcher.get(tx["blockNumber"])

        return ChangesForTx(
            before_tx=block_changes[: tx["transactionIndex"]],
            by_tx=block_changes[tx["transactionIndex"]],
            after_tx=block_changes[tx["transactionIndex"] + 1 :],
        )

    def _sanity_check(
        self,
        change_a_normal: PrePostState,
        change_b_normal: PrePostState,
        change_b_reverse: PrePostState,
        tx_b_sender: str,
    ):
        """Sanity checks for the correctness of the state changes. These should never fail."""
        tx_b_sender = tx_b_sender.lower()
        assert (
            tx_b_sender in change_b_normal["pre"]
        ), "Sender of tx B was not included in its normal change set"
        assert (
            tx_b_sender in change_b_reverse["pre"]
        ), "Sender of tx B was not included in its reverse change set"

        assert (
            change_b_normal["pre"][tx_b_sender].get("nonce")
            == change_b_reverse["pre"][tx_b_sender].get("nonce")
        ), f"Nonce of the tx B sender was different in the executions {change_b_normal['pre'][tx_b_sender]['nonce']} (expected) vs {change_b_reverse['pre'][tx_b_sender]['nonce']} (reverse)"  # type: ignore

        # check that prestates are equal; exclude those modified by tx a
        common_addresses = set(change_b_normal["pre"]) & set(change_b_reverse["pre"])
        unmodified_common_addresses = common_addresses - set(change_a_normal["pre"])

        for addr in unmodified_common_addresses:
            for key in set(change_b_normal["pre"][addr]) & set(
                change_b_reverse["pre"][addr]
            ):
                val_normal = change_b_normal["pre"][addr][key]
                val_reverse = change_b_reverse["pre"][addr][key]
                if isinstance(val_normal, dict):
                    for slot in set(val_normal) & set(val_reverse):
                        assert (
                            val_normal[slot] == val_reverse[slot]
                        ), f"Differing storage prestate at {addr}: {slot}: {val_normal[slot]} vs {val_reverse[slot]}"
                else:
                    assert (
                        val_normal == val_reverse
                    ), f"Differing {key} prestate at {addr}: {val_normal} vs {val_reverse}"
