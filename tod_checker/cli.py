"""CLI interface for tod_checker project."""

from argparse import ArgumentParser, BooleanOptionalAction
import json
from pathlib import Path

from tod_checker.checker.checker import ReplayDivergedException, TodChecker
from tod_checker.rpc.rpc import RPC
from tod_checker.executor.executor import TransactionExecutor
from tod_checker.state_changes.fetcher import StateChangesFetcher
from tod_checker.tx_block_mapper.tx_block_mapper import TransactionBlockMapper


def main():
    parser = ArgumentParser(description="Check if two transactions are TOD")
    parser.add_argument("tx_a", type=str, help="Hash of the first transaction")
    parser.add_argument("tx_b", type=str, help="Hash of the second transaction")
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
    args = parser.parse_args()

    tx_a, tx_b = args.tx_a, args.tx_b

    print(f"Checking {tx_a} -> ... -> {tx_b} for TOD")

    rpc = RPC(args.provider)
    state_changes_fetcher = StateChangesFetcher(rpc)
    tx_block_mapper = TransactionBlockMapper(rpc)
    simulator = TransactionExecutor(rpc)
    checker = TodChecker(simulator, state_changes_fetcher, tx_block_mapper)

    block_a = checker.download_data_for_transaction(tx_a)
    block_b = checker.download_data_for_transaction(tx_b)
    for block in set((block_a, block_b)):
        checker.download_data_for_block(block)

    try:
        result = checker.is_TOD(tx_a, tx_b)
    except ReplayDivergedException as e:
        print("Replay Diverged")
        for diff in e.comparison.differences():
            print(diff)
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

        if args.evaluate:
            with open(path_normal) as f_normal, open(path_reverse) as f_reverse:
                trace_normal = json.load(f_normal)
                trace_reverse = json.load(f_reverse)
                first_diff_step = checker.first_difference_in_traces(
                    trace_normal, trace_reverse
                )
                if first_diff_step:
                    step_a, step_b = first_diff_step
                    print(f'Traces differ at {step_a["op"]}!')
                    for key in set(step_a) | set(step_b):
                        if step_a.get(key) != step_b.get(key):
                            if key == "storage":
                                storage_a = step_a.get(key, {})
                                storage_b = step_b.get(key, {})
                                for slot in set(storage_a) | set(storage_b):
                                    if storage_a.get(slot) != storage_b.get(slot):
                                        print(
                                            f"storage@{slot}",
                                            storage_a.get(slot),
                                            storage_b.get(slot),
                                        )
                            else:
                                print(key, step_a.get(key), step_b.get(key))
                else:
                    print("Traces are equal!")
        else:
            print("Creating traces")
            traces_dir.mkdir(exist_ok=True)
            trace_normal, trace_reverse = checker.trace_both_scenarios(tx_a, tx_b)

            with open(path_normal, "w") as f:
                json.dump(trace_normal, f, indent=2)
            with open(path_reverse, "w") as f:
                json.dump(trace_reverse, f, indent=2)
