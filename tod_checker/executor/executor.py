from tod_checker.rpc.rpc import RPC
from tod_checker.rpc.state_diff_utils import (
    state_diff_fill_implicit_fields,
    state_diff_remove_unchanged_fields,
)
from tod_checker.rpc.types import PrePostState, TxData, WorldState


class TransactionExecutor:
    def __init__(self, rpc: RPC) -> None:
        self._rpc = rpc

    def simulate_with_state_changes(
        self, tx: TxData, state_overrides: WorldState
    ) -> PrePostState:
        state_diffs = self._rpc.debug_trace_call_state_diffs(
            tx,
            tx["blockNumber"],
            state_overrides,
            {"number": hex(tx["blockNumber"])},
            "state_diff",
        )
        state_diff_fill_implicit_fields(state_diffs)
        state_diff_remove_unchanged_fields(state_diffs)
        return state_diffs

    def simulate_with_traces(self, tx: TxData, state_overrides: WorldState) -> dict:
        return self._rpc.debug_trace_call_state_diffs(  # type: ignore
            tx,
            tx["blockNumber"],
            state_overrides,
            {"number": hex(tx["blockNumber"])},
            "vmTrace",
        )

    def replay_with_traces(self, tx_hash: str) -> dict:
        print("Replaying", tx_hash)
        return self._rpc.debug_trace_transaction(tx_hash)
