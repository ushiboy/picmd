from dataclasses import dataclass
from ._const import MAX_DATA_SIZE
from ._exception import InvalidParityException, \
        InvalidResultFormatException
from ._util import calc_parity

@dataclass
class CommandRequest:
    # 1byte
    command: int
    # 2byte
    size: int
    # <size>byte
    data: bytes
    # 1byte
    parity: int

    def validate(self):
        s1 = self.size & 0xff00 >> 8
        s2 = self.size >> 8
        t = bytes([self.command, s1, s2]) + self.data
        if self.parity != calc_parity(t):
            raise InvalidParityException

@dataclass
class CommandResponse:
    # 1byte
    status: int
    # any byte
    data: bytes = b''

    def to_bytes(self):
        size = len(self.data)
        t = bytes([self.status, size & 0xff00 >> 8, size >> 8]) + self.data
        return t + bytes([calc_parity(t)])

    def validate(self):
        if not 0x00 <= self.status <= 0xff:
            raise InvalidResultFormatException('unsupport status [%s]' % self.status)
        size = len(self.data)
        if size > MAX_DATA_SIZE:
            raise InvalidResultFormatException('over data size [%s]' % size)
