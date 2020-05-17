import time
import pytest
from picmd._communicator import Communicator
from picmd._const import PICMD_NO_ERROR, \
        PICMD_COMMAND_FAIL_ERROR
from picmd._data import CommandResponse
from .mock import MockSerial

def test_send_result():
    s = MockSerial()
    c = Communicator(s)

    # OK case
    c.send_result(CommandResponse(PICMD_NO_ERROR, b'\x01'))
    assert s.written_data == b'*PIC:\x01\x01\x00\x01\x01\r\nOK\r\n'

    s.written_data = b''    # clear

    # ERROR case
    c.send_result(CommandResponse(PICMD_COMMAND_FAIL_ERROR))
    assert s.written_data == b'*PIC:\x06\x00\x00\x06\r\nERROR\r\n'

def test_communicate():
    s = MockSerial([
        b'AT*PIC=\x01\x01\x00\x02\x02\r\n'
        ])
    c = Communicator(s)
    c.start()
    time.sleep(0.1)
    c.stop()

    g = c.receive_command()
    rc = next(g)
    assert rc.command == 0x01
    assert rc.size == 0x01
    assert rc.data == b'\x02'
    assert rc.parity == 0x02

    with pytest.raises(StopIteration):
        next(g)

    assert s.written_data == b''    # no response

def test_communicate_when_invalid_length():
    s = MockSerial([
        b'AT*PIC=\x01\x01\x00\x02\x02\r?' # invalid end
        ])
    c = Communicator(s)
    c.start()
    time.sleep(0.1)
    c.stop()

    g = c.receive_command()
    with pytest.raises(StopIteration):
        next(g)

    assert s.written_data == b'*PIC:\x05\x00\x00\x05\r\nERROR\r\n'

def test_communicate_when_a_ping_command_is_received():
    s = MockSerial([
        b'AT\r\n'
        ])
    c = Communicator(s)
    c.start()
    time.sleep(0.1)
    c.stop()

    assert s.written_data == b'\r\nOK\r\n'
