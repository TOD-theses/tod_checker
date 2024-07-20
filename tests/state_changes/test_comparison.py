from tod_checker.rpc.types import WorldState
from tod_checker.state_changes.comparison import StateComparison

addr_1: str = "0xabcd"
addr_2: str = "0xbbbb"


def get_sample_state() -> WorldState:
    return {
        addr_1: {
            "balance": "abcd",
            "nonce": 123,
            "storage": {
                "a": "aaaa",
            },
        },
        addr_2: {"code": "abcde"},
    }


def test_comparison_equal():
    a = get_sample_state()
    b = get_sample_state()

    assert StateComparison.between(a, b).is_equal()


def test_comparison_changed_storage_value():
    a = get_sample_state()
    b = get_sample_state()
    b[addr_1]["storage"]["a"] = "bbbb"  # type: ignore

    assert not StateComparison.between(a, b).is_equal()


def test_comparison_new_storage_slot():
    a = get_sample_state()
    b = get_sample_state()
    b[addr_1]["storage"]["x"] = "xxxx"  # type: ignore

    assert not StateComparison.between(a, b).is_equal()


def test_comparison_removed_storage_slot():
    a = get_sample_state()
    b = get_sample_state()
    del b[addr_1]["storage"]["a"]  # type: ignore

    assert not StateComparison.between(a, b).is_equal()


def test_comparison_changed_nonce_value():
    a = get_sample_state()
    b = get_sample_state()
    b[addr_1]["nonce"] = 9999

    assert not StateComparison.between(a, b).is_equal()


def test_comparison_added_nonce_value():
    a = get_sample_state()
    b = get_sample_state()
    b[addr_2]["nonce"] = 9999

    assert not StateComparison.between(a, b).is_equal()


def test_comparison_removed_nonce_value():
    a = get_sample_state()
    b = get_sample_state()
    del b[addr_1]["nonce"]

    assert not StateComparison.between(a, b).is_equal()


def test_comparison_new_address():
    a = get_sample_state()
    b = get_sample_state()
    b["0xnew"] = {"balance": "abcd"}

    assert not StateComparison.between(a, b).is_equal()


def test_comparison_removed_address():
    a = get_sample_state()
    b = get_sample_state()
    del b[addr_1]

    assert not StateComparison.between(a, b).is_equal()


def test_differing_addresses():
    a = get_sample_state()
    b = get_sample_state()
    b["0xnew"] = {"nonce": 1234}
    b[addr_1]["storage"]["x"] = "xxxx"  # type: ignore

    differing_addresses = set(StateComparison.between(a, b).differing_addresses())

    assert differing_addresses == {"0xnew", addr_1}


def test_differing_types():
    a = get_sample_state()
    b = get_sample_state()
    b["0xnew"] = {"nonce": 1234}
    b[addr_1]["storage"]["x"] = "xxxx"  # type: ignore
    del b[addr_1]["balance"]

    differing_types = StateComparison.between(a, b).differing_types()

    assert differing_types == {"balance", "nonce", "storage"}
