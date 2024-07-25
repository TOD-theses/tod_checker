from copy import deepcopy
from typing import Sequence
from tod_checker.types.types import PrePostState, WorldState


def sum_state_changes(state_changes: Sequence[PrePostState]) -> PrePostState:
    if not state_changes:
        return {"pre": {}, "post": {}}
    result = deepcopy(state_changes[0])
    for x in state_changes[1:]:
        overwrite_account_changes(result["post"], x["post"])
    return result


def undo_state_changes(state_changes: Sequence[PrePostState]) -> PrePostState:
    result = deepcopy(state_changes[-1])
    for x in reversed(state_changes[:-1]):
        overwrite_account_changes(result["pre"], x["pre"])
    return result


def overwrite_account_changes(base: WorldState, value: WorldState):
    for addr, account in value.items():
        if addr not in base:
            base[addr] = {}
        if "balance" in account:
            base[addr]["balance"] = account["balance"]
        if "nonce" in account:
            base[addr]["nonce"] = account["nonce"]
        if "code" in account:
            if account["code"] == "0x0":
                account["code"] = "0x"
            base[addr]["code"] = account["code"]
        if "storage" in account:
            if "storage" not in base[addr]:
                base[addr]["storage"] = {}
            for slot, v in account["storage"].items():
                base[addr]["storage"][slot] = v  # type: ignore
