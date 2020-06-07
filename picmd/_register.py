from typing import List, Tuple, Callable
from ._handler import Handler

class HandlerRegister:

    _handlers: List[Tuple[int, Handler]]

    @property
    def handlers(self) -> List[Tuple[int, Handler]]:
        return self._handlers

    def __init__(self):
        self._handlers = []

    def handler(self, command: int) -> Callable[[Handler], Handler]:
        def decorator(f: Handler):
            self.add_handle_command(command, f)
            return f
        return decorator

    def add_handle_command(self, command: int, handle_func: Handler):
        if 0x00 <= command <= 0xff:
            self._handlers.append((command, handle_func))
        else:
            raise ValueError('command out of range 0x00 to 0xff [%s]' % command)
