from collections import defaultdict
from copy import deepcopy
from typing import Iterable, TypedDict
from tod_checker.currency_changes.currency_change import (
    CurrencyChange,
    LocatedCurrencyChange,
)
from tod_checker.currency_changes.tracer.currency_changes_js_tracer import (
    unify_hex_value,
)

CurrencyChangesByAddress = dict[str, dict[str, CurrencyChange]]


class GainAndLossProperties(TypedDict):
    attacker_gain_and_victim_loss: bool
    attacker_eoa_gain: bool
    attacker_eoa_loss: bool
    attacker_bot_gain: bool
    attacker_bot_loss: bool
    victim_gain: bool
    victim_loss: bool


class GainAndLossAccounts(TypedDict):
    attacker_eoa: str
    attacker_bot: str
    victim: str


class GainAndLossResult(TypedDict):
    properties: GainAndLossProperties
    accounts: GainAndLossAccounts
    witnesses: CurrencyChangesByAddress


def check_gain_and_loss_properties(
    changes_normal: Iterable[LocatedCurrencyChange],
    changes_reverse: Iterable[LocatedCurrencyChange],
    accounts: GainAndLossAccounts,
) -> GainAndLossResult:
    accounts = unify_accounts(accounts)

    grouped_normal = group_by_address(changes_normal)
    grouped_reverse = group_by_address(changes_reverse)

    changes = add_changes(grouped_normal, negated_changes(grouped_reverse))
    # remove changes for addresses that do not interest us (makes witnesses easier to read)
    relevant_changes = only_keep_changes_by(
        changes,
        [accounts["attacker_eoa"], accounts["attacker_bot"], accounts["victim"]],
    )

    return {
        "accounts": accounts,
        "properties": compute_properties(relevant_changes, accounts),
        "witnesses": relevant_changes,
    }


def unify_accounts(accounts: GainAndLossAccounts) -> GainAndLossAccounts:
    return {
        "attacker_eoa": unify_hex_value(accounts["attacker_eoa"]),
        "attacker_bot": unify_hex_value(accounts["attacker_bot"]),
        "victim": unify_hex_value(accounts["victim"]),
    }


def group_by_address(
    changes: Iterable[LocatedCurrencyChange],
) -> CurrencyChangesByAddress:
    groups: CurrencyChangesByAddress = defaultdict(dict)

    for change in changes:
        addr = change["owner"]
        key = f'{change["type"]}-{change["currency_identifier"]}'
        if key not in groups[addr]:
            groups[addr][key] = deepcopy(change)
        else:
            groups[addr][key]["change"] += change["change"]

    return groups


def only_keep_changes_by(changes: CurrencyChangesByAddress, addresses: Iterable[str]):
    return {addr: changes[addr] for addr in addresses if addr in changes}


def compute_properties(
    changes: CurrencyChangesByAddress, accounts: GainAndLossAccounts
) -> GainAndLossProperties:
    attacker_eoa_gain = has_gains(changes, accounts["attacker_eoa"])
    attacker_eoa_loss = has_losses(changes, accounts["attacker_eoa"])
    attacker_bot_gain = has_gains(changes, accounts["attacker_bot"])
    attacker_bot_loss = has_losses(changes, accounts["attacker_bot"])
    victim_gain = has_gains(changes, accounts["victim"])
    victim_loss = has_losses(changes, accounts["victim"])

    overall_prop = (
        (attacker_eoa_gain and not attacker_eoa_loss)
        or (attacker_bot_gain and not attacker_bot_loss)
    ) and (victim_loss and not victim_gain)

    return {
        "attacker_gain_and_victim_loss": overall_prop,
        "attacker_eoa_gain": attacker_eoa_gain,
        "attacker_eoa_loss": attacker_eoa_loss,
        "attacker_bot_gain": attacker_bot_gain,
        "attacker_bot_loss": attacker_bot_loss,
        "victim_gain": victim_gain,
        "victim_loss": victim_loss,
    }


def has_gains(changes: CurrencyChangesByAddress, address: str):
    if address not in changes:
        return False
    addr_changes = changes[address]
    for c in addr_changes.values():
        if c["change"] > 0:
            return True
    return False


def has_losses(changes: CurrencyChangesByAddress, address: str):
    if address not in changes:
        return False
    addr_changes = changes[address]
    for c in addr_changes.values():
        if c["change"] < 0:
            return True
    return False


def add_changes(base: CurrencyChangesByAddress, *operands: CurrencyChangesByAddress):
    result = deepcopy(base)

    for operand in operands:
        for addr, changes in operand.items():
            for key, change in changes.items():
                if key not in result[addr]:
                    result[addr][key] = deepcopy(change)
                else:
                    result[addr][key]["change"] += change["change"]

    return result


def negated_changes(changes: CurrencyChangesByAddress):
    result = deepcopy(changes)

    for addr, c in result.items():
        for key in c:
            result[addr][key]["change"] *= -1

    return result
