from dataclasses import dataclass
from typing import Sequence, TypedDict


class TraceLocation(TypedDict):
    address: str
    pc: int


class JSTraceResultCall(TypedDict):
    op: int
    sender: str
    to: str
    value: str
    location: TraceLocation


class JSTraceResultLog(TypedDict):
    topics: Sequence[str]
    data: str
    address: str
    location: TraceLocation


class JSTraceResult(TypedDict):
    gas: int
    calls: Sequence[JSTraceResultCall]
    logs: Sequence[JSTraceResultLog]
    reverted_call_contexts: Sequence[int]


@dataclass
class JSTracesBundle:
    tx_a_normal: JSTraceResult
    tx_a_reverse: JSTraceResult
    tx_b_normal: JSTraceResult
    tx_b_reverse: JSTraceResult
