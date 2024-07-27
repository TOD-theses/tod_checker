from copy import deepcopy
from typing import Literal

from tod_checker.types.types import AccountState

Provider = Literal["old Erigon"] | Literal["reth"]


class OverridesFormatter:
    def __init__(self, target: Provider) -> None:
        self.target: Provider = target

    def format(self, account_state: AccountState) -> AccountState:
        result: dict = deepcopy(account_state)  # type: ignore
        if "nonce" in result:
            result["nonce"] = hex(result["nonce"])
        if "storage" in result:
            result["stateDiff"] = result["storage"]
            for slot, val in result["stateDiff"].items():
                if self.target == "old Erigon":
                    # https://github.com/erigontech/erigon/issues/8345
                    result["stateDiff"][slot] = hex(int(val, 16))
                if self.target == "reth":
                    if result["stateDiff"][slot] == "0x0":
                        result["stateDiff"][slot] = "0x" + "0" * 64
            del result["storage"]
        if result.get("code") == "0x0":
            result["code"] = "0x"

        return result  # type: ignore
