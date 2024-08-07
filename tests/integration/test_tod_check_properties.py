import pytest

from tod_checker.checker.checker import (
    TodChecker,
)
from tod_checker.currency_changes.properties.securify import check_securify_properties
from tod_checker.currency_changes.tracer.currency_changes_js_tracer import (
    CurrencyChangesJSTracer,
)
from tod_checker.executor.executor import TransactionExecutor
from tod_checker.rpc.override_formatter import OverridesFormatter
from tod_checker.rpc.rpc import RPC
from tod_checker.state_changes.fetcher import StateChangesFetcher
from tod_checker.tx_block_mapper.tx_block_mapper import TransactionBlockMapper

from snapshottest.pytest import PyTestSnapshotTest

test_provider_url = "http://localhost:8124/eth"
overrides_formatter = OverridesFormatter("old Erigon")


def _get_checker():
    rpc = RPC(test_provider_url, overrides_formatter)
    state_changes_fetcher = StateChangesFetcher(rpc)
    tx_block_mapper = TransactionBlockMapper(rpc)
    simulator = TransactionExecutor(rpc)
    return TodChecker(simulator, state_changes_fetcher, tx_block_mapper)


def _get_currency_changes(tx_a: str, tx_b: str):
    checker = _get_checker()
    block_a = checker.download_data_for_transaction(tx_a)
    block_b = checker.download_data_for_transaction(tx_b)
    for block in set((block_a, block_b)):
        checker.download_data_for_block(block)

    analyzer = CurrencyChangesJSTracer()
    js_tracer, config = analyzer.get_js_tracer()
    traces = checker.js_trace_scenarios(tx_a, tx_b, js_tracer, config)
    return analyzer.process_traces(traces)


@pytest.mark.vcr
def test_finds_TOD_Amount(snapshot: PyTestSnapshotTest):
    tx_a = "0x65df49728edca9888255b262f082c1a13beaf1dca58bcb8004920b1fbb53e86b"
    tx_b = "0xf812335569705e032f8eca9fff94d3348e29d748bd9ed4e2acd76fe54dbec42d"

    currency_changes = _get_currency_changes(tx_a, tx_b)
    securify_tx_a = check_securify_properties(
        currency_changes.tx_a_normal, currency_changes.tx_a_reverse
    )
    securify_tx_b = check_securify_properties(
        currency_changes.tx_b_normal, currency_changes.tx_b_reverse
    )

    snapshot.assert_match(securify_tx_a, "securify a")
    snapshot.assert_match(securify_tx_b, "securify b")
