from copy import deepcopy
from dataclasses import dataclass
from typing import Literal, Sequence

from tod_checker.state_changes.comparison import (
    StateChangesComparison,
    add_world_state_diffs,
    compare_state_changes,
    compare_world_state_diffs,
    to_world_state_diff,
)
from tod_checker.types.types import (
    BlockWithTransactions,
    PrePostState,
    TxData,
    WorldState,
    WorldStateDiff,
)
from tod_checker.executor.executor import TransactionExecutor
from tod_checker.state_changes.calculation import (
    overwrite_account_changes,
    undo_state_changes,
)
from tod_checker.state_changes.fetcher import StateChangesFetcher
from tod_checker.tx_block_mapper.tx_block_mapper import TransactionBlockMapper

TODMethod = Literal["original"] | Literal["adapted"] | Literal["fast-fail-adapted"]


@dataclass
class ChangesForTx:
    before_tx: Sequence[PrePostState]
    by_tx: PrePostState
    after_tx: Sequence[PrePostState]


@dataclass
class ReplayingStateOverrides:
    normal: WorldState
    reverse: WorldState


@dataclass
class TODCheckData:
    tx: TxData
    block: BlockWithTransactions
    changes: PrePostState
    overrides_normal: WorldState


@dataclass
class TODCheckResult:
    tx_a_comparison: StateChangesComparison
    """tx_a_comparison is the addition for the overall comparison"""
    tx_b_comparison: StateChangesComparison
    """tx_b_comparison is the approximation, only covering changes of tx_b"""
    overall_comparison: StateChangesComparison
    """overall_comparison compares the changes of tx_a and tx_b together"""

    def is_approximately_TOD(self):
        return len(self.tx_b_comparison.differences()) > 0

    def is_overall_TOD(self):
        return len(self.overall_comparison.differences()) > 0


class ReplayDivergedException(Exception):
    def __init__(self, comparison: StateChangesComparison, *args: object) -> None:
        super().__init__(*args)
        self.comparison = comparison


class InsufficientEtherReplayException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class TransactionFetchingException(Exception):
    def __init__(self, tx: str) -> None:
        super().__init__(f"Could not fetch transaction {tx}")


