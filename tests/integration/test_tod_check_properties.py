import pytest

from tod_checker.checker.checker import (
    TodChecker,
)
from tod_checker.currency_changes.properties.gain_and_loss import (
    check_gain_and_loss_properties,
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
    currency_changes, _ = _get_analyzed_traces(tx_a, tx_b)
    return currency_changes


def _get_events(tx_a: str, tx_b: str):
    _, events = _get_analyzed_traces(tx_a, tx_b)
    return events


def _get_analyzed_traces(tx_a: str, tx_b: str):
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

    assert securify_tx_a["properties"]["TOD_Amount"]
    assert securify_tx_b["properties"]["TOD_Amount"]

    snapshot.assert_match(securify_tx_a, "securify a")
    snapshot.assert_match(securify_tx_b, "securify b")


@pytest.mark.vcr
def test_finds_ERC20_gains_and_losses(snapshot: PyTestSnapshotTest):
    tx_a = "0x6bfb3911273d5ff4019e2178538bc6d93c6631d81a30155790691ac6cdcd23b8"
    tx_b = "0x21398faf8d32827f6cc016e3d40f70c0096d932ada51201f66682c867ab37b01"

    currency_changes = _get_currency_changes(tx_a, tx_b)
    result = check_gain_and_loss_properties(
        changes_normal=[*currency_changes.tx_a_normal, *currency_changes.tx_b_normal],
        changes_reverse=[
            *currency_changes.tx_a_reverse,
            *currency_changes.tx_b_reverse,
        ],
        accounts={
            "attacker_eoa": "0x867DB1CE98b2Ed8cC68Ba5015b163Bbbe07d4A41",
            "attacker_bot": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
            "victim": "0x465A8228594a8437014B092f65E925bC0473e6FD",
        },
    )

    assert result["properties"]["attacker_gain_and_victim_loss"]
    snapshot.assert_match(result, "properties")


@pytest.mark.vcr
def test_finds_ERC721_gains_and_losses(snapshot: PyTestSnapshotTest):
    tx_a = "0x6f041d50130de251ad373941f35abfdda4b34238c5e1cc51f838c375c330185f"
    tx_b = "0xbc1272438dabda0641eef3cad5068a30499f257dc4d4f73b9b03921d6859ad01"

    currency_changes = _get_currency_changes(tx_a, tx_b)
    result = check_gain_and_loss_properties(
        changes_normal=[*currency_changes.tx_a_normal, *currency_changes.tx_b_normal],
        changes_reverse=[
            *currency_changes.tx_a_reverse,
            *currency_changes.tx_b_reverse,
        ],
        accounts={
            "attacker_eoa": "0xC5442AA3bFcfd998c3d1d5d197E0D8bA689cC3D8",
            "attacker_bot": "0xFB4ccb3e948FEd6946fC528bA806e737eDc938c4",
            "victim": "0x81a4E7C03c54f32D5037241e101B2D20c4984287",
        },
    )

    assert result["properties"]["attacker_gain_and_victim_loss"]
    snapshot.assert_match(result, "properties")


@pytest.mark.vcr
def test_finds_ERC777_gains_and_losses(snapshot: PyTestSnapshotTest):
    tx_a = "0x727a6dea2553b704e3d3b58b401774daac5f2a8b7b5ae960e96af69c95b2ef62"
    tx_b = "0x845e38a03adec2dc949fe47d957ace051925fbf79ec0b4dce206528cdb268db3"

    currency_changes = _get_currency_changes(tx_a, tx_b)
    result = check_gain_and_loss_properties(
        changes_normal=[*currency_changes.tx_a_normal, *currency_changes.tx_b_normal],
        changes_reverse=[
            *currency_changes.tx_a_reverse,
            *currency_changes.tx_b_reverse,
        ],
        accounts={
            "attacker_eoa": "0x26263a3432104dD51ac232269Fb01dAfa630e956",
            "attacker_bot": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
            "victim": "0x69fA4085475Eb9c0CA6df51A348f6673caD4d2EE",
        },
    )

    assert result["properties"]["attacker_gain_and_victim_loss"]
    snapshot.assert_match(result, "properties")


@pytest.mark.vcr
def test_finds_ERC1155_gains_and_losses(snapshot: PyTestSnapshotTest):
    tx_a = "0x1d77e368ff75f39b6807b164332feb428be4083159992a0b0ef03feaf076c854"
    tx_b = "0x8e5643bcc5bb98dd0be5bc6ba15b4de96de7092e5da0b2ff75c569636c188590"

    currency_changes = _get_currency_changes(tx_a, tx_b)
    result = check_gain_and_loss_properties(
        changes_normal=[*currency_changes.tx_a_normal, *currency_changes.tx_b_normal],
        changes_reverse=[
            *currency_changes.tx_a_reverse,
            *currency_changes.tx_b_reverse,
        ],
        accounts={
            "attacker_eoa": "0x7490486486eEf630d8E3eFa44a5264657E3B4bBD",
            "attacker_bot": "0xA7206d878c5c3871826DfdB42191c49B1D11F466",
            "victim": "0xAb61903EE0A18780129C345A1264D78BB39a97CD",
        },
    )

    assert result["properties"]["attacker_gain_and_victim_loss"]
    snapshot.assert_match(result, "properties")
