"""CLI interface for tod_checker project."""

from argparse import ArgumentParser
import json
from pathlib import Path

from tod_checker.currency_changes.properties.erc20_approve_after_transfer import (
    check_erc20_approval_attack,
)
from tod_checker.currency_changes.properties.gain_and_loss import (
    check_gain_and_loss_properties,
)
from tod_checker.currency_changes.properties.securify import check_securify_properties
from tod_checker.currency_changes.tracer.currency_changes_js_tracer import (
    CurrencyChangesJSTracer,
)
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
    parser.add_argument(
        "--provider-type",
        default="old Erigon",
        choices=["old Erigon", "reth"],
        help="Some fine tuning for peculiarities of the providers",
    )
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    tx_a, tx_b = args.tx_a, args.tx_b
    verbose: bool = args.verbose

    rpc = RPC(args.provider, OverridesFormatter(args.provider_type))
    state_changes_fetcher = StateChangesFetcher(rpc)
    tx_block_mapper = TransactionBlockMapper(rpc)
    simulator = TransactionExecutor(rpc)
    checker = TodChecker(simulator, state_changes_fetcher, tx_block_mapper)

    block_a = checker.download_data_for_transaction(tx_a)
    block_b = checker.download_data_for_transaction(tx_b)
    for block in set((block_a, block_b)):
        checker.download_data_for_block(block)

    try:
        result = checker.check(tx_a, tx_b)
        tx_a_differences = result.tx_a_comparison.differences()
        tx_b_differences = result.tx_b_comparison.differences()
        overall_differences = result.overall_comparison.differences()
        print(f"Approximately TOD: {result.is_approximately_TOD()}")
        print(f"Overall TOD:       {result.is_overall_TOD()}")
        if verbose:
            print("Differences between the normal and reverse scenario:")
            print(f"Overall: {len(overall_differences)}")
            print(*overall_differences, sep="\n")
            print()
            print(f"Tx B: {len(tx_b_differences)}")
            print(*tx_b_differences, sep="\n")
            print()
            print(f"Tx A: {len(tx_a_differences)}")
            print(*tx_a_differences, sep="\n")
            print()

        analyzer = CurrencyChangesJSTracer()
        js_tracer, config = analyzer.get_js_tracer()
        traces = checker.js_trace_scenarios(tx_a, tx_b, js_tracer, config)
        currency_changes, events = analyzer.process_traces(traces)

        tx_a_data = tx_block_mapper.get_transaction(tx_a)
        tx_b_data = tx_block_mapper.get_transaction(tx_b)

        gain_and_loss = check_gain_and_loss_properties(
            changes_normal=[
                *currency_changes.tx_a_normal,
                *currency_changes.tx_b_normal,
            ],
            changes_reverse=[
                *currency_changes.tx_a_reverse,
                *currency_changes.tx_b_reverse,
            ],
            accounts={
                "attacker_eoa": tx_a_data["from"],
                "attacker_bot": tx_a_data["to"],
                "victim": tx_b_data["from"],
            },
        )
        print(
            "Attacker gain & victim loss:",
            gain_and_loss["properties"]["attacker_gain_and_victim_loss"],
        )
        if verbose:
            print("Sub properties:", json.dumps(gain_and_loss["properties"], indent=2))
            print("Witnesses:", json.dumps(gain_and_loss["witnesses"], indent=2))

        securify_tx_a = check_securify_properties(
            currency_changes.tx_a_normal, currency_changes.tx_a_reverse
        )
        securify_tx_b = check_securify_properties(
            currency_changes.tx_b_normal, currency_changes.tx_b_reverse
        )
        print("Securify Tx A:", securify_tx_a["properties"])
        if verbose:
            print("Witnesses:", json.dumps(securify_tx_a["witnesses"], indent=2))
        print("Securify Tx B:", securify_tx_b["properties"])
        if verbose:
            print("Witnesses:", json.dumps(securify_tx_b["witnesses"], indent=2))

        approval = check_erc20_approval_attack(events.tx_a_normal, events.tx_b_normal)
        print(
            "ERC-20 Transfer-Approval:",
            approval["properties"]["approve_after_transfer"],
        )
        if verbose:
            print(
                "Witnesses:",
                json.dumps(approval["witnesses"]["transfer_approval_pairs"], indent=2),
            )

        if args.traces_dir:
            print("Creating traces")
            traces = checker.trace_both_scenarios(tx_a, tx_b)
            trace_normal_b, trace_reverse_b, trace_normal_a, trace_reverse_a = traces

            traces_dir: Path = args.traces_dir
            print(f"Storing traces in {traces_dir}")
            traces_dir.mkdir(exist_ok=True)
            with open(traces_dir / f"{tx_b}_normal.json", "w") as f:
                json.dump(trace_normal_b, f, indent=2)
            with open(traces_dir / f"{tx_b}_reverse.json", "w") as f:
                json.dump(trace_reverse_b, f, indent=2)
            with open(traces_dir / f"{tx_a}_normal.json", "w") as f:
                json.dump(trace_normal_a, f, indent=2)
            with open(traces_dir / f"{tx_a}_reverse.json", "w") as f:
                json.dump(trace_reverse_a, f, indent=2)
    except ReplayDivergedException as e:
        print("Replay Diverged")
        print(
            "Differences between original and normal scenario (due to inaccuracies in the replaying method):"
        )
        print(*e.comparison.differences(), sep="\n")
