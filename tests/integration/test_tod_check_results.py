import pytest

from tod_checker.checker.checker import (
    InsufficientEtherReplayException,
    ReplayDivergedException,
    TodChecker,
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


@pytest.mark.vcr
def test_finds_TOD(snapshot: PyTestSnapshotTest):
    tx_a = "0x0001e7b0bcf0c41941c5d53c8636139565456343e8fad9bc86609329e63cb350"
    tx_b = "0xa3cc046ea030d51a16ee32514650f82ea9e41d1270ec2c1a749e5087b1fde4ce"

    checker = _get_checker()
    block_a = checker.download_data_for_transaction(tx_a)
    block_b = checker.download_data_for_transaction(tx_b)
    for block in set((block_a, block_b)):
        checker.download_data_for_block(block)
    result = checker.is_TOD(tx_a, tx_b, "original", False)

    assert result is not False

    snapshot.assert_match(result.differences(), "differences")


@pytest.mark.vcr
def test_finds_TOD_adapted_definition(snapshot: PyTestSnapshotTest):
    tx_a = "0x0001e7b0bcf0c41941c5d53c8636139565456343e8fad9bc86609329e63cb350"
    tx_b = "0xa3cc046ea030d51a16ee32514650f82ea9e41d1270ec2c1a749e5087b1fde4ce"

    checker = _get_checker()
    block_a = checker.download_data_for_transaction(tx_a)
    block_b = checker.download_data_for_transaction(tx_b)
    for block in set((block_a, block_b)):
        checker.download_data_for_block(block)
    result = checker.is_TOD(tx_a, tx_b, "adapted", False)

    assert result is not False

    snapshot.assert_match(result.differences(), "differences")


@pytest.mark.vcr
def test_non_TOD_fail_fast(snapshot: PyTestSnapshotTest):
    tx_a = "0x000a3e22cc7b60cc63cf5edb85d5f09010b37a59ee4188b9888a7113d36e7e17"
    tx_b = "0x2e86626089b30f0d89bac6c6c0c90423ebfc15657c38c62183cafe29b7f9d478"

    checker = _get_checker()
    block_a = checker.download_data_for_transaction(tx_a)
    block_b = checker.download_data_for_transaction(tx_b)
    for block in set((block_a, block_b)):
        checker.download_data_for_block(block)
    result = checker.is_TOD(tx_a, tx_b, "fast-fail-adapted", False)

    assert result is False


@pytest.mark.vcr
def test_replay_diverges(snapshot: PyTestSnapshotTest):
    tx_a = "0xcab686b06d64de0fc5dc5b86fd634e377f57a837c1e63d0d1431ea69b622ce4d"
    tx_b = "0x2302452ea583716d83a13f9f522f2ed5c098448fb9ee1abf7fced20932c4972b"

    checker = _get_checker()
    block_a = checker.download_data_for_transaction(tx_a)
    block_b = checker.download_data_for_transaction(tx_b)
    for block in set((block_a, block_b)):
        checker.download_data_for_block(block)

    with pytest.raises(ReplayDivergedException):
        checker.is_TOD(tx_a, tx_b, "original", False)


@pytest.mark.vcr
def test_insufficient_ether_in_replay(snapshot: PyTestSnapshotTest):
    tx_a = "0x009a4a436e300ebf4857126acb7599d7cc093c832ae9deb38dc3efcb69c2c995"
    tx_b = "0x61a9a98fb61ad14360f71a4702ff920863da7c67e2c0e9392f138500b867228d"

    checker = _get_checker()
    block_a = checker.download_data_for_transaction(tx_a)
    block_b = checker.download_data_for_transaction(tx_b)
    for block in set((block_a, block_b)):
        checker.download_data_for_block(block)

    with pytest.raises(InsufficientEtherReplayException):
        checker.is_TOD(tx_a, tx_b, "original", False)


@pytest.mark.vcr
def test_finds_non_TOD(snapshot: PyTestSnapshotTest):
    tx_a = "0x0001e7b0bcf0c41941c5d53c8636139565456343e8fad9bc86609329e63cb350"
    tx_b = "0x866bf65489b0839eecfa313a60415e4f581786fbba1257c90e4f7ded97f74dd7"

    checker = _get_checker()
    block_a = checker.download_data_for_transaction(tx_a)
    block_b = checker.download_data_for_transaction(tx_b)
    for block in set((block_a, block_b)):
        checker.download_data_for_block(block)
    result = checker.is_TOD(tx_a, tx_b, "original", False)

    assert not result
