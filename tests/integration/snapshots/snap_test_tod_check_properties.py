# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_finds_TOD_Amount securify a"] = {
    "properties": {"TOD_Amount": True, "TOD_Receiver": False, "TOD_Transfer": False},
    "witnesses": {
        "TOD_Amount": [
            (
                (
                    "0x3328f7f4a1d1c57c35df56bbf0c9dcafca309c49",
                    16089,
                    161132982504865020,
                ),
                [
                    {
                        "amount": 161132982504865020,
                        "location": {
                            "address": "0x3328f7f4a1d1c57c35df56bbf0c9dcafca309c49",
                            "pc": 16089,
                        },
                        "recipient": "0x9a19f7fb2f2eaa80ce3718f05db9c5e8fcdebf1f",
                        "sender": "0x3328f7f4a1d1c57c35df56bbf0c9dcafca309c49",
                    }
                ],
                [],
            ),
            (
                (
                    "0x3328f7f4a1d1c57c35df56bbf0c9dcafca309c49",
                    16089,
                    161132982504865019,
                ),
                [],
                [
                    {
                        "amount": 161132982504865019,
                        "location": {
                            "address": "0x3328f7f4a1d1c57c35df56bbf0c9dcafca309c49",
                            "pc": 16089,
                        },
                        "recipient": "0x9a19f7fb2f2eaa80ce3718f05db9c5e8fcdebf1f",
                        "sender": "0x3328f7f4a1d1c57c35df56bbf0c9dcafca309c49",
                    }
                ],
            ),
        ],
        "TOD_Receiver": [],
        "TOD_Transfer": [],
    },
}

snapshots["test_finds_TOD_Amount securify b"] = {
    "properties": {"TOD_Amount": True, "TOD_Receiver": False, "TOD_Transfer": False},
    "witnesses": {
        "TOD_Amount": [
            (
                (
                    "0x3328f7f4a1d1c57c35df56bbf0c9dcafca309c49",
                    16089,
                    97164590959203982,
                ),
                [],
                [
                    {
                        "amount": 97164590959203982,
                        "location": {
                            "address": "0x3328f7f4a1d1c57c35df56bbf0c9dcafca309c49",
                            "pc": 16089,
                        },
                        "recipient": "0xb1cedfaa2339fb81dd7dcf9f490ac9d6f1e26f5c",
                        "sender": "0x3328f7f4a1d1c57c35df56bbf0c9dcafca309c49",
                    }
                ],
            ),
            (
                (
                    "0x3328f7f4a1d1c57c35df56bbf0c9dcafca309c49",
                    16089,
                    97164590959203981,
                ),
                [
                    {
                        "amount": 97164590959203981,
                        "location": {
                            "address": "0x3328f7f4a1d1c57c35df56bbf0c9dcafca309c49",
                            "pc": 16089,
                        },
                        "recipient": "0xb1cedfaa2339fb81dd7dcf9f490ac9d6f1e26f5c",
                        "sender": "0x3328f7f4a1d1c57c35df56bbf0c9dcafca309c49",
                    }
                ],
                [],
            ),
        ],
        "TOD_Receiver": [],
        "TOD_Transfer": [],
    },
}
