# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_finds_ERC1155_gains_and_losses properties"] = {
    "accounts": {
        "attacker_bot": "a7206d878c5c3871826dfdb42191c49b1d11f466",
        "attacker_eoa": "7490486486eef630d8e3efa44a5264657e3b4bbd",
        "victim": "ab61903ee0a18780129c345a1264d78bb39a97cd",
    },
    "properties": {
        "attacker_bot_gain": False,
        "attacker_bot_loss": False,
        "attacker_eoa_gain": True,
        "attacker_eoa_loss": False,
        "attacker_gain_and_victim_loss": True,
        "victim_gain": False,
        "victim_loss": True,
    },
    "witnesses": {
        "7490486486eef630d8e3efa44a5264657e3b4bbd": {
            "ERC-1155-a7206d878c5c3871826dfdb42191c49b1d11f466-0x1": {
                "change": 1,
                "currency_identifier": "a7206d878c5c3871826dfdb42191c49b1d11f466-0x1",
                "location": {
                    "address": "0xa7206d878c5c3871826dfdb42191c49b1d11f466",
                    "pc": 8448,
                },
                "owner": "7490486486eef630d8e3efa44a5264657e3b4bbd",
                "type": "ERC-1155",
            }
        },
        "ab61903ee0a18780129c345a1264d78bb39a97cd": {
            "ERC-1155-a7206d878c5c3871826dfdb42191c49b1d11f466-0x1": {
                "change": -1,
                "currency_identifier": "a7206d878c5c3871826dfdb42191c49b1d11f466-0x1",
                "location": {
                    "address": "0xa7206d878c5c3871826dfdb42191c49b1d11f466",
                    "pc": 8448,
                },
                "owner": "ab61903ee0a18780129c345a1264d78bb39a97cd",
                "type": "ERC-1155",
            }
        },
    },
}

snapshots["test_finds_ERC20_gains_and_losses properties"] = {
    "accounts": {
        "attacker_bot": "7a250d5630b4cf539739df2c5dacb4c659f2488d",
        "attacker_eoa": "867db1ce98b2ed8cc68ba5015b163bbbe07d4a41",
        "victim": "465a8228594a8437014b092f65e925bc0473e6fd",
    },
    "properties": {
        "attacker_bot_gain": False,
        "attacker_bot_loss": False,
        "attacker_eoa_gain": True,
        "attacker_eoa_loss": False,
        "attacker_gain_and_victim_loss": True,
        "victim_gain": False,
        "victim_loss": True,
    },
    "witnesses": {
        "465a8228594a8437014b092f65e925bc0473e6fd": {
            "ERC-20-446c9033e7516d820cc9a2ce2d0b7328b579406f": {
                "change": 0,
                "currency_identifier": "446c9033e7516d820cc9a2ce2d0b7328b579406f",
                "location": {
                    "address": "0x446c9033e7516d820cc9a2ce2d0b7328b579406f",
                    "pc": 5581,
                },
                "owner": "465a8228594a8437014b092f65e925bc0473e6fd",
                "type": "ERC-20",
            },
            "ERC-20-dac17f958d2ee523a2206206994597c13d831ec7": {
                "change": -485157,
                "currency_identifier": "dac17f958d2ee523a2206206994597c13d831ec7",
                "location": {
                    "address": "0xdac17f958d2ee523a2206206994597c13d831ec7",
                    "pc": 9801,
                },
                "owner": "465a8228594a8437014b092f65e925bc0473e6fd",
                "type": "ERC-20",
            },
        },
        "7a250d5630b4cf539739df2c5dacb4c659f2488d": {
            "ETHER-Wei": {
                "change": 0,
                "currency_identifier": "Wei",
                "location": {
                    "address": "0x7a250d5630b4cf539739df2c5dacb4c659f2488d",
                    "pc": 17090,
                },
                "owner": "7a250d5630b4cf539739df2c5dacb4c659f2488d",
                "type": "ETHER",
            }
        },
        "867db1ce98b2ed8cc68ba5015b163bbbe07d4a41": {
            "ERC-20-84cffa78b2fbbeec8c37391d2b12a04d2030845e": {
                "change": 0,
                "currency_identifier": "84cffa78b2fbbeec8c37391d2b12a04d2030845e",
                "location": {
                    "address": "0x84cffa78b2fbbeec8c37391d2b12a04d2030845e",
                    "pc": 3695,
                },
                "owner": "867db1ce98b2ed8cc68ba5015b163bbbe07d4a41",
                "type": "ERC-20",
            },
            "ERC-20-dac17f958d2ee523a2206206994597c13d831ec7": {
                "change": 485157,
                "currency_identifier": "dac17f958d2ee523a2206206994597c13d831ec7",
                "location": {
                    "address": "0xdac17f958d2ee523a2206206994597c13d831ec7",
                    "pc": 9801,
                },
                "owner": "867db1ce98b2ed8cc68ba5015b163bbbe07d4a41",
                "type": "ERC-20",
            },
        },
    },
}

