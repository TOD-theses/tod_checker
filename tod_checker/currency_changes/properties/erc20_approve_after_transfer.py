from typing import Iterable, Sequence, TypedDict

from tod_checker.currency_changes.events.event import Event
from tod_checker.currency_changes.events.tokens.erc_20 import (
    ERC20ApprovalEvent,
    ERC20TransferEvent,
)


class ERC20ApprovalProperties(TypedDict):
    approve_after_transfer: bool


class ERC20ApprovalWitnesses(TypedDict):
    transfer_approval_pairs: Sequence[dict]


class ERC20ApprovalCheckResult(TypedDict):
    properties: ERC20ApprovalProperties
    witnesses: ERC20ApprovalWitnesses


def check_erc20_approval_attack(
    events_tx_a: Iterable[Event],
    events_tx_b: Iterable[Event],
    events_tx_b_reverse: Iterable[Event],
) -> ERC20ApprovalCheckResult:
    matches = [
        *match_transfers_with_approvals(events_tx_a, events_tx_b, events_tx_b_reverse)
    ]

    witnesses = events_to_witnesses(matches)

    return {
        "properties": {
            "approve_after_transfer": len(witnesses) > 0,
        },
        "witnesses": {
            "transfer_approval_pairs": witnesses,
        },
    }


def match_transfers_with_approvals(
    events_tx_a: Iterable[Event],
    events_tx_b: Iterable[Event],
    events_tx_b_reverse: Iterable[Event],
) -> Iterable[tuple[ERC20TransferEvent, ERC20ApprovalEvent]]:
    transfers_a = [e for e in events_tx_a if isinstance(e, ERC20TransferEvent)]
    approvals_b = [e for e in events_tx_b if isinstance(e, ERC20ApprovalEvent)]
    approvals_b_reverse = [
        e for e in events_tx_b_reverse if isinstance(e, ERC20ApprovalEvent)
    ]

    for transfer in transfers_a:
        for approval in approvals_b:
            # Transfer matches Approval
            if transfer_matches_approval(transfer, approval):
                # Approval is independent of transaction order
                if any(approvals_equal(approval, x) for x in approvals_b_reverse):
                    yield transfer, approval


def transfer_matches_approval(
    transfer: ERC20TransferEvent, approval: ERC20ApprovalEvent
) -> bool:
    return (
        transfer.sender == approval.owner
        and transfer.to == approval.spender
        and transfer.token_address == approval.token_address
    )


def approvals_equal(a: ERC20ApprovalEvent, b: ERC20ApprovalEvent) -> bool:
    return (
        a.spender == b.spender
        and a.owner == b.owner
        and a.value == b.value
        and a.token_address == b.token_address
    )


def events_to_witnesses(
    matches: Iterable[tuple[ERC20TransferEvent, ERC20ApprovalEvent]],
):
    return [
        {
            "transfer": {
                "from": transfer.sender,
                "to": transfer.to,
                "value": transfer.value,
                "token": transfer.token_address,
            },
            "approval": {
                "owner": approval.owner,
                "spender": approval.spender,
                "value": approval.value,
                "token": approval.token_address,
            },
        }
        for transfer, approval in matches
    ]
