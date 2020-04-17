from .mock import MockSerial

def test_in_waiting():
    m = MockSerial([
        b'1',
        b'22',
        b'333'
        ])

    assert m.in_waiting == 1
    m.read(1)
    assert m.in_waiting == 2
    m.read(1)
    assert m.in_waiting == 3
    m.read(1)
    assert m.in_waiting == 0

def test_read():
    m = MockSerial([
        b'1',
        b'2',
        b'3'
        ])

    assert m.read(1) == b'1'
    assert m.read(1) == b'2'
    assert m.read(1) == b'3'
    assert m.read(1) == b''

def test_write():
    m = MockSerial()

    assert m.written_data == b''
    m.write(b'1234')
    assert m.written_data == b'1234'
    m.write(b'5678')
    assert m.written_data == b'12345678'