snapshots["test_finds_ERC721_gains_and_losses properties"] = {
    "accounts": {
        "attacker_bot": "fb4ccb3e948fed6946fc528ba806e737edc938c4",
        "attacker_eoa": "c5442aa3bfcfd998c3d1d5d197e0d8ba689cc3d8",
        "victim": "81a4e7c03c54f32d5037241e101b2d20c4984287",
    },
    "properties": {
        "attacker_bot_gain": False,
        "attacker_bot_loss": False,
        "attacker_eoa_gain": True,
        "attacker_eoa_loss": False,
        "attacker_gain_and_victim_loss": True,
        "victim_gain": False,
        "victim_loss": True,
    },
    "witnesses": {
        "81a4e7c03c54f32d5037241e101b2d20c4984287": {
            "ERC-721-fb4ccb3e948fed6946fc528ba806e737edc938c4-00000000000000000000000000000000000000000000000000000000000001a0": {
                "change": -1,
                "currency_identifier": "fb4ccb3e948fed6946fc528ba806e737edc938c4-00000000000000000000000000000000000000000000000000000000000001a0",
                "location": {
                    "address": "0xfb4ccb3e948fed6946fc528ba806e737edc938c4",
                    "pc": 10230,
                },
                "owner": "81a4e7c03c54f32d5037241e101b2d20c4984287",
                "type": "ERC-721",
            }
        },
        "c5442aa3bfcfd998c3d1d5d197e0d8ba689cc3d8": {
            "ERC-721-fb4ccb3e948fed6946fc528ba806e737edc938c4-00000000000000000000000000000000000000000000000000000000000001a0": {
                "change": 1,
                "currency_identifier": "fb4ccb3e948fed6946fc528ba806e737edc938c4-00000000000000000000000000000000000000000000000000000000000001a0",
                "location": {
                    "address": "0xfb4ccb3e948fed6946fc528ba806e737edc938c4",
                    "pc": 10230,
                },
                "owner": "c5442aa3bfcfd998c3d1d5d197e0d8ba689cc3d8",
                "type": "ERC-721",
            }
        },
    },
}

