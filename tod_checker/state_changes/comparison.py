from typing import Iterable, Sequence

from attr import dataclass
from tod_checker.types.types import PrePostState, StateKey, WorldState, WorldStateDiff


@dataclass
class StateChangeDifference:
    key: StateKey
    original: int
    other: int

    def __str__(self):
        msg = "<changes differ: "
        msg += "@".join(self.key)
        msg += f" normal: {self._format_change(self.original)} | reverse: {self._format_change(self.other)}>"
        return msg

    @staticmethod
    def _format_change(change: int):
        if change >= 0:
            return f"+{hex(change)}"
        else:
            return f"-{hex(-change)}"


def resolve(state: WorldState | WorldStateDiff, key: StateKey) -> int | None:
    if len(key) == 2:
        value = state.get(key[1], {}).get(key[0])
    else:
        value = state.get(key[1], {}).get(key[0], {}).get(key[2])
    if value is None:
        return None
    if value == "0x":
        return 0
    if isinstance(value, str):
        return int(value, 16)
    return value


def resolve_diff(state: WorldStateDiff, key: StateKey) -> int:
    value = resolve(state, key)
    if value is None:
        return 0
    return value


def to_world_state_diff(changes: PrePostState) -> WorldStateDiff:
    state_a, state_b = changes["pre"], changes["post"]
    diff: WorldStateDiff = {}
    for k in set(state_keys(state_a)) | set(state_keys(state_b)):
        type = k[0]
        addr = k[1]
        if addr not in diff:
            diff[addr] = {}
        val_a = resolve(state_a, k)
        val_b = resolve(state_b, k)
        assert (
            val_a is not None and val_b is not None
        ), f"Cannot create diff if states have different keys: {k}"
        val_diff = val_b - val_a

        if len(k) == 2:
            diff[addr][type] = val_diff
        else:
            slot = k[2]
            if type not in diff[addr]:
                diff[addr][type] = {}
            diff[addr][type][slot] = val_diff

    return diff


def add_world_state_diffs(a: WorldStateDiff, b: WorldStateDiff) -> WorldStateDiff:
    diff_sum_state: WorldStateDiff = {}
    for k in set(state_keys(a)) | set(state_keys(b)):
        type = k[0]
        addr = k[1]
        if addr not in diff_sum_state:
            diff_sum_state[addr] = {}
        val_a = resolve(a, k) or 0
        val_b = resolve(b, k) or 0
        diff_sum = val_a + val_b

        if len(k) == 2:
            diff_sum_state[addr][type] = diff_sum
        else:
            slot = k[2]
            if type not in diff_sum_state[addr]:
                diff_sum_state[addr][type] = {}
            diff_sum_state[addr][type][slot] = diff_sum

    return diff_sum_state


class StateChangesComparison:
    def __init__(self, a: WorldStateDiff, b: WorldStateDiff) -> None:
        self._a = a
        self._b = b

    def differences(self) -> Sequence[StateChangeDifference]:
        differences = []

        for state_key in self.all_state_keys():
            diff_a = resolve_diff(self._a, state_key)
            diff_b = resolve_diff(self._b, state_key)

            if diff_a != diff_b:
                differences.append(StateChangeDifference(state_key, diff_a, diff_b))

        return differences

    def all_state_keys(self) -> Sequence[StateKey]:
        keys = set()

        keys.update(state_keys(self._a))
        keys.update(state_keys(self._b))

        return sorted(keys)


def state_keys(state: WorldState | WorldStateDiff) -> Iterable[StateKey]:
    for addr in state:
        for key in state[addr]:
            if key == "storage":
                for slot in state[addr][key]:  # type: ignore
                    yield (key, addr, slot)
            else:
                yield ((key, addr))


def compare_state_changes(a: PrePostState, b: PrePostState) -> StateChangesComparison:
    return StateChangesComparison(
        to_world_state_diff(a),
        to_world_state_diff(b),
    )


def compare_world_state_diffs(
    a: WorldStateDiff, b: WorldStateDiff
) -> StateChangesComparison:
    return StateChangesComparison(a, b)
