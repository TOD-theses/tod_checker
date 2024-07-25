from copy import deepcopy
import json
from typing import Any, Literal
from eth_typing import HexStr
from web3 import Web3
from web3.types import RPCEndpoint, TxParams
from web3.method import Method
from web3.datastructures import AttributeDict

from tod_checker.types.types import (
    AccountState,
    BlockWithTransactions,
    PrePostState,
    TxData,
    TxPrestate,
    TxStateDiff,
    WorldState,
)


class RPC:
    def __init__(self, archive_node_provider_url: str) -> None:
        self.w3 = Web3(
            Web3.HTTPProvider(
                archive_node_provider_url, request_kwargs={"timeout": 120}
            )
        )

        self.w3.eth.attach_methods(
            {
                "debug_traceBlockByNumber": Method(
                    RPCEndpoint("debug_traceBlockByNumber")
                ),
                "eth_getBlockByNumber": Method(RPCEndpoint("eth_getBlockByNumber")),
                "debug_traceCall": Method(RPCEndpoint("debug_traceCall")),
                "debug_traceTransaction": Method(RPCEndpoint("debug_traceTransaction")),
                # NOTE: the stateDiff RPC method is expensive to call
                # rpc.trace_replay_block_transactions(block_number, ["stateDiff"])
            }
        )

    def fetch_transaction(self, tx_hash: str) -> TxData:
        tx = self.w3.eth.get_transaction(HexStr(tx_hash))
        return _attribute_dict_to_dict(tx)  # type: ignore

    def fetch_block_with_transactions(self, block_number: int) -> BlockWithTransactions:
        block: AttributeDict = self.w3.eth.eth_getBlockByNumber(hex(block_number), True)  # type: ignore
        return _attribute_dict_to_dict(block)

    def fetch_prestates(self, block_number: int) -> list[TxPrestate]:
        trace: list[AttributeDict] = self.w3.eth.debug_traceBlockByNumber(  # type: ignore
            hex(block_number), {"tracer": "prestateTracer"}
        )
        return [_attribute_dict_to_dict(prestate) for prestate in trace]

    def fetch_state_diffs(self, block_number: int) -> list[TxStateDiff]:
        trace: list[AttributeDict] = self.w3.eth.debug_traceBlockByNumber(  # type: ignore
            hex(block_number),
            {"tracer": "prestateTracer", "tracerConfig": {"diffMode": True}},
        )
        return [_attribute_dict_to_dict(statediff) for statediff in trace]

    def debug_trace_call_state_diffs(
        self,
        tx: TxData,
        block_number: int,
        state_overrides: WorldState,
        block_overrides: dict[str, str],
        tracing_type: Literal["state_diff"] | Literal["prestate"] | Literal["vmTrace"],
    ) -> PrePostState:
        overrides = dict(
            (key, account_state_to_override(acc))
            for key, acc in state_overrides.items()
        )
        options: dict = {
            "stateOverrides": overrides,
            "blockOverrides": block_overrides,
        }
        if tracing_type == "state_diff":
            options["tracer"] = "prestateTracer"
            options["tracerConfig"] = {"diffMode": True}
        elif tracing_type == "prestate":
            options["tracer"] = "prestateTracer"
            options["tracerConfig"] = {"diffMode": False}

        tx_params = tx_data_to_tx_params(tx)
        trace: AttributeDict = self.w3.eth.debug_traceCall(  # type: ignore
            tx_params, hex(block_number), options
        )

        return _attribute_dict_to_dict(trace)

    def debug_trace_transaction(self, tx_hash: str) -> dict:
        trace: AttributeDict = self.w3.eth.debug_traceTransaction(tx_hash)  # type: ignore
        return _attribute_dict_to_dict(trace)


def _attribute_dict_to_dict(attribute_dict: AttributeDict) -> Any:
    return json.loads(Web3.to_json(attribute_dict))  # type: ignore


def tx_data_to_tx_params(tx_data: TxData) -> TxParams:
    result: dict = deepcopy(tx_data)  # type: ignore
    # unused_keys = ['blockHash', 'blockNumber']
    result: TxParams = {  # type: ignore
        "accessList": tx_data.get("accessList"),
        "blobVersionedHashes": tx_data.get("blobVersionedHashes"),
        "chainId": tx_data["chainId"],
        "data": tx_data["input"],
        "from": tx_data["from"],
        "gas": tx_data["gas"],
        "gasPrice": tx_data["gasPrice"],
        "maxFeePerBlobGas": tx_data.get("maxFeePerBlobGas"),
        "maxFeePerGas": tx_data.get("maxFeePerGas"),
        "maxPriorityFeePerGas": tx_data.get("maxPriorityFeePerGas"),
        "nonce": tx_data["nonce"],
        "to": tx_data["to"],
        "type": tx_data["type"],
        "value": tx_data["value"],
    }
    for key, val in result.items():
        if isinstance(val, int):
            result[key] = hex(val)
    if result.get("type") == "0x2":
        del result["gasPrice"]
    else:
        del result["maxFeePerGas"]
        del result["maxFeePerBlobGas"]
        del result["maxPriorityFeePerGas"]
    return result


def account_state_to_override(account_state: AccountState) -> dict:
    result: dict = deepcopy(account_state)  # type: ignore
    if "nonce" in result:
        result["nonce"] = hex(result["nonce"])
    if "storage" in result:
        result["stateDiff"] = result["storage"]
        for slot, val in result["stateDiff"].items():
            # remove leading zeros, erigon does not like them
            result["stateDiff"][slot] = hex(int(val, 16))
        del result["storage"]
    return result
