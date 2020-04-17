from picmd._const import PICMD_INVALID_FORMAT_ERROR, \
        PICMD_INVALID_PARITY_ERROR, \
        PICMD_COMMAND_NOT_FOUND_ERROR, \
        PICMD_INVALID_LENGTH_ERROR
from picmd._exception import InvalidFormatException, \
        InvalidParityException, \
        CommandNotFoundException, \
        InvalidLengthException


def test_invalid_format_exception():
    e = InvalidFormatException()
    assert e.status_code == PICMD_INVALID_FORMAT_ERROR

def test_invalid_parity_exception():
    e = InvalidParityException()
    assert e.status_code == PICMD_INVALID_PARITY_ERROR

def test_command_not_found_exception():
    e = CommandNotFoundException()
    assert e.status_code == PICMD_COMMAND_NOT_FOUND_ERROR

def test_invalid_length_exception():
    e = InvalidLengthException()
    assert e.status_code == PICMD_INVALID_LENGTH_ERROR
