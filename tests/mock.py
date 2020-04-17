class MockSerial:

    @property
    def in_waiting(self):
        if self._cursor < len(self._buffer_datas):
            return len(self._buffer_datas[self._cursor])
        return 0

    def __init__(self, buffer_datas=None):
        if buffer_datas is None:
            buffer_datas = []
        self._buffer_datas = buffer_datas
        self._cursor = 0
        self.written_data = b''

    def read(self, size):
        # ignore size
        if self._cursor < len(self._buffer_datas):
            r = self._buffer_datas[self._cursor]
            self._cursor += 1
            return r
        return b''

    def write(self, data):
        self.written_data += data

    def close(self):
        pass
