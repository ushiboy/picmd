import pytest
from picmd._exception import InvalidFormatException, \
        InvalidLengthException
from picmd._receiver import ATCommandReceiver, UNINITIALIZED_DATA_SIZE


def test_store_buff():
    r = ATCommandReceiver()
    assert r.cur_cmd_data_size == UNINITIALIZED_DATA_SIZE
    assert r.buffered_size == 0

    # append empty
    r.store_buff(b'')
    assert r.cur_cmd_data_size == UNINITIALIZED_DATA_SIZE
    assert r.buffered_size == 0

    # append noise
    r.store_buff(b'00000')
    assert r.cur_cmd_data_size == UNINITIALIZED_DATA_SIZE
    assert r.buffered_size == 5

    # append piece of command prefix
    r.store_buff(b'AT*')
    assert r.cur_cmd_data_size == UNINITIALIZED_DATA_SIZE
    assert r.buffered_size == 8

    # append piece of command prefix
    r.store_buff(b'CMD=')
    assert r.cur_cmd_data_size == UNINITIALIZED_DATA_SIZE
    assert r.buffered_size == 7 # cut noise

    # append command
    r.store_buff(b'01')
    assert r.cur_cmd_data_size == UNINITIALIZED_DATA_SIZE
    assert r.buffered_size == 9

    # append data size low
    r.store_buff(b'ff')
    assert r.cur_cmd_data_size == UNINITIALIZED_DATA_SIZE
    assert r.buffered_size == 11

    # append data size high
    r.store_buff(b'00')
    assert r.cur_cmd_data_size == 255
    assert r.buffered_size == 13

    # append data buffer
    r.store_buff(b'0000')
    assert r.cur_cmd_data_size == 255 # not change
    assert r.buffered_size == 17

def test_store_buff_when_invalid_data_size():
    r = ATCommandReceiver()
    assert r.cur_cmd_data_size == UNINITIALIZED_DATA_SIZE
    assert r.buffered_size == 0

    r.store_buff(b'AT*CMD=01')
    assert r.cur_cmd_data_size == UNINITIALIZED_DATA_SIZE
    assert r.buffered_size == 9

    with pytest.raises(InvalidFormatException):
        r.store_buff(b'ZZZZ')
    assert r.cur_cmd_data_size == UNINITIALIZED_DATA_SIZE
    assert r.buffered_size == 0 # reset

def test_pull_received_command():
    r1 = ATCommandReceiver()
    assert r1.pull_received_command() is None
    assert r1.cur_cmd_data_size == UNINITIALIZED_DATA_SIZE
    assert r1.buffered_size == 0

    r1.store_buff(b'AT*CMD=01000001\r')
    assert r1.pull_received_command() is None
    assert r1.cur_cmd_data_size == 0
    assert r1.buffered_size == 16

    r1.store_buff(b'\n')
    c1 = r1.pull_received_command()
    assert c1.command == 0x01
    assert c1.size == 0x00
    assert c1.data == b''
    assert c1.parity == 0x01
    assert r1.cur_cmd_data_size == UNINITIALIZED_DATA_SIZE # reset
    assert r1.buffered_size == 0 # change


    r2 = ATCommandReceiver()
    r2.store_buff(b'AT*CMD=0101000202\r\nAT*CMD=')
    assert r2.cur_cmd_data_size == 1
    assert r2.buffered_size == 26

    c2 = r2.pull_received_command()
    assert c2.command == 0x01
    assert c2.size == 0x01
    assert c2.data == b'\x02'
    assert c2.parity == 0x02
    assert r2.cur_cmd_data_size == UNINITIALIZED_DATA_SIZE # reset
    assert r2.buffered_size == 7 # change


    r3 = ATCommandReceiver()
    r3.store_buff(b'AT*CMD=0101000202\r?AT*CMD=')
    with pytest.raises(InvalidLengthException):
        r3.pull_received_command()
    assert r3.cur_cmd_data_size == UNINITIALIZED_DATA_SIZE # reset
    assert r3.buffered_size == 7 # change

def test_pull_received_command_when_invalid_command():
    r1 = ATCommandReceiver()
    r1.store_buff(b'AT*CMD=ZZ000001\r\n')

    with pytest.raises(InvalidFormatException):
        r1.pull_received_command()
    assert r1.cur_cmd_data_size == UNINITIALIZED_DATA_SIZE # reset
    assert r1.buffered_size == 0 # change

def test_pull_received_command_when_invalid_data():
    r1 = ATCommandReceiver()
    r1.store_buff(b'AT*CMD=010100ZZ01\r\n')

    with pytest.raises(InvalidFormatException):
        r1.pull_received_command()
    assert r1.cur_cmd_data_size == UNINITIALIZED_DATA_SIZE # reset
    assert r1.buffered_size == 0 # change

def test_pull_received_command_when_invalid_parity():
    r1 = ATCommandReceiver()
    r1.store_buff(b'AT*CMD=010000ZZ\r\n')

    with pytest.raises(InvalidFormatException):
        r1.pull_received_command()
    assert r1.cur_cmd_data_size == UNINITIALIZED_DATA_SIZE # reset
    assert r1.buffered_size == 0 # change
