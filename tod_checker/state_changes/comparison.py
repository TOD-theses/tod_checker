from typing import Iterable, Sequence

from attr import dataclass
from tod_checker.types.types import PrePostState, StateKey, WorldState


@dataclass
class StateChangeDifference:
    key: StateKey
    difference_a: int
    difference_b: int


def resolve(state: WorldState, key: StateKey) -> int | None:
    if len(key) == 2:
        value = state.get(key[1], {}).get(key[0])
    else:
        value = state.get(key[1], {}).get(key[0], {}).get(key[2])
    if value is None:
        return None
    if isinstance(value, str):
        return int(value, 16)
    return value


def compute_diff(state_a: WorldState, state_b: WorldState, key: StateKey) -> int:
    a = resolve(state_a, key)
    b = resolve(state_b, key)

    if a == b:
        return 0
    if a is None or b is None:
        raise Exception(
            f"Unexpected None: {key} {a} {b}. Please verify, that both states have the same state keys"
        )
    return b - a


class StateChangesComparison:
    def __init__(self, a: PrePostState, b: PrePostState) -> None:
        self.a = a
        self.b = b

    def differences(self) -> Sequence[StateChangeDifference]:
        differences = []

        for state_key in self.all_state_keys():
            diff_a = compute_diff(self.a["pre"], self.a["post"], state_key)
            diff_b = compute_diff(self.b["pre"], self.b["post"], state_key)

            if diff_a != diff_b:
                differences.append(StateChangeDifference(state_key, diff_a, diff_b))

        return differences

    def all_state_keys(self) -> Sequence[StateKey]:
        keys = set()

        keys.update(state_keys(self.a["pre"]))
        keys.update(state_keys(self.b["pre"]))
        keys.update(state_keys(self.a["post"]))
        keys.update(state_keys(self.b["post"]))

        return sorted(keys)


def state_keys(state: WorldState) -> Iterable[StateKey]:
    for addr in state:
        for key in state[addr]:
            if key == "storage":
                for slot in state[addr][key]:  # type: ignore
                    yield (key, addr, slot)
            else:
                yield ((key, addr))
