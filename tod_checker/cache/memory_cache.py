from typing import Generic, TypeVar


Key = TypeVar("Key")
Value = TypeVar("Value")


class MemoryCache(Generic[Key, Value]):
    def __init__(self) -> None:
        self._cache: dict[Key, Value] = {}

    def store(self, key: Key, value: Value):
        self._cache[key] = value

    def get(self, key: Key) -> Value:
        return self._cache[key]

    def has(self, key: Key) -> bool:
        return key in self._cache
