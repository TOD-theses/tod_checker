from typing import Literal
from tod_checker.types.types import AccountState, PrePostState


def state_diff_fill_implicit_fields(state_diff: PrePostState) -> None:
    """
    Insert implicit fields, such that each field in pre has a corresponding field in post and vice versa.
    See https://geth.ethereum.org/docs/developers/evm-tracing/built-in-tracers#prestate-tracer
    """
    pre, post = state_diff["pre"], state_diff["post"]

    pre_addresses = set(pre.keys())
    post_addresses = set(post.keys())

    for deleted_addr in pre_addresses - post_addresses:
        post[deleted_addr] = account_deleted_state(pre[deleted_addr])

    for inserted_addr in post_addresses - pre_addresses:
        pre[inserted_addr] = account_inserted_state(post[inserted_addr])

    for modified_addr in pre_addresses & post_addresses:
        fill_implicit_prestate(pre[modified_addr], post[modified_addr])
        fill_poststate_with_unchanged_prestate(pre[modified_addr], post[modified_addr])

    for addr in pre_addresses | post_addresses:
        missing_fields = (set(pre[addr]) - set(post[addr])) | (
            set(post[addr]) - set(pre[addr])
        )
        if missing_fields:
            raise Exception(
                f"Failed to fill implicit fields {missing_fields} for {addr}: "
                + ", ".join(
                    [
                        f"{pre[addr].get(f)} vs {post[addr].get(f)}"
                        for f in missing_fields
                    ]
                )
            )


def fill_implicit_prestate(prestate: AccountState, poststate: AccountState):
    if "nonce" in poststate and "nonce" not in prestate:
        # it can happen that the prestate nonce is missing, despite not being 0 in the prestate
        # thus we only decrement by 1 and hope it's correct
        # see https://github.com/erigontech/erigon/pull/10961
        prestate["nonce"] = poststate["nonce"] - 1
    if "code" in poststate and "code" not in prestate:
        prestate["code"] = "0x"


def fill_poststate_with_unchanged_prestate(
    prestate: AccountState, poststate: AccountState
):
    if "balance" in prestate:
        poststate.setdefault("balance", prestate["balance"])
    if "code" in prestate:
        poststate.setdefault("code", prestate["code"])
    if "nonce" in prestate:
        poststate.setdefault("nonce", prestate["nonce"])
    if "storage" in prestate or "storage" in poststate:
        if "storage" not in prestate:
            prestate["storage"] = {}
        if "storage" not in poststate:
            poststate["storage"] = {}
        keys_prestate = prestate["storage"].keys()
        keys_poststate = poststate["storage"].keys()
        added_slots = keys_poststate - keys_prestate
        removed_slots = keys_prestate - keys_poststate

        for key in added_slots:
            prestate["storage"][key] = "0x0"
        for key in removed_slots:
            poststate["storage"][key] = "0x0"


def account_inserted_state(poststate: AccountState):
    prestate: AccountState = {}
    if "balance" in poststate:
        # not precise, balance could exist before account creation
        prestate["balance"] = "0x0"
    if "code" in poststate:
        prestate["code"] = "0x0"
    if "nonce" in poststate:
        prestate["nonce"] = 0
    if "storage" in poststate:
        prestate["storage"] = {}
        for key in poststate["storage"]:
            prestate["storage"][key] = "0x0"
    return prestate


def account_deleted_state(prestate: AccountState):
    poststate: AccountState = {}
    if "balance" in prestate:
        poststate["balance"] = "0x0"
    if "code" in prestate:
        poststate["code"] = "0x0"
    if "nonce" in prestate:
        poststate["nonce"] = 0
    if "storage" in prestate:
        poststate["storage"] = {}
        for key in prestate["storage"]:
            poststate["storage"][key] = "0x0"
    return poststate


def state_diff_remove_unchanged_fields(state_diff: PrePostState) -> None:
    """
    Remove fields that did not change between pre and post.
    Ignores storage, as these should not be equal in pre and post.
    """
    pre = state_diff["pre"]
    post = state_diff["post"]

    for addr, prestate in pre.items():
        poststate = post[addr]

        types: list[Literal["balance"] | Literal["code"] | Literal["nonce"]] = [
            "balance",
            "code",
            "nonce",
        ]

        for type in types:
            if type in prestate and type in poststate:
                if prestate.get(type) == poststate.get(type):
                    del prestate[type]
                    del poststate[type]
