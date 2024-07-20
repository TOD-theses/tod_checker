"""CLI interface for tod_checker project."""

from argparse import ArgumentParser
import json
from pathlib import Path

from tod_checker.checker.checker import TodChecker
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

    print("Fetching state changes")
    checker.download_data_for_transactions([tx_a, tx_b])

    print("Simulating reverse execution")
    result = checker.is_TOD(tx_a, tx_b)

    if result:
        print("Found TOD")
        print(
            "Prestate differs at following addresses", result.pre.differing_addresses()
        )
        print(
            "Poststate differs at following addresses",
            result.post.differing_addresses(),
        )
        print(
            "Prestate differing in following types", list(result.pre.differing_types())
        )
        print(
            "Poststate differing in following types",
            list(result.post.differing_types()),
        )
    else:
        print("Transactions are not TOD")

    if args.traces_dir:
        print("Creating traces")
        traces_dir: Path = args.traces_dir
        traces_dir.mkdir(exist_ok=True)
        trace_normal, trace_reverse = checker.trace_both_scenarios(tx_a, tx_b)

        with open(traces_dir / f"{tx_a}_{tx_b}.json", "w") as f:
            json.dump(trace_normal, f, indent=2)
        with open(traces_dir / f"{tx_b}_{tx_a}.json", "w") as f:
            json.dump(trace_reverse, f, indent=2)
