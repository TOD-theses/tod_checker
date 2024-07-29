# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import GenericRepr, Snapshot


snapshots = Snapshot()

snapshots["test_finds_TOD differences"] = [
    GenericRepr(
        "StateChangeDifference(key=('balance', '0x6b75d8af000000e20b7a7ddf000ba900b4009a80'), original=41, other=0)"
    ),
    GenericRepr(
        "StateChangeDifference(key=('storage', '0x2e464a9332dc86a60d6b2c24fada0c8728a528e8', '0x0000000000000000000000000000000000000000000000000000000000000008'), original=-93642995832518067243923322503102599459654300860416, other=0)"
    ),
    GenericRepr(
        "StateChangeDifference(key=('storage', '0x440568bde9c7c9841400d7d6fe78aac0b0e66c39', '0x4fa8a8526b4491c9a8a9cea2cce5e853b07a553ae851c86bb0a20942be44fc1e'), original=196998862693466112, other=0)"
    ),
    GenericRepr(
        "StateChangeDifference(key=('storage', '0x440568bde9c7c9841400d7d6fe78aac0b0e66c39', '0x577b913a3c8810dd10161c9ae11e2ee31042564c62114c83b0bc5d3a3e71b362'), original=-196998862693466112, other=0)"
    ),
    GenericRepr(
        "StateChangeDifference(key=('storage', '0x4c9edd5852cd905f086c759e8383e09bff1e68b3', '0x29cb8bd4e192d16f51155329ce8b0f5eb88a1d9e4d3b93ce07efbac9e1c4d175'), original=2375409971275820075352, other=0)"
    ),
    GenericRepr(
        "StateChangeDifference(key=('storage', '0x4c9edd5852cd905f086c759e8383e09bff1e68b3', '0xd3eb0c7a34e059cb07429f8ece14ae93b5fd7b5255290002e4bf7ccfe1b81cd6'), original=-2375409971275820075352, other=0)"
    ),
    GenericRepr(
        "StateChangeDifference(key=('storage', '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48', '0x154bb98efc83b034ad81fbf23cc88c9737739df170c146ea18e8113dac893665'), original=-2369667434, other=0)"
    ),
    GenericRepr(
        "StateChangeDifference(key=('storage', '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48', '0xaf0f667aab27684156fab5bb64c20fab8833c4f474fe01181a318d6840a86fd8'), original=2369667434, other=0)"
    ),
    GenericRepr(
        "StateChangeDifference(key=('storage', '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2', '0x12231cd4c753cb5530a43a74c45106c24765e6f81dc8927d4f4be7e53315d5a8'), original=18034984975597568, other=0)"
    ),
    GenericRepr(
        "StateChangeDifference(key=('storage', '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2', '0x4234a9a4d18d33c093d84fc349f5d5e25ac8a9bc0f8630afb7ce4ce96202702c'), original=-18034984975597568, other=0)"
    ),
    GenericRepr(
        "StateChangeDifference(key=('storage', '0xe6d7ebb9f1a9519dc06d557e03c522d53520e76a', '0x0000000000000000000000000000000000000000000000000000000000000000'), original=379990425706034758732958056507254968786735030024465, other=0)"
    ),
    GenericRepr(
        "StateChangeDifference(key=('storage', '0xe6d7ebb9f1a9519dc06d557e03c522d53520e76a', '0x0000000000000000000000000000000000000000000000000000000000000002'), original=438730428500927451644285052, other=0)"
    ),
    GenericRepr(
        "StateChangeDifference(key=('storage', '0xe6d7ebb9f1a9519dc06d557e03c522d53520e76a', '0x0000000000000000000000000000000000000000000000000000000000000004'), original=2563581225170350143, other=0)"
    ),
    GenericRepr(
        "StateChangeDifference(key=('storage', '0xe6d7ebb9f1a9519dc06d557e03c522d53520e76a', '0x6233fd32985d73917a1807516ec6823063b0b86cbeb593de8607b7649c9e69e4'), original=221177889131518017951132655387731757887147, other=0)"
    ),
    GenericRepr(
        "StateChangeDifference(key=('storage', '0xe6d7ebb9f1a9519dc06d557e03c522d53520e76a', '0x6233fd32985d73917a1807516ec6823063b0b86cbeb593de8607b7649c9e69e5'), original=220442363514146950436458972979, other=0)"
    ),
    GenericRepr(
        "StateChangeDifference(key=('storage', '0xe6d7ebb9f1a9519dc06d557e03c522d53520e76a', '0x6233fd32985d73917a1807516ec6823063b0b86cbeb593de8607b7649c9e69e6'), original=180663013411288391444714137005961876109685998443927300198544718743520972208, other=0)"
    ),
]

