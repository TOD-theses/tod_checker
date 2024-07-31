"""CLI interface for tod_checker project."""

from argparse import ArgumentParser, BooleanOptionalAction
import json
from pathlib import Path

from tod_checker.checker.checker import ReplayDivergedException, TodChecker
from tod_checker.rpc.override_formatter import OverridesFormatter
from tod_checker.rpc.rpc import RPC
from tod_checker.executor.executor import TransactionExecutor
from tod_checker.state_changes.fetcher import StateChangesFetcher
from tod_checker.tx_block_mapper.tx_block_mapper import TransactionBlockMapper


def main():
    parser = ArgumentParser(description="Check if two transactions are TOD")
    parser.add_argument("tx_a", type=str, help="Hash of the first transaction")
    parser.add_argument("tx_b", type=str, help="Hash of the second transaction")
    parser.add_argument(
        "--tod-method",
        choices=("original", "adapted", "fast-fail-adapted"),
        default="adapted",
    )
    parser.add_argument(
        "--traces-dir",
        type=Path,
        help="If provided, it will additionally store VM traces in this directory",
    )
    parser.add_argument(
        "--evaluate",
        action=BooleanOptionalAction,
        help="Run in evaluation mode, reading the trace from the traces-dir rather than producing it",
    )
    parser.add_argument(
        "--provider",
        type=str,
        default="http://localhost:8124/eth",
        help="Url for the archive node RPC",
    )
    parser.add_argument(
        "--provider-type",
        default="old Erigon",
        choices=["old Erigon", "reth"],
        help="Some fine tuning for peculiarities of the providers",
    )
    args = parser.parse_args()

    tx_a, tx_b = args.tx_a, args.tx_b
    tod_method = args.tod_method

    rpc = RPC(args.provider, OverridesFormatter(args.provider_type))
    state_changes_fetcher = StateChangesFetcher(rpc)
    tx_block_mapper = TransactionBlockMapper(rpc)
    simulator = TransactionExecutor(rpc)
    checker = TodChecker(simulator, state_changes_fetcher, tx_block_mapper)

    block_a = checker.download_data_for_transaction(tx_a)
    block_b = checker.download_data_for_transaction(tx_b)
    for block in set((block_a, block_b)):
        checker.download_data_for_block(block)

    if args.evaluate:
        assert tod_method == "adapted", "Can only evaluate with --tod-method adapted"
        result = checker.is_TOD(tx_a, tx_b, tod_method, True)
        if result:
            comparison_b, comparison_a = result
            print("Transaction B differences:")
            for diff in comparison_b.differences():
                print(diff)
            print()
            print("Transaction A differences:")
            for diff in comparison_a.differences():
                print(diff)
        else:
            print("no TOD")
        quit()

    try:
        result = checker.is_TOD(tx_a, tx_b, tod_method, False)
    except ReplayDivergedException as e:
        print("Replay Diverged")
        for diff in e.comparison.differences():
            print("diverged at", diff)
        quit()

    if result:
        print("Found TOD")
        for diff in result.differences():
            print(diff)
    else:
        print("Transactions are not TOD")

    if args.traces_dir:
        traces_dir: Path = args.traces_dir
        path_normal = traces_dir / f"{tx_a}_{tx_b}.json"
        path_reverse = traces_dir / f"{tx_b}_{tx_a}.json"

        print("Creating traces")
        traces_dir.mkdir(exist_ok=True)
        traces = checker.trace_both_scenarios(tx_a, tx_b)
        trace_normal, trace_reverse, _, _ = traces

        with open(path_normal, "w") as f:
            json.dump(trace_normal, f, indent=2)
        with open(path_reverse, "w") as f:
            json.dump(trace_reverse, f, indent=2)
