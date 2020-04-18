import binascii
import struct
from threading import Thread
from queue import Queue
from serial import Serial

class SerialCommunicator:

    def __init__(self, conn):
        self._queue = Queue()
        self._conn = conn
        self._th = None
        self._alive = False

    def start(self):
        self._alive = True
        self._th = Thread(target=self._process, daemon=True)
        self._th.start()
        return self

    def stop(self):
        self._alive = False
        self._th.join()
        self._th = None
        self._conn.close()

    def sync_read_rx(self):
        return self._queue.get()

    def send_tx(self, data):
        self._conn.write(data)

    def _process(self):
        conn = self._conn
        buf = b''
        while self._alive:
            c = conn.read(conn.in_waiting or 1)
            if c:
                buf += c
                p = buf.find(b'\r\nOK\r\n')
                p = p if p >= -1 else buf.find(b'\r\nERROR\r\n')
                if p >= 0:
                    t = buf[:p]
                    buf = b''
                    self._queue.put(t)

    @classmethod
    def connect(cls, port):
        conn = Serial(port=port, baudrate=115200, timeout=1)
        return cls(conn).start()

def parse_result(d):
    t = d[5:]
    command = t[0]
    size = struct.unpack('<H', t[1:3])[0]
    data = t[3:3 + size]
    parity = int.from_bytes(t[3+size:], 'big')
    return command, size, data, parity == calc_parity(t[:-1])

def calc_parity(values):
    parity = 0x00
    for value in values:
        parity ^= value
    return parity


s = SerialCommunicator.connect('/dev/ttyUSB0')

s.send_tx(b'AT*CMD=01000001\r\n')
r1 = s.sync_read_rx()
print(parse_result(r1)) # (1, 11, b'hello world', True)

with open('./data.dat', 'rb') as f:
    buff = f.read()
    buff_size = len(buff)
    tx_data = bytes([0x02]) + struct.pack('<H', buff_size) + buff
    s.send_tx(b'AT*CMD=')
    s.send_tx(binascii.b2a_hex(tx_data + bytes([calc_parity(tx_data)])))
    s.send_tx(b'\r\n')

r2 = s.sync_read_rx()
print(parse_result(r2)) # (1, 0, b'', True)

s.stop()
