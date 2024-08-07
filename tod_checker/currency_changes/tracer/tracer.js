{
  structLogs: [],
  calls: [],
  logs: [],
  errors: [],

  location: function(log) {
    return {
        'address': toHex(log.contract.getAddress()),
        'pc': log.getPC(),
    }
  },

  step: function(log, db) {
    opcode = log.op.toNumber()
    if (log.getError()) {
        errors.push(log.getError())
    }

    if (opcode == 0xF1 || opcode == 0xF2) {
        this.calls.push({
            'op': opcode,
            'sender': toHex(log.contract.getAddress()),
            'to': toHex(toAddress(log.stack.peek(1).toString(16))),
            'value': log.stack.peek(2).toString(16),
            'location': this.location(log),
        })
    }

    else if (opcode >= 0xA0 && opcode <= 0xA4) {
        offset = log.stack.peek(0).valueOf()
        size = log.stack.peek(1).valueOf()
        data = toHex(log.memory.slice(offset, offset + size))
        topics_amount = opcode - 0xA0
        topics = []
        for (i = 0; i < topics_amount; i++) {
            topics.push(log.stack.peek(2 + i).toString(16).padStart(64, "0"))
        }

        this.logs.push({
            'topics': topics,
            'data': data,
            'address': toHex(log.contract.getAddress()),
            'location': this.location(log),
        })
    }

    switch(log.op.toString()) {
    //   case "SSTORE":
    //     this.structLogs.push({"op": log.op.toString(), "stack": [log.stack.peek(1), log.stack.peek(0)], "depth": log.getDepth(), "contract": toHex(log.contract.getAddress()), "error": log.getError()});
    //     break;
    //   case "SLOAD":
    //     this.structLogs.push({"op": log.op.toString(), "stack": [log.stack.peek(0)], "depth": log.getDepth(), "contract": toHex(log.contract.getAddress()), "error": log.getError()});
    //     break;
    //   case "CREATE": case "CREATE2":
    //     this.structLogs.push({"op": log.op.toString(), "stack": [log.stack.peek(2), log.stack.peek(1), log.stack.peek(0)], "memory": toHex(log.memory.slice(log.stack.peek(1).valueOf(), log.stack.peek(1).valueOf() + log.stack.peek(2).valueOf())), "depth": log.getDepth(), "contract": toHex(log.contract.getAddress()), "error": log.getError()});
    //     break;
      case "CALL": case "CALLCODE":
        this.structLogs.push({"op": log.op.toString(), "stack": [log.stack.peek(4), log.stack.peek(3), log.stack.peek(2), toHex(toAddress(log.stack.peek(1).toString(16))), log.stack.peek(0)], "memory": toHex(log.memory.slice(log.stack.peek(3).valueOf(), log.stack.peek(3).valueOf() + log.stack.peek(4).valueOf())), "depth": log.getDepth(), "contract": toHex(log.contract.getAddress()), "error": log.getError()});
        break;
    //   case "DELEGATECALL": case "STATICCALL":
    //     this.structLogs.push({"op": log.op.toString(), "stack": [log.stack.peek(3), log.stack.peek(2), toHex(toAddress(log.stack.peek(1).toString(16))), log.stack.peek(0)], "memory": toHex(log.memory.slice(log.stack.peek(2).valueOf(), log.stack.peek(2).valueOf() + log.stack.peek(3).valueOf())), "depth": log.getDepth(), "contract": toHex(log.contract.getAddress()), "error": log.getError()});
    //     break;
    //   case "SELFDESTRUCT": case "SUICIDE":
    //     this.structLogs.push({"op": log.op.toString(), "stack": [db.getBalance(log.contract.getAddress()), toHex(toAddress(log.stack.peek(0).toString(16)))], "depth": log.getDepth(), "contract": toHex(log.contract.getAddress()), "error": log.getError()});
    //     break;
    //   case "LOG3":
    //     this.structLogs.push({"op": log.op.toString(), "stack": [toHex(toAddress(log.stack.peek(4).toString(16))), toHex(toAddress(log.stack.peek(3).toString(16))), log.stack.peek(2).toString(16), log.stack.peek(1), log.stack.peek(0)], "memory": toHex(log.memory.slice(log.stack.peek(0).valueOf(), log.stack.peek(0).valueOf() + log.stack.peek(1).valueOf())), "depth": log.getDepth(), "contract": toHex(log.contract.getAddress()), "error": log.getError()});
    //     break;
    //   case "SHA3":
    //     this.structLogs.push({"op": log.op.toString(), "stack": [log.stack.peek(1), log.stack.peek(0)], "depth": log.getDepth(), "contract": toHex(log.contract.getAddress()), "error": log.getError()});
    //     break;
    }
  },

  fault: function(log, db) {},

  result: function(ctx, db) {
    return {"gas": ctx.gasUsed, "calls": this.calls, "logs": this.logs };
  }
}