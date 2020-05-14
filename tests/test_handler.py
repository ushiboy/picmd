from picmd._data import CommandRequest
from picmd._handler import CommandHandler

class Service:

    def greet(self):
        return 'hello'

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

def test_handle_execute_when_provide():
    expect_data = b'\x01\x02'
    expect_size = 2
    req = CommandRequest(0x01, expect_size, expect_data, 0x00)

    provided = {
        's1': 123,
        's2': 'abc',
        's3': Service()
    }

    def h1(data, size, s1):
        assert data == expect_data
        assert size == expect_size
        assert s1 == 123

    def h2(data, s2):
        assert data == expect_data
        assert s2 == 'abc'

    def h3(s1, s2, s3):
        assert s1 == 123
        assert s2 == 'abc'
        assert s3.greet() == 'hello'

    ch1 = CommandHandler(h1)
    ch1.execute(req, provided)

    ch2 = CommandHandler(h2)
    ch2.execute(req, provided)

    ch3 = CommandHandler(h3)
    ch3.execute(req, provided)
