import pytest
from picmd._exception import InvalidLengthException
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
    r.store_buff(b'PIC=')
    assert r.cur_cmd_data_size == UNINITIALIZED_DATA_SIZE
    assert r.buffered_size == 7 # cut noise

    # append command
    r.store_buff(b'\x01')
    assert r.cur_cmd_data_size == UNINITIALIZED_DATA_SIZE
    assert r.buffered_size == 8

    # append data size low
    r.store_buff(b'\xff')
    assert r.cur_cmd_data_size == UNINITIALIZED_DATA_SIZE
    assert r.buffered_size == 9

    # append data size high
    r.store_buff(b'\x00')
    assert r.cur_cmd_data_size == 255
    assert r.buffered_size == 10

    # append data buffer
    r.store_buff(b'\x00\x00')
    assert r.cur_cmd_data_size == 255 # not change
    assert r.buffered_size == 12

def test_store_buff_when_ping():
    a1 = ATCommandReceiver()
    assert a1.should_pong == False
    a1.store_buff(b'AT\r\n')
    assert a1.should_pong == True

    a2 = ATCommandReceiver()
    a2.store_buff(b'AT\r')
    assert a2.should_pong == False
    a2.store_buff(b'\n')
    assert a2.should_pong == True

    a3 = ATCommandReceiver()
    a3.store_buff(b'AT*PIC=\x01\x04\x00AT\r\n\x17\r\n')
    assert a3.cur_cmd_data_size == 4
    assert a3.buffered_size == 17
    assert a3.should_pong == False

def test_pull_received_command():
    r1 = ATCommandReceiver()
    assert r1.pull_received_command() is None
    assert r1.cur_cmd_data_size == UNINITIALIZED_DATA_SIZE
    assert r1.buffered_size == 0

    r1.store_buff(b'AT*PIC=\x01\x00\x00\x01\r')
    assert r1.pull_received_command() is None
    assert r1.cur_cmd_data_size == 0
    assert r1.buffered_size == 12

    r1.store_buff(b'\n')
    c1 = r1.pull_received_command()
    assert c1.command == 0x01
    assert c1.size == 0x00
    assert c1.data == b''
    assert c1.parity == 0x01
    assert r1.cur_cmd_data_size == UNINITIALIZED_DATA_SIZE # reset
    assert r1.buffered_size == 0 # change


    r2 = ATCommandReceiver()
    r2.store_buff(b'AT*PIC=\x01\x01\x00\x02\x02\r\nAT*PIC=')
    assert r2.cur_cmd_data_size == 1
    assert r2.buffered_size == 21

    c2 = r2.pull_received_command()
    assert c2.command == 0x01
    assert c2.size == 0x01
    assert c2.data == b'\x02'
    assert c2.parity == 0x02
    assert r2.cur_cmd_data_size == UNINITIALIZED_DATA_SIZE # reset
    assert r2.buffered_size == 7 # change


    r3 = ATCommandReceiver()
    r3.store_buff(b'AT*PIC=\x01\x01\x00\x02\x02\r?AT*PIC=')
    with pytest.raises(InvalidLengthException):
        r3.pull_received_command()
    assert r3.cur_cmd_data_size == UNINITIALIZED_DATA_SIZE # reset
    assert r3.buffered_size == 7 # change

def test_reset_pong():
    a1 = ATCommandReceiver()
    a1.store_buff(b'AT\r\n')
    assert a1.should_pong == True

    a1.reset_pong()
    assert a1.should_pong == False
