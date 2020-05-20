from typing import Optional
import struct
from ._const import CMD_PREFIX, \
        CMD_PREFIX_LEN, \
        CMD_END, \
        CMD_END_LEN, \
        CMD_LEN, \
        CMD_DATA_SIZE_LEN, \
        CMD_PARITY_LEN, \
        MAX_DATA_SIZE, \
        CMD_PING
from ._data import CommandRequest
from ._exception import InvalidLengthException

CMD_STATIC_SIZE = CMD_PREFIX_LEN + CMD_LEN + CMD_DATA_SIZE_LEN
UNINITIALIZED_DATA_SIZE = MAX_DATA_SIZE + 1

class ATCommandReceiver:

    _ready_to_receive_command: bool
    _cur_cmd_data_size: int
    _buffered: bytes
    _buffered_size: int
    _should_pong: bool

    @property
    def cur_cmd_data_size(self):
        return self._cur_cmd_data_size

    @property
    def buffered_size(self):
        return self._buffered_size

    @property
    def should_pong(self):
        return self._should_pong

    def __init__(self):
        self._ready_to_receive_command = False
        self._buffered = b''
        self._cur_cmd_data_size = UNINITIALIZED_DATA_SIZE
        self._buffered_size = len(self._buffered)
        self._should_pong = False

    def store_buff(self, buff: bytes):
        if len(buff) == 0:
            return
        self._buffered += buff
        self._buffered_size = len(self._buffered)

        if not self._ready_to_receive_command:
            p = self._buffered.find(CMD_PREFIX)
            if p < 0:
                p = self._buffered.find(CMD_PING)
                if p > -1:
                    self._should_pong = True
                    self._buffered = self._buffered[p + len(CMD_PING):]
                    self._buffered_size = len(self._buffered)
                return
            self._ready_to_receive_command = True
            self._buffered = self._buffered[p:]
            self._buffered_size = len(self._buffered)

        if self._cur_cmd_data_size == UNINITIALIZED_DATA_SIZE and \
                self._buffered_size >= CMD_STATIC_SIZE:
            t = self._buffered[CMD_PREFIX_LEN + CMD_LEN: CMD_STATIC_SIZE]
            self._cur_cmd_data_size = struct.unpack('<H', t)[0]

    def pull_received_command(self) -> Optional[CommandRequest]:
        d_end = CMD_STATIC_SIZE + self._cur_cmd_data_size
        p_end = d_end + CMD_PARITY_LEN
        end = p_end + CMD_END_LEN

        # check size
        if self._buffered_size < end:
            return None

        buf = self._buffered
        size = self._cur_cmd_data_size

        # reset state
        self._ready_to_receive_command = False
        self._buffered = self._buffered[end:]
        self._cur_cmd_data_size = UNINITIALIZED_DATA_SIZE
        self._buffered_size = len(self._buffered)

        # check end
        if buf[p_end: end] != CMD_END:
            raise InvalidLengthException

        c = buf[CMD_PREFIX_LEN: CMD_PREFIX_LEN + CMD_LEN]
        p = buf[d_end: p_end]

        cmd = int.from_bytes(c, 'big')
        data = buf[CMD_STATIC_SIZE: d_end]
        parity = int.from_bytes(p, 'big')
        return CommandRequest(cmd, size, data, parity)

    def reset_pong(self):
        self._should_pong = False
