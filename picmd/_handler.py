from dataclasses import dataclass
from inspect import signature
from typing import Callable, Union
from ._data import CommandRequest

HandleResult = Union[bool, int, float, str, bytes, None]

HandlerBothArgs = Callable[[bytes, int], HandleResult]
HandlerDataOnly = Callable[[bytes], HandleResult]
HandlerSizeOnly = Callable[[int], HandleResult]
HandlerNoArgs = Callable[[], HandleResult]
Handler = Union[HandlerBothArgs, HandlerDataOnly, HandlerSizeOnly, HandlerNoArgs]

@dataclass
class ArgumentConfig:
    need_data: bool = False
    need_size: bool = False

class HandlerArgument:

    def __init__(self, config: ArgumentConfig, data: bytes, size: int):
        self._config = config
        self._data = data
        self._size = size

    def __iter__(self):
        if self._config.need_data:
            yield self._data
        if self._config.need_size:
            yield self._size

class CommandHandler:

    _config: ArgumentConfig
    _handler: Handler

    def __init__(self, handler: Handler):
        self._handler = handler
        sig = signature(handler)
        need_data = 'data' in sig.parameters
        need_size = 'size' in sig.parameters
        self._config = ArgumentConfig(need_data, need_size)

    def execute(self, req: CommandRequest) -> HandleResult:
        args = HandlerArgument(self._config, req.data, req.size)
        return self._handler(*args)
