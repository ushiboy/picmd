from threading import Thread
import time
import pytest
from picmd._communicator import Communicator
from picmd._const import PICMD_NO_ERROR, \
        PICMD_INVALID_PARITY_ERROR, \
        PICMD_COMMAND_FAIL_ERROR
from picmd._data import CommandRequest
from picmd._exception import CommandNotFoundException
from picmd._picmd import PiCmd
from .mock import MockSerial


class DomainException(Exception):
    status_code = 0xff
    description = 'domain error'

class InvalidStatusCodeException(Exception):
    status_code = 0xff + 1

class InvalidDescriptionException(Exception):
    description = b'\x00' * (0xffff + 1)

def test_handler():
    p = PiCmd(Communicator(MockSerial()))

    @p.handler(0x01)
    def h1(data, size):
        pass

    with pytest.raises(ValueError):
        @p.handler(256)
        def h2(data, size):
            pass


def test_execute_command():
    p = PiCmd(Communicator(MockSerial()))

    @p.handler(0x01)
    def h1(data, size):
        return 1

    @p.handler(0x02)
    def h2(data, size):
        raise Exception

    @p.handler(0x03)
    def h3(data, size):
        raise DomainException

    c1 = CommandRequest(0x01, 1, b'\x01', 0x01)
    r1 = p.execute_command(c1)
    assert r1.status == PICMD_NO_ERROR
    assert r1.data == b'\x01\x00\x00\x00\x00\x00\x00\x00'

    c2 = CommandRequest(0x01, 0, b'', 0x02) # invalid parity
    r2 = p.execute_command(c2)
    assert r2.status == PICMD_INVALID_PARITY_ERROR
    assert r2.data == b''

    c3 = CommandRequest(0x02, 0, b'', 0x02)
    r3 = p.execute_command(c3)
    assert r3.status == PICMD_COMMAND_FAIL_ERROR
    assert r3.data == b''

    c4 = CommandRequest(0x03, 0, b'', 0x03)
    r4 = p.execute_command(c4)
    assert r4.status == 0xff
    assert r4.data == b'domain error'

def test_execute_command_when_invalid_result_format():
    p = PiCmd(Communicator(MockSerial()))

    @p.handler(0x01)
    def h1(data, size):
        return b'\x00' * (0xffff + 1) # over data size

    @p.handler(0x02)
    def h2(data, size):
        raise InvalidStatusCodeException

    @p.handler(0x03)
    def h3(data, size):
        raise InvalidDescriptionException

    r1 = p.execute_command(CommandRequest(0x01, 0, b'', 0x01))
    assert r1.status == PICMD_COMMAND_FAIL_ERROR
    assert r1.data == b''

    r2 = p.execute_command(CommandRequest(0x02, 0, b'', 0x02))
    assert r2.status == PICMD_COMMAND_FAIL_ERROR
    assert r2.data == b''

    r3 = p.execute_command(CommandRequest(0x03, 0, b'', 0x03))
    assert r3.status == PICMD_COMMAND_FAIL_ERROR
    assert r3.data == b''

def test_get_handler():
    p = PiCmd(Communicator(MockSerial()))

    @p.handler(0x01)
    def h1(data, size):
        return 1

    assert p.get_handler(CommandRequest(0x01, 0, b'', 0x01)) is not None

    with pytest.raises(CommandNotFoundException):
        p.get_handler(CommandRequest(0x02, 0, b'', 0x02))

def test_picmd_runner():
    s = MockSerial([
        b'AT*CMD=0101000202\r\n'
        ])
    c = Communicator(s)
    p = PiCmd(c)

    @p.handler(0x01)
    def h1(data, size):
        return 1

    Thread(target=p.run, daemon=True).start()
    time.sleep(0.1)
    c.stop()

    assert s.written_data == b'*CMD=\x01\x08\x00\x01\x00\x00\x00\x00\x00\x00\x00\x08\r\nOK\r\n'
