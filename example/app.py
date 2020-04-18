import time
from picmd import PiCmd

app = PiCmd.create('/dev/serial0')

@app.handler(0x01)
def greeting_handler(data: bytes, size: int) -> str:
    return 'hello world'

@app.handler(0x02)
def file_receive_handler(data: bytes, size: int):
    with open('./tmp/received-%s.bin' % int(time.time()), 'wb') as f:
        f.write(data)

app.run()
