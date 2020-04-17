import pytest
from picmd._util import calc_parity, data_to_bytes

def test_calc_parity():
    assert calc_parity(bytes([0x01])) == 0x01
    assert calc_parity(bytes([0x01, 0x02])) == 0x03
    assert calc_parity(bytes([0x01, 0x00, 0x01])) == 0x00
    assert calc_parity(bytes([0x01, 0x00, 0x00])) == 0x01
    assert calc_parity(bytes([0x01, 0x02, 0x03])) == 0x00
    assert calc_parity(bytes([0x01, 0x02, 0x04])) == 0x07
    assert calc_parity(bytes([0xff, 0x01, 0x01])) == 0xff

def test_data_to_bytes():
    assert data_to_bytes(None) == b''
    assert data_to_bytes(1) == b'\x01\x00\x00\x00\x00\x00\x00\x00'
    assert data_to_bytes(9223372036854775807) == b'\xff\xff\xff\xff\xff\xff\xff\x7f'
    assert data_to_bytes(9223372036854775808) == b'\x00\x00\x00\x00\x00\x00\x00\x80'
    assert data_to_bytes(1.0) == b'\x00\x00\x00\x00\x00\x00\xf0\x3f'
    assert data_to_bytes(True) == b'\x01'
    assert data_to_bytes(False) == b'\x00'
    assert data_to_bytes('ABC') == b'\x41\x42\x43'
    assert data_to_bytes(b'\x01\x02\x03') == b'\x01\x02\x03'

    with pytest.raises(ValueError):
        data_to_bytes([])