snapshots["test_finds_TOD_adapted_definition differences"] = [
    GenericRepr(
        "StateChangeDifference(key=('balance', '0x6b75d8af000000e20b7a7ddf000ba900b4009a80'), original=41, other=0)"
    ),
    GenericRepr(
        "StateChangeDifference(key=('storage', '0x2e464a9332dc86a60d6b2c24fada0c8728a528e8', '0x0000000000000000000000000000000000000000000000000000000000000008'), original=789047470118402629606261053464311833749059703100296, other=882690465950920696850184375967414433208714003960712)"
    ),
    GenericRepr(
        "StateChangeDifference(key=('storage', '0x440568bde9c7c9841400d7d6fe78aac0b0e66c39', '0x4fa8a8526b4491c9a8a9cea2cce5e853b07a553ae851c86bb0a20942be44fc1e'), original=-1689792423302573176, other=-1886791285996039288)"
    ),
    GenericRepr(
        "StateChangeDifference(key=('storage', '0x440568bde9c7c9841400d7d6fe78aac0b0e66c39', '0x577b913a3c8810dd10161c9ae11e2ee31042564c62114c83b0bc5d3a3e71b362'), original=-196998862693466112, other=0)"
    ),
    GenericRepr(
        "StateChangeDifference(key=('storage', '0x4c9edd5852cd905f086c759e8383e09bff1e68b3', '0x29cb8bd4e192d16f51155329ce8b0f5eb88a1d9e4d3b93ce07efbac9e1c4d175'), original=2375409971275820075352, other=0)"
    ),
    GenericRepr(
        "StateChangeDifference(key=('storage', '0x4c9edd5852cd905f086c759e8383e09bff1e68b3', '0xd3eb0c7a34e059cb07429f8ece14ae93b5fd7b5255290002e4bf7ccfe1b81cd6'), original=-2375409971275820075352, other=0)"
    ),
    GenericRepr(
        "StateChangeDifference(key=('storage', '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48', '0x154bb98efc83b034ad81fbf23cc88c9737739df170c146ea18e8113dac893665'), original=-2369667434, other=0)"
    ),
    GenericRepr(
        "StateChangeDifference(key=('storage', '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48', '0xaf0f667aab27684156fab5bb64c20fab8833c4f474fe01181a318d6840a86fd8'), original=2369667434, other=0)"
    ),
    GenericRepr(
        "StateChangeDifference(key=('storage', '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2', '0x12231cd4c753cb5530a43a74c45106c24765e6f81dc8927d4f4be7e53315d5a8'), original=18034984975597568, other=0)"
    ),
    GenericRepr(
        "StateChangeDifference(key=('storage', '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2', '0x4234a9a4d18d33c093d84fc349f5d5e25ac8a9bc0f8630afb7ce4ce96202702c'), original=151965015024402432, other=170000000000000000)"
    ),
    GenericRepr(
        "StateChangeDifference(key=('storage', '0xe6d7ebb9f1a9519dc06d557e03c522d53520e76a', '0x0000000000000000000000000000000000000000000000000000000000000000'), original=379990425706034758732958056507254968786735030024465, other=0)"
    ),
    GenericRepr(
        "StateChangeDifference(key=('storage', '0xe6d7ebb9f1a9519dc06d557e03c522d53520e76a', '0x0000000000000000000000000000000000000000000000000000000000000002'), original=438730428500927451644285052, other=0)"
    ),
    GenericRepr(
        "StateChangeDifference(key=('storage', '0xe6d7ebb9f1a9519dc06d557e03c522d53520e76a', '0x0000000000000000000000000000000000000000000000000000000000000004'), original=2563581225170350143, other=0)"
    ),
    GenericRepr(
        "StateChangeDifference(key=('storage', '0xe6d7ebb9f1a9519dc06d557e03c522d53520e76a', '0x6233fd32985d73917a1807516ec6823063b0b86cbeb593de8607b7649c9e69e4'), original=221177889131518017951132655387731757887147, other=0)"
    ),
    GenericRepr(
        "StateChangeDifference(key=('storage', '0xe6d7ebb9f1a9519dc06d557e03c522d53520e76a', '0x6233fd32985d73917a1807516ec6823063b0b86cbeb593de8607b7649c9e69e5'), original=220442363514146950436458972979, other=0)"
    ),
    GenericRepr(
        "StateChangeDifference(key=('storage', '0xe6d7ebb9f1a9519dc06d557e03c522d53520e76a', '0x6233fd32985d73917a1807516ec6823063b0b86cbeb593de8607b7649c9e69e6'), original=180663013411288391444714137005961876109685998443927300198544718743520972208, other=0)"
    ),
]
