import os
from pathlib import Path
from typing import Iterable, Sequence

from tod_checker.currency_changes.currency_change import (
    CURRENCY_TYPE,
    LocatedCurrencyChange,
)
from tod_checker.currency_changes.events.event import CurrencyChangeEvent
from tod_checker.currency_changes.events.events_decoder import EventsDecoder
from tod_checker.currency_changes.events.tokens.erc_1155 import (
    ERC1155TransferBatchEvent,
    ERC1155TransferSingleEvent,
)
from tod_checker.currency_changes.events.tokens.erc_20 import ERC20TransferEvent
from tod_checker.currency_changes.events.tokens.erc_721 import ERC721TransferEvent
from tod_checker.currency_changes.events.tokens.erc_777 import (
    ERC777BurnedEvent,
    ERC777MintedEvent,
    ERC777SentEvent,
)
from tod_checker.currency_changes.tracer.js_trace_types import (
    JSTraceResult,
)
from tod_checker.currency_changes.tracer.tracer import JS_TRACER
from tod_checker.types.types import TxScenarioBundle

TRACER_PATH = Path(os.path.realpath(__file__)).parent / "tracer.js"


class CurrencyChangesJSTracer:
    def __init__(self) -> None:
        self._decoder = EventsDecoder(
            [
                ERC20TransferEvent,
                ERC721TransferEvent,
                ERC777MintedEvent,
                ERC777SentEvent,
                ERC777BurnedEvent,
                ERC1155TransferSingleEvent,
                ERC1155TransferBatchEvent,
            ]
        )

    def get_js_tracer(self) -> tuple[str, dict]:
        return JS_TRACER, {}

    def process_traces(
        self, traces: TxScenarioBundle[JSTraceResult]
    ) -> TxScenarioBundle[Sequence[LocatedCurrencyChange]]:
        return TxScenarioBundle(
            tx_a_normal=self.process_trace(traces.tx_a_normal),
            tx_a_reverse=self.process_trace(traces.tx_a_reverse),
            tx_b_normal=self.process_trace(traces.tx_b_normal),
            tx_b_reverse=self.process_trace(traces.tx_b_reverse),
        )

    def process_trace(self, trace: JSTraceResult) -> Sequence[LocatedCurrencyChange]:
        currency_changes: list[LocatedCurrencyChange] = []
        for call in trace["calls"]:
            value = int(call["value"], 16)
            currency_changes.append(
                {
                    "type": CURRENCY_TYPE.ETHER,
                    "currency_identifier": "Wei",
                    "owner": unify_hex_value(call["sender"]),
                    "change": -value,
                    "location": call["location"],
                },
            )
            currency_changes.append(
                {
                    "type": CURRENCY_TYPE.ETHER,
                    "currency_identifier": "Wei",
                    "owner": unify_hex_value(call["to"]),
                    "change": value,
                    "location": call["location"],
                },
            )

        for log in trace["logs"]:
            event = self._decoder.decode_event(
                unify_hex_values(log["topics"]),
                unify_hex_value(log["data"]),
                unify_hex_value(log["address"]),
            )
            if isinstance(event, CurrencyChangeEvent):
                currency_changes.extend(
                    [
                        {**c, "location": log["location"]}
                        for c in event.get_currency_changes()
                    ]
                )

        return currency_changes


def unify_hex_value(val: str):
    return val.lower().removeprefix("0x")


def unify_hex_values(values: Iterable[str]):
    return [unify_hex_value(v) for v in values]
