JS_TRACER = """{
  calls: [],
  logs: [],
  call_context_stack: [0],
  call_context_counter: 0,
  reverted_call_contexts: [],
  children_of: {},

  location: function(log) {
    return {
        'address': toHex(log.contract.getAddress()),
        'pc': log.getPC(),
    }
  },

  enter: function(callFrame) {
    current_call_context = this.call_context_stack[this.call_context_stack.length - 1]
    this.call_context_counter += 1
    this.call_context_stack.push(this.call_context_counter)
    if (!this.children_of[current_call_context]) {
      this.children_of[current_call_context] = []
    }
    this.children_of[current_call_context].push(this.call_context_counter)
  },

  exit: function(frameResult) {
    context_id = this.call_context_stack.pop(this.call_context_counter)
    error = frameResult.getError()
    if (error) {
      this._revert(context_id)
    }
  },

  _revert: function(id) {
    // revert context and all of its sub contexts
    this.reverted_call_contexts.push(id)
    children = this.children_of[id] || []
    for (child_id of children) {
      this._revert(child_id)
    }
  },


  step: function(log, db) {
    opcode = log.op.toNumber()

    if (opcode == 0xF1 || opcode == 0xF2) {
        this.calls.push({
            'op': opcode,
            'sender': toHex(log.contract.getAddress()),
            'to': toHex(toAddress(log.stack.peek(1).toString(16))),
            'value': log.stack.peek(2).toString(16),
            'location': this.location(log),
            'call_context_id': this.call_context_stack[this.call_context_stack.length - 1],
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
            'call_context_id': this.call_context_stack[this.call_context_stack.length - 1],
        })
    }
  },

  fault: function(log, db) {},

  result: function(ctx, db) {
    if (ctx.error) {
      this._revert(0)
    }
    logs = this.logs.filter(log => !this.reverted_call_contexts.includes(log['call_context_id']))
    calls = this.calls.filter(call => !this.reverted_call_contexts.includes(call['call_context_id']))
    return {
      "gas": ctx.gasUsed,
      "calls": calls,
      "logs": logs,
      "reverted_call_contexts": this.reverted_call_contexts,
    };
  }
}"""
