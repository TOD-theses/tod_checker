from typing import Sequence
from tod_checker.currency_changes.events.event import Event


class EventDecodingException(Exception):
    pass


class EventsDecoder:
    def __init__(self, events: Sequence[type[Event]]) -> None:
        self._events = events

    def decode_event(self, topics: Sequence[str], data: str, storage_address: str):
        if not topics:
            raise EventDecodingException("Can not decode event without any topic")
        for event in self._events:
            if event.can_decode(topics, data):
                return event.decode(topics, data, storage_address)
