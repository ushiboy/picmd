import binascii
import struct
from typing import Union

def calc_parity(values: bytes) -> int:
    parity = 0x00
    for value in values:
        parity ^= value
    return parity


def data_to_bytes(data: Union[bool, int, float, str, bytes, None]) -> bytes:
    if data is None:
        result = b''
    elif isinstance(data, bool):
        result = struct.pack('<?', data)
    elif isinstance(data, int):
        if data > 9223372036854775807:
            result = struct.pack('<Q', data)
        else:
            result = struct.pack('<q', data)
    elif isinstance(data, float):
        result = struct.pack('<d', data)
    elif isinstance(data, str):
        result = binascii.unhexlify(data.encode('utf-8').hex())
    elif isinstance(data, bytes):
        result = data
    else:
        raise ValueError('Unsupported Type %s' % data.__class__)
    return result
