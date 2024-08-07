from collections import defaultdict
from typing import Callable, Hashable, Iterable, Mapping, Sequence, TypeVar, TypedDict

from tod_checker.currency_changes.currency_change import (
    CURRENCY_TYPE,
    LocatedCurrencyChange,
    Location,
)

KEY = TypeVar("KEY", bound=Hashable)


class SecurifyProperties(TypedDict):
    TOD_Transfer: bool
    TOD_Amount: bool
    TOD_Receiver: bool


class EtherTransfer(TypedDict):
    sender: str
    recipient: str
    amount: int
    location: Location


class SecurifyPropertyWitnesses(TypedDict):
    """A list of witnesses for each property. A witness consists of the key and two lists with different lengths"""

    TOD_Transfer: Sequence[
        tuple[tuple, Sequence[EtherTransfer], Sequence[EtherTransfer]]
    ]
    TOD_Amount: Sequence[tuple[tuple, Sequence[EtherTransfer], Sequence[EtherTransfer]]]
    TOD_Receiver: Sequence[
        tuple[tuple, Sequence[EtherTransfer], Sequence[EtherTransfer]]
    ]


class SecurifyCheckResult(TypedDict):
    properties: SecurifyProperties
    witnesses: SecurifyPropertyWitnesses


def check_securify_properties(
    currency_changes_normal: Iterable[LocatedCurrencyChange],
    currency_changes_reverse: Iterable[LocatedCurrencyChange],
) -> SecurifyCheckResult:
    calls_normal = filter_ether_transfers_with_positive_value(currency_changes_normal)
    calls_reverse = filter_ether_transfers_with_positive_value(currency_changes_reverse)

    tod_transfer_witnesses = get_different_groups(
        calls_normal, calls_reverse, location_key
    )
    tod_amount_witnesses = get_different_groups(
        calls_normal, calls_reverse, location_amount_key
    )
    tod_receiver_witnesses = get_different_groups(
        calls_normal, calls_reverse, location_receiver_key
    )

    tod_transfer = len(tod_transfer_witnesses) > 0
    tod_amount = len(tod_amount_witnesses) > 0
    tod_receiver = len(tod_receiver_witnesses) > 0

    return {
        "properties": {
            "TOD_Transfer": tod_transfer,
            "TOD_Amount": tod_amount and not tod_transfer,
            "TOD_Receiver": tod_receiver and not tod_transfer,
        },
        "witnesses": {
            "TOD_Transfer": tod_transfer_witnesses,
            "TOD_Amount": tod_amount_witnesses,
            "TOD_Receiver": tod_receiver_witnesses,
        },
    }


def filter_ether_transfers_with_positive_value(
    changes: Iterable[LocatedCurrencyChange],
) -> Sequence[EtherTransfer]:
    transfers: list[EtherTransfer] = []
    for c in changes:
        if c["type"] == CURRENCY_TYPE.ETHER and c["change"] > 0:
            transfers.append(
                {
                    "sender": c["location"]["address"],
                    "recipient": c["owner"],
                    "amount": c["change"],
                    "location": c["location"],
                }
            )

    return transfers


def get_different_groups(
    calls_normal: Iterable[EtherTransfer],
    calls_reverse: Iterable[EtherTransfer],
    get_key: Callable[[EtherTransfer], KEY],
) -> Sequence[tuple[KEY, Sequence[EtherTransfer], Sequence[EtherTransfer]]]:
    groups_normal = group_by(calls_normal, get_key)
    groups_reverse = group_by(calls_reverse, get_key)
    return groups_of_different_size(groups_normal, groups_reverse)


def group_by(
    calls: Iterable[EtherTransfer],
    get_key: Callable[[EtherTransfer], KEY],
) -> Mapping[KEY, Sequence[EtherTransfer]]:
    groups = defaultdict(list)
    for call in calls:
        groups[get_key(call)].append(call)

    return groups


def groups_of_different_size(
    groups_normal: Mapping[KEY, Sequence[EtherTransfer]],
    groups_reverse: Mapping[KEY, Sequence[EtherTransfer]],
) -> Sequence[tuple[KEY, Sequence[EtherTransfer], Sequence[EtherTransfer]]]:
    groups: list[tuple[KEY, Sequence[EtherTransfer], Sequence[EtherTransfer]]] = []
    for key in set(groups_normal) | set(groups_reverse):
        group_normal = groups_normal.get(key, [])
        group_reverse = groups_reverse.get(key, [])
        if len(group_normal) != len(group_reverse):
            groups.append((key, group_normal, group_reverse))

    return groups


def location_key(call: EtherTransfer):
    return call["location"]["address"], call["location"]["pc"]


def location_amount_key(call: EtherTransfer):
    return call["location"]["address"], call["location"]["pc"], call["amount"]


def location_receiver_key(call: EtherTransfer):
    # the owner must be the receiver, as we only consider positive Wei changes (the sender would loose Wei)
    return call["location"]["address"], call["location"]["pc"], call["recipient"]
