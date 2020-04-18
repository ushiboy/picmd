import logging
from typing import Dict, Callable
from ._communicator import Communicator
from ._const import PICMD_NO_ERROR, \
        PICMD_COMMAND_FAIL_ERROR
from ._data import Command, CommandResponse
from ._exception import CommandNotFoundException, \
        InvalidResultFormatException
from ._util import data_to_bytes

log = logging.getLogger(__name__)

class PiCmd:

    _comm: Communicator
    _command_handlers: Dict

    def __init__(self, comm: Communicator):
        self._command_handlers = {}
        self._comm = comm

    def handler(self, command: int):
        def decorator(f):
            self.add_handle_command(command, f)
            return f
        return decorator

    def add_handle_command(self, command: int, handle_func):
        self._command_handlers[command] = handle_func

    def run(self):
        self._comm.start()
        try:
            for c in self._comm.receive_command():
                self._comm.send_result(self.execute_command(c))
        except KeyboardInterrupt:
            self._comm.stop()

    def execute_command(self, command: Command) -> CommandResponse:
        status = PICMD_NO_ERROR
        data = b''
        try:
            command.validate()
            h = self.get_handler(command)
            result = h(command.data, command.size)
            data = data_to_bytes(result)
        except Exception as e:
            if hasattr(e, 'status_code'):
                status = e.status_code  # type: ignore
            else:
                status = PICMD_COMMAND_FAIL_ERROR
            if hasattr(e, 'description'):
                data = data_to_bytes(e.description) # type: ignore

        r = CommandResponse(status, data)
        try:
            r.validate()
        except InvalidResultFormatException as e:
            log.error(e)
            r = CommandResponse(PICMD_COMMAND_FAIL_ERROR)
        return r

    def get_handler(self, command: Command) -> Callable:
        if command.command not in self._command_handlers:
            raise CommandNotFoundException
        return self._command_handlers[command.command]

    @classmethod
    def create(cls, serial_port: str):
        return cls(Communicator.create(serial_port))