class StateChangesFetchingException(Exception):
    def __init__(self, block_number: int) -> None:
        super().__init__(f"Could not fetch state changes for block {hex(block_number)}")


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
        try:
            return self._tx_block_mapper.download_block_for_transaction(transaction)
        except Exception as e:
            raise TransactionFetchingException(transaction) from e

    def download_data_for_block(self, block_number: int) -> None:
        try:
            self._state_changes_fetcher.download_block(block_number)
        except Exception as e:
            raise StateChangesFetchingException(block_number) from e

    def is_TOD(self, tx_a_hash: str, tx_b_hash: str) -> TODCheckResult:
        """Check if two transactions are TOD w.r.t. to the approximation and overall definition."""
        a = self._prepare_data(tx_a_hash)
        b = self._prepare_data(tx_b_hash)

        changes_b_normal = self.executor.simulate_with_state_changes(
            b.tx,
            b.overrides_normal,
        )
        self._assert_not_diverging(b.tx, b.changes, changes_b_normal, b.block)

        overrides_reverse_b = deepcopy(b.overrides_normal)
        overwrite_account_changes(overrides_reverse_b, a.changes["pre"])

        _assert_enough_balance(b.tx, changes_b_normal, overrides_reverse_b)

        changes_b_reverse = self.executor.simulate_with_state_changes(
            b.tx,
            overrides_reverse_b,
        )

        self._sanity_check(a.changes, changes_b_normal, changes_b_reverse, b.tx["from"])

        changes_b_normal_no_gas_costs = deepcopy(changes_b_normal)
        changes_b_reverse_no_gas_costs = deepcopy(changes_b_reverse)
        _remove_gas_cost_changes(
            changes_b_normal_no_gas_costs, b.tx["from"], b.block["miner"]
        )
        _remove_gas_cost_changes(
            changes_b_reverse_no_gas_costs, b.tx["from"], b.block["miner"]
        )
        comparison_b = compare_state_changes(
            changes_b_normal_no_gas_costs, changes_b_reverse_no_gas_costs
        )

        # also compare changes from executing T_A after T_B
        changes_a_normal = self.executor.simulate_with_state_changes(
            a.tx,
            a.overrides_normal,
        )
        self._assert_not_diverging(a.tx, a.changes, changes_a_normal, a.block)

        overrides_reverse_a = deepcopy(a.overrides_normal)
        overwrite_account_changes(overrides_reverse_a, changes_b_reverse["post"])

        _assert_enough_balance(a.tx, changes_a_normal, overrides_reverse_a)

        changes_a_reverse = self.executor.simulate_with_state_changes(
            a.tx,
            overrides_reverse_a,
        )

        _remove_gas_cost_changes(changes_a_normal, a.tx["from"], a.block["miner"])
        _remove_gas_cost_changes(changes_a_reverse, a.tx["from"], a.block["miner"])
        _remove_gas_cost_changes(changes_b_normal, b.tx["from"], b.block["miner"])
        _remove_gas_cost_changes(changes_b_reverse, b.tx["from"], b.block["miner"])

        diff_normal = add_world_state_diffs(
            to_world_state_diff(changes_a_normal),
            to_world_state_diff(changes_b_normal),
        )
        diff_reverse = add_world_state_diffs(
            to_world_state_diff(changes_a_reverse),
            to_world_state_diff(changes_b_reverse),
        )

        comparison_a = compare_state_changes(changes_a_normal, changes_a_reverse)
        comparison_both = compare_world_state_diffs(diff_normal, diff_reverse)

        return TODCheckResult(
            tx_a_comparison=comparison_a,
            tx_b_comparison=comparison_b,
            overall_comparison=comparison_both,
        )

    def _prepare_data(self, tx_hash: str) -> TODCheckData:
        tx = self._tx_block_mapper.get_transaction(tx_hash)
        block = self._tx_block_mapper.get_block(tx["blockNumber"])
        changes = self._changes_for_tx(tx_hash)
        overrides_normal = undo_state_changes([changes.by_tx, *changes.after_tx])["pre"]

        return TODCheckData(
            tx=tx,
            block=block,
            changes=changes.by_tx,
            overrides_normal=overrides_normal,
        )

    def _assert_not_diverging(
        self,
        tx: TxData,
        original_changes: PrePostState,
        replayed_changes: PrePostState,
        block: BlockWithTransactions,
    ):
        replay_comparison = _compare_ignoring_gas_costs(
            original_changes, replayed_changes, tx["from"], block["miner"]
        )
        if replay_comparison.differences():
            raise ReplayDivergedException(
                replay_comparison,
                f"The replay of transaction {tx['hash']} is not close enough to the original",
            )

    def trace_both_scenarios(
        self, tx_a_hash: str, tx_b_hash: str
    ) -> tuple[dict, dict, dict, dict]:
        a = self._prepare_data(tx_a_hash)
        b = self._prepare_data(tx_b_hash)

        overrides_reverse_b = deepcopy(b.overrides_normal)
        overwrite_account_changes(overrides_reverse_b, a.changes["pre"])

        changes_b_reverse = self.executor.simulate_with_state_changes(
            b.tx,
            overrides_reverse_b,
        )

        overrides_reverse_a = deepcopy(a.overrides_normal)
        overwrite_account_changes(overrides_reverse_a, changes_b_reverse["post"])

        traces_normal = self.executor.simulate_with_traces(b.tx, b.overrides_normal)
        traces_reverse = self.executor.simulate_with_traces(b.tx, overrides_reverse_b)

        traces_normal_a = self.executor.simulate_with_traces(a.tx, a.overrides_normal)
        traces_reverse_a = self.executor.simulate_with_traces(a.tx, overrides_reverse_a)
        return (traces_normal, traces_reverse, traces_normal_a, traces_reverse_a)

    def first_difference_in_traces(
        self, traces_a: dict, traces_b: dict
    ) -> tuple[dict, dict] | None:
        for step_a, step_b in zip(traces_a["structLogs"], traces_b["structLogs"]):
            if step_a != step_b:
                return step_a, step_b
        return None

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


def _compare_ignoring_gas_costs(
    changes_a: PrePostState, changes_b: PrePostState, sender: str, miner: str
):
    """Ignore gas costs, as these are not correct for Erigon currently"""
    changes_a_copy = deepcopy(changes_a)
    changes_b_copy = deepcopy(changes_b)
    _remove_gas_cost_changes(changes_a_copy, sender, miner)
    _remove_gas_cost_changes(changes_b_copy, sender, miner)

    comparison = compare_state_changes(changes_a_copy, changes_b_copy)
    return comparison


def _remove_gas_cost_changes(
    changes: PrePostState | WorldStateDiff, sender: str, miner: str
):
    if miner.lower() in changes["pre"]:
        del changes["pre"][miner.lower()]["balance"]
        del changes["post"][miner.lower()]["balance"]
    if "balance" in changes["pre"][sender.lower()]:
        del changes["pre"][sender.lower()]["balance"]
        del changes["post"][sender.lower()]["balance"]


def _assert_enough_balance(tx: TxData, tx_changes: PrePostState, overrides: WorldState):
    used = _ether_used(tx, tx_changes)
    balance = _get_balance(overrides, tx["from"])
    if used > balance:
        raise InsufficientEtherReplayException(
            f'Transaction {tx["hash"]} has insufficient ether in the replay scenario (requires {used} Wei > {balance} Wei)'
        )


def _ether_used(tx: TxData, changes: PrePostState):
    return _get_balance(changes["pre"], tx["from"]) - _get_balance(
        changes["post"], tx["from"]
    )


def _get_balance(state: WorldState, addr: str) -> int:
    balance = state[addr.lower()]["balance"]  # type: ignore
    if balance == "0x":
        return 0
    return int(balance, 16)
