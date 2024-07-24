# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_finds_TOD post differing addresses"] = [
    "0x2e464a9332dc86a60d6b2c24fada0c8728a528e8",
    "0x440568bde9c7c9841400d7d6fe78aac0b0e66c39",
    "0x4c9edd5852cd905f086c759e8383e09bff1e68b3",
    "0x6b75d8af000000e20b7a7ddf000ba900b4009a80",
    "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
    "0xae2fc483527b8ef99eb5d9b44875f005ba1fae13",
    "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
    "0xe6d7ebb9f1a9519dc06d557e03c522d53520e76a",
]

snapshots["test_finds_TOD post differing types"] = frozenset(["balance", "storage"])

snapshots["test_finds_TOD pre differing addresses"] = [
    "0x2e464a9332dc86a60d6b2c24fada0c8728a528e8",
    "0x440568bde9c7c9841400d7d6fe78aac0b0e66c39",
    "0x4c9edd5852cd905f086c759e8383e09bff1e68b3",
    "0x6b75d8af000000e20b7a7ddf000ba900b4009a80",
    "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
    "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
    "0xe6d7ebb9f1a9519dc06d557e03c522d53520e76a",
]

snapshots["test_finds_TOD pre differing types"] = frozenset(["balance", "storage"])
