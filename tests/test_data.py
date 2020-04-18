import pytest
from picmd._data import Command, CommandResponse
from picmd._exception import InvalidParityException, \
        InvalidResultFormatException

def test_command_validate():
    c = Command(0x01, 8, b'\x01\x00\x00\x00\x00\x00\x00\x00', 0x08)
    c.validate()

    with pytest.raises(InvalidParityException):
        c = Command(0x01, 8, b'\x01\x00\x00\x00\x00\x00\x00\x00', 0x09)
        c.validate()

def test_command_result_to_bytes():
    r = CommandResponse(0x01, b'\x01\x00\x00\x00\x00\x00\x00\x00')
    assert r.to_bytes() == b'\x01\x08\x00\x01\x00\x00\x00\x00\x00\x00\x00\x08'


def test_command_result_validate():
    CommandResponse(0x00).validate()

    with pytest.raises(InvalidResultFormatException):
        CommandResponse(0x100).validate()

    CommandResponse(0xff, b'\x00' * 0xffff).validate()

    with pytest.raises(InvalidResultFormatException):
        CommandResponse(0x01, b'\x00' * (0xffff + 1)).validate()
