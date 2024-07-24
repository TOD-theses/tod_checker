from typing import Sequence
from tod_checker.rpc.types import WorldState


class StateComparison:
    def __init__(self, a: WorldState, b: WorldState) -> None:
        self._a = a
        self._b = b

    def is_equal(self) -> bool:
        return len(self.differing_addresses()) == 0

    def differing_addresses(self) -> Sequence[str]:
        results = set()
        for addr in set(self._a) | set(self._b):
            if self._a.get(addr) != self._b.get(addr):
                results.add(addr)
        return sorted(results)

    def differing_types(self) -> frozenset:
        results = set()

        for addr in self.differing_addresses():
            if addr not in self._a:
                # all types of an address if one state change does not contain the address
                results.update(self._b[addr])
            elif addr not in self._b:
                # all types of an address if one state change does not contain the address
                results.update(self._a[addr])
            else:
                # all types, where the state changes are different
                for addr in set(self._a) & set(self._b):
                    for type in set(self._a[addr]) | set(self._b[addr]):
                        if self._a[addr].get(type) != self._b[addr].get(type):
                            results.add(type)

        return frozenset(results)

    @staticmethod
    def between(a: WorldState, b: WorldState):
        return StateComparison(a, b)


class StateChangesComparison:
    def __init__(
        self, pre_comparison: StateComparison, post_comparison: StateComparison
    ) -> None:
        self.pre = pre_comparison
        self.post = post_comparison

    def equal(self) -> bool:
        return self.pre.is_equal() and self.post.is_equal()
