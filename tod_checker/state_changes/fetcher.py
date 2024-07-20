from pathlib import Path
from typing import Iterable, Sequence

from tod_checker.cache.memory_cache import MemoryCache
from tod_checker.rpc.rpc import RPC
from tod_checker.rpc.state_diff_utils import (
    state_diff_fill_implicit_fields,
    state_diff_remove_unchanged_fields,
)
from tod_checker.rpc.types import PrePostState


class StateChangesFetcher:
    def __init__(self, rpc: RPC, cache_dir: Path | None = None) -> None:
        self.rpc = rpc
        self.cache_dir = cache_dir
        self._cache: MemoryCache[int, Sequence[PrePostState]] = MemoryCache()

    def download_blocks(self, blocks: Iterable[int]):
        for block in blocks:
            self.download_block(block)

    def download_block(self, block: int):
        state_diffs = self.rpc.fetch_state_diffs(block)
        for diff in state_diffs:
            state_diff_fill_implicit_fields(diff["result"])
            state_diff_remove_unchanged_fields(diff["result"])
        pre_post_states = [x["result"] for x in state_diffs]
        self._cache.store(block, pre_post_states)

    def get(self, block: int):
        return self._cache.get(block)
