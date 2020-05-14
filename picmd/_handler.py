from dataclasses import dataclass, field
from inspect import signature
from typing import Callable, Union, Dict, Any, Optional, List
from ._data import CommandRequest

Provided = Dict[str, Any]

HandleResult = Union[bool, int, float, str, bytes, None]

HandlerAnyArgs = Callable[..., HandleResult]
HandlerBothArgs = Callable[[bytes, int], HandleResult]
HandlerDataOnly = Callable[[bytes], HandleResult]
HandlerSizeOnly = Callable[[int], HandleResult]
HandlerNoArgs = Callable[[], HandleResult]
Handler = Union[HandlerAnyArgs, HandlerBothArgs, HandlerDataOnly, HandlerSizeOnly, HandlerNoArgs]

@dataclass
class ArgumentConfig:
    need_data: bool = False
    need_size: bool = False
    provided_keys: List[str] = field(default_factory=list)

def to_arguments(config: ArgumentConfig,
                 req: CommandRequest,
                 provided: Optional[Provided]) -> List[Any]:
    provided = provided if provided is not None else {}
    args: List[Any] = []
    if config.need_data:
        args.append(req.data)
    if config.need_size:
        args.append(req.size)
    for k in config.provided_keys:
        args.append(provided[k])
    return args

class CommandHandler:

    _config: ArgumentConfig
    _handler: Handler

    def __init__(self, handler: Handler):
        self._handler = handler
        sig = signature(handler)
        need_data = 'data' in sig.parameters
        need_size = 'size' in sig.parameters
        params = list(sig.parameters.keys())
        keys = list(filter(lambda x: x not in ('data', 'size'), params))
        self._config = ArgumentConfig(need_data, need_size, keys)

    def execute(self, req: CommandRequest, provided: Provided = None) -> HandleResult:
        args = to_arguments(self._config, req, provided)
        return self._handler(*args)
