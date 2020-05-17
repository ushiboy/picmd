from threading import Thread
from typing import Optional, Dict
from queue import Queue
from serial import Serial # type: ignore
from ._const import PICMD_NO_ERROR, \
        CMD_RESULT_PREFIX, \
        CMD_RESULT_OK, \
        CMD_RESULT_ERROR
from ._data import CommandResponse
from ._exception import InvalidLengthException
from ._receiver import ATCommandReceiver

class Communicator:

    _conn: Serial
    _th: Optional[Thread]
    _alive: bool
    _queue: Queue

    _END_GENERATE: Dict = {}

    def __init__(self, conn: Serial):
        self._conn = conn
        self._th = None
        self._alive = False
        self._queue = Queue()
        self._generator = self._make_generator()

    def start(self):
        self._alive = True
        self._th = Thread(target=self._process, daemon=True)
        self._th.start()
        return self

    def stop(self):
        self._queue.put(self._END_GENERATE)
        self._alive = False
        self._conn.close()
        self._th.join()
        self._th = None

    def receive_command(self):
        return self._generator

    def send_result(self, result: CommandResponse):
        self._conn.write(CMD_RESULT_PREFIX)
        self._conn.write(result.to_bytes())
        if result.status == PICMD_NO_ERROR:
            self._conn.write(CMD_RESULT_OK)
        else:
            self._conn.write(CMD_RESULT_ERROR)

    def _process(self):
        at = ATCommandReceiver()
        while self._alive:
            try:
                at.store_buff(self._conn.read(self._conn.in_waiting or 1))
                if at.should_pong:
                    at.reset_pong()
                    self._send_pong()
                    continue
                cmd = at.pull_received_command()
                if cmd is not None:
                    self._queue.put(cmd)
            except InvalidLengthException as e:
                self.send_result(CommandResponse(e.status_code))

    def _send_pong(self):
        self._conn.write(CMD_RESULT_OK)

    def _make_generator(self):
        while True:
            q = self._queue.get()
            if q is self._END_GENERATE:
                return
            yield q

    @classmethod
    def create(cls, port: str):
        return cls(Serial(port, 115200, timeout=1.0))
