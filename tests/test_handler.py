import pytest
from picmd._data import CommandRequest
from picmd._handler import CommandHandler

def test_handle_execute():

    expect_data = b'\x01\x02'
    expect_size = 2

    req = CommandRequest(0x01, expect_size, expect_data, 0x00)

    def h1(data, size):
        assert data == expect_data
        assert size == expect_size

    def h2(data):
        assert data == expect_data

    def h3(size):
        assert size == expect_size

    def h4():
        return 'ok'

    ch1 = CommandHandler(h1)
    ch1.execute(req)

    ch2 = CommandHandler(h2)
    ch2.execute(req)

    ch3 = CommandHandler(h3)
    ch3.execute(req)

    ch4 = CommandHandler(h4)
    assert ch4.execute(req) == 'ok'
