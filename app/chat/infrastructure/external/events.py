from chat.domain.interfaces.events import IEventDispatcher

class EventDispatcher(IEventDispatcher):
    def __init__(self):
        self._handlers = {}

    def register(self, event_type, handler):
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def dispatch(self, event):
        event_type = type(event)
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                result = handler(event)
                if hasattr(result, "__await__"):
                    await result