snapshots["test_finds_ERC777_gains_and_losses properties"] = {
    "accounts": {
        "attacker_bot": "7a250d5630b4cf539739df2c5dacb4c659f2488d",
        "attacker_eoa": "26263a3432104dd51ac232269fb01dafa630e956",
        "victim": "69fa4085475eb9c0ca6df51a348f6673cad4d2ee",
    },
    "properties": {
        "attacker_bot_gain": False,
        "attacker_bot_loss": False,
        "attacker_eoa_gain": True,
        "attacker_eoa_loss": False,
        "attacker_gain_and_victim_loss": True,
        "victim_gain": False,
        "victim_loss": True,
    },
    "witnesses": {
        "26263a3432104dd51ac232269fb01dafa630e956": {
            "ERC-20-e1d7c7a4596b038ced2a84bf65b8647271c53208": {
                "change": 13600269514768362,
                "currency_identifier": "e1d7c7a4596b038ced2a84bf65b8647271c53208",
                "location": {
                    "address": "0xe1d7c7a4596b038ced2a84bf65b8647271c53208",
                    "pc": 9724,
                },
                "owner": "26263a3432104dd51ac232269fb01dafa630e956",
                "type": "ERC-20",
            }
        },
        "69fa4085475eb9c0ca6df51a348f6673cad4d2ee": {
            "ERC-20-5228a22e72ccc52d415ecfd199f99d0665e7733b": {
                "change": -67934201495,
                "currency_identifier": "5228a22e72ccc52d415ecfd199f99d0665e7733b",
                "location": {
                    "address": "0x5228a22e72ccc52d415ecfd199f99d0665e7733b",
                    "pc": 8340,
                },
                "owner": "69fa4085475eb9c0ca6df51a348f6673cad4d2ee",
                "type": "ERC-20",
            },
            "ERC-20-dac17f958d2ee523a2206206994597c13d831ec7": {
                "change": 0,
                "currency_identifier": "dac17f958d2ee523a2206206994597c13d831ec7",
                "location": {
                    "address": "0xdac17f958d2ee523a2206206994597c13d831ec7",
                    "pc": 10748,
                },
                "owner": "69fa4085475eb9c0ca6df51a348f6673cad4d2ee",
                "type": "ERC-20",
            },
            "ERC-777-5228a22e72ccc52d415ecfd199f99d0665e7733b": {
                "change": -67934201495,
                "currency_identifier": "5228a22e72ccc52d415ecfd199f99d0665e7733b",
                "location": {
                    "address": "0x5228a22e72ccc52d415ecfd199f99d0665e7733b",
                    "pc": 8265,
                },
                "owner": "69fa4085475eb9c0ca6df51a348f6673cad4d2ee",
                "type": "ERC-777",
            },
        },
        "7a250d5630b4cf539739df2c5dacb4c659f2488d": {
            "ERC-20-c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2": {
                "change": 0,
                "currency_identifier": "c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
                "location": {
                    "address": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
                    "pc": 2510,
                },
                "owner": "7a250d5630b4cf539739df2c5dacb4c659f2488d",
                "type": "ERC-20",
            },
            "ETHER-Wei": {
                "change": 0,
                "currency_identifier": "Wei",
                "location": {
                    "address": "0x7a250d5630b4cf539739df2c5dacb4c659f2488d",
                    "pc": 9129,
                },
                "owner": "7a250d5630b4cf539739df2c5dacb4c659f2488d",
                "type": "ETHER",
            },
        },
    },
}

snapshots["test_finds_TOD_Amount securify a"] = {
    "properties": {"TOD_Amount": True, "TOD_Receiver": False, "TOD_Transfer": False},
    "witnesses": {
        "TOD_Amount": [
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
                        "recipient": "9a19f7fb2f2eaa80ce3718f05db9c5e8fcdebf1f",
                        "sender": "0x3328f7f4a1d1c57c35df56bbf0c9dcafca309c49",
                    }
                ],
            ),
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
                        "recipient": "9a19f7fb2f2eaa80ce3718f05db9c5e8fcdebf1f",
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

snapshots["test_finds_TOD_Amount securify b"] = {
    "properties": {"TOD_Amount": True, "TOD_Receiver": False, "TOD_Transfer": False},
    "witnesses": {
        "TOD_Amount": [
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
                        "recipient": "b1cedfaa2339fb81dd7dcf9f490ac9d6f1e26f5c",
                        "sender": "0x3328f7f4a1d1c57c35df56bbf0c9dcafca309c49",
                    }
                ],
                [],
            ),
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
                        "recipient": "b1cedfaa2339fb81dd7dcf9f490ac9d6f1e26f5c",
                        "sender": "0x3328f7f4a1d1c57c35df56bbf0c9dcafca309c49",
                    }
                ],
            ),
        ],
        "TOD_Receiver": [],
        "TOD_Transfer": [],
    },
}
