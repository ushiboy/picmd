from ._const import PICMD_INVALID_FORMAT_ERROR, \
        PICMD_INVALID_PARITY_ERROR, \
        PICMD_COMMAND_NOT_FOUND_ERROR, \
        PICMD_INVALID_LENGTH_ERROR

class InvalidFormatException(Exception):
    """
    Invalid command format Error
    """
    status_code = PICMD_INVALID_FORMAT_ERROR

class InvalidParityException(Exception):
    """
    Parity does not match Error
    """
    status_code = PICMD_INVALID_PARITY_ERROR

class CommandNotFoundException(Exception):
    """
    Command not found Error
    """
    status_code = PICMD_COMMAND_NOT_FOUND_ERROR

class InvalidLengthException(Exception):
    """
    Invalid command length Error
    """
    status_code = PICMD_INVALID_LENGTH_ERROR

class InvalidResultFormatException(Exception):
    """
    Invalid result format Error
    """
