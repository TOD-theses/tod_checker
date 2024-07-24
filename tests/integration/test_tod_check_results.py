import pytest

from tod_checker.checker.checker import ReplayDivergedException, TodChecker
from tod_checker.executor.executor import TransactionExecutor
from tod_checker.rpc.rpc import RPC
from tod_checker.state_changes.fetcher import StateChangesFetcher
from tod_checker.tx_block_mapper.tx_block_mapper import TransactionBlockMapper

from snapshottest.pytest import PyTestSnapshotTest

test_provider_url = "http://localhost:8124/eth"


def _get_checker():
    rpc = RPC(test_provider_url)
    state_changes_fetcher = StateChangesFetcher(rpc)
    tx_block_mapper = TransactionBlockMapper(rpc)
    simulator = TransactionExecutor(rpc)
    return TodChecker(simulator, state_changes_fetcher, tx_block_mapper)


@pytest.mark.vcr
def test_finds_TOD(snapshot: PyTestSnapshotTest):
    tx_a = "0x0001e7b0bcf0c41941c5d53c8636139565456343e8fad9bc86609329e63cb350"
    tx_b = "0xa3cc046ea030d51a16ee32514650f82ea9e41d1270ec2c1a749e5087b1fde4ce"

    checker = _get_checker()
    checker.download_data_for_transactions([tx_a, tx_b])
    result = checker.is_TOD(tx_a, tx_b)

    assert result is not False

    snapshot.assert_match(result.pre.differing_addresses(), "pre differing addresses")
    snapshot.assert_match(result.post.differing_addresses(), "post differing addresses")
    snapshot.assert_match(result.pre.differing_types(), "pre differing types")
    snapshot.assert_match(result.post.differing_types(), "post differing types")


@pytest.mark.vcr
def test_replay_diverges(snapshot: PyTestSnapshotTest):
    tx_a = "0x0364a6845b37541c3e06b1e1e1fb7b7d287ee48fe4d375f11fc7cdb68fe4e1d8"
    tx_b = "0xf1d36e5749ec4ff511110afdd68b6e663023c0bf3438c991006ecb2e6d9c5b32"

    checker = _get_checker()
    checker.download_data_for_transactions([tx_a, tx_b])

    with pytest.raises(ReplayDivergedException):
        checker.is_TOD(tx_a, tx_b)


@pytest.mark.vcr
def test_finds_non_TOD(snapshot: PyTestSnapshotTest):
    tx_a = "0x0001e7b0bcf0c41941c5d53c8636139565456343e8fad9bc86609329e63cb350"
    tx_b = "0x866bf65489b0839eecfa313a60415e4f581786fbba1257c90e4f7ded97f74dd7"

    checker = _get_checker()
    checker.download_data_for_transactions([tx_a, tx_b])
    result = checker.is_TOD(tx_a, tx_b)

    assert not result
