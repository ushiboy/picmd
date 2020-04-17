from dataclasses import dataclass
from ._exception import InvalidParityException
from ._util import calc_parity

@dataclass
class Command:
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
class CommandResult:
    # 1byte
    status: int
    # any byte
    data: bytes = b''

    def to_bytes(self):
        size = len(self.data)
        t = bytes([self.status, size & 0xff00 >> 8, size >> 8]) + self.data
        return t + bytes([calc_parity(t)])
