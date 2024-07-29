from tod_checker.state_changes.comparison import (
    add_world_state_diffs,
    compare_state_changes,
)
from tod_checker.types.types import PrePostState, WorldState, WorldStateDiff

addr_1: str = "0xabcd"
addr_2: str = "0xbbbb"
addr_1_slot: str = "a"


def get_sample_state() -> WorldState:
    return {
        addr_1: {
            "balance": "abcd",
            "nonce": 123,
            "storage": {
                addr_1_slot: "aaaa",
            },
        },
        addr_2: {"code": "abcde"},
    }


def get_sample_states() -> tuple[PrePostState, PrePostState]:
    return (
        {
            "pre": get_sample_state(),
            "post": get_sample_state(),
        },
        {
            "pre": get_sample_state(),
            "post": get_sample_state(),
        },
    )


def test_comparison_equal():
    a, b = get_sample_states()

    comparison = compare_state_changes(a, b)

    assert not comparison.differences()


def test_comparison_equal_const_change():
    # both change the balance by the same value, but have different pre and post values
    a, b = get_sample_states()
    a["pre"][addr_1]["balance"] = hex(1234)
    b["pre"][addr_1]["balance"] = hex(5678)
    a["post"][addr_1]["balance"] = hex(int(a["pre"][addr_1]["balance"], 16) + 123)  # type: ignore
    b["post"][addr_1]["balance"] = hex(int(b["pre"][addr_1]["balance"], 16) + 123)  # type: ignore

    differences = compare_state_changes(a, b).differences()

    assert not differences


def test_comparison_changed_pre_storage():
    # write-write TOD
    a, b = get_sample_states()
    b["pre"][addr_1]["storage"][addr_1_slot] = "bbbb"  # type: ignore

    differences = compare_state_changes(a, b).differences()

    assert len(differences) == 1
    assert differences[0].key == ("storage", addr_1, addr_1_slot)


def test_comparison_changed_post_storage():
    a, b = get_sample_states()
    b["post"][addr_1]["storage"][addr_1_slot] = "bbbb"  # type: ignore

    differences = compare_state_changes(a, b).differences()

    assert len(differences) == 1
    assert differences[0].key == ("storage", addr_1, addr_1_slot)


def test_comparison_new_storage_slot():
    a, b = get_sample_states()
    b["pre"][addr_1]["storage"]["x"] = "0000"  # type: ignore
    b["post"][addr_1]["storage"]["x"] = "cccc"  # type: ignore

    differences = compare_state_changes(a, b).differences()

    assert len(differences) == 1
    assert differences[0].key == ("storage", addr_1, "x")


def test_comparison_removed_slot():
    a, b = get_sample_states()
    a["pre"][addr_1]["storage"][addr_1_slot] = hex(10)  # type: ignore
    a["post"][addr_1]["storage"][addr_1_slot] = hex(20)  # type: ignore
    del b["pre"][addr_1]["storage"][addr_1_slot]  # type: ignore
    del b["post"][addr_1]["storage"][addr_1_slot]  # type: ignore

    differences = compare_state_changes(a, b).differences()

    assert len(differences) == 1
    assert differences[0].key == ("storage", addr_1, addr_1_slot)


def test_comparison_added_nonce_change():
    a, b = get_sample_states()
    b["pre"][addr_2]["nonce"] = 123
    b["post"][addr_2]["nonce"] = 456

    differences = compare_state_changes(a, b).differences()

    assert len(differences) == 1
    assert differences[0].key == ("nonce", addr_2)


def test_comparison_new_address():
    a, b = get_sample_states()
    b["pre"]["0xnew"] = {"balance": "0xaaaa"}
    b["post"]["0xnew"] = {"balance": "0xbbbb"}

    differences = compare_state_changes(a, b).differences()

    assert len(differences) == 1
    assert differences[0].key == ("balance", "0xnew")


def test_comparison_removed_address():
    a, b = get_sample_states()
    a["pre"][addr_1]["balance"] = "0xaaaa"
    a["post"][addr_1]["balance"] = "0xbbbb"
    del b["pre"][addr_1]
    del b["post"][addr_1]

    differences = compare_state_changes(a, b).differences()

    assert len(differences) == 1
    assert differences[0].key == ("balance", addr_1)


def test_comparison_diff_result():
    a, b = get_sample_states()
    a["pre"][addr_1]["balance"] = "0xaaaa"
    a["post"][addr_1]["balance"] = "0xbbbb"
    del b["pre"][addr_1]
    del b["post"][addr_1]

    differences = compare_state_changes(a, b).differences()

    assert len(differences) == 1
    assert differences[0].original == 0xBBBB - 0xAAAA
    assert differences[0].other == 0x0


def test_world_state_diff_sum():
    a: WorldStateDiff = {"0xaddr": {"balance": 1234}}
    b: WorldStateDiff = {"0xaddr": {"balance": 10}, "0xother": {"nonce": 1}}

    state = add_world_state_diffs(a, b)

    assert state["0xaddr"].get("balance") == 1244
    assert state["0xother"].get("nonce") == 1
