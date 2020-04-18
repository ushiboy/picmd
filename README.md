pi-cmd
=====

pi-cmd is a framework for creating applications that request and respond to AT commands using serial communication.

Its main purpose is for use with Raspberry PI.

## Quick Sample

Create an instance of `PiCmd` with the `create` method and register the command handler with the `handler` decorator.

Start the application with the `run` method and wait for a command request.

```python
from picmd import PiCmd
import time

app = PiCmd.create('/dev/serial0')

@app.handler(0x01)
def handler(data: bytes, size: int) -> str:
    return 'hello world'

@app.handler(0x02)
def handler(data: bytes, size: int):
    with open('./tmp/received-%s.bin' % int(time.time()), 'wb') as f:
        f.write(data)

app.run()
```

## AT Command Format

(wip)

## Command Handler Interface

(wip)

```python
@app.handler(0x01)
def handler1(data: bytes, data_size: int) -> Union[bool, int, float, str, bytes, None]:
    ....
    return response_data
```

```python
@app.handler(0x02)
def handler2(data: bytes, data_size: int):
    ....
    # nothing return
```

```python
class DomainException(Exception):
    status_code = 0xff
    description = 'any error message'

@app.handler(0x03)
def handler3(data: bytes, data_size: int):
    ....
    raise DomainException
```

## API

(wip)

### PiCmd

#### PiCmd.create

#### handler

#### run

## Change Log

### 0.1.0

Initial release.

## License

MIT
