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
def greeting_handler(data: bytes, size: int) -> str:
    return 'hello world'

@app.handler(0x02)
def file_receive_handler(data: bytes, size: int):
    with open('./tmp/received-%s.bin' % int(time.time()), 'wb') as f:
        f.write(data)

app.run()
```

## AT Command Format

### Command Request (Client -> Application)

Hexadecimal data starting with `AT*PIC=` and ending with `CRLF`.

The command type is specified by the first 8 bits.

The command parameter size is represented by the second 16 bits. Then there is the content of the command parameters.

The check parity is the XOR of the values from command type to command parameter.

```
AT*PIC=\x01\x04\x00\x01\x00\x00\x00\x04\r\n
<-----><--><------><--------------><--><-->
   \     \      \     \               \  \_ command end delimiter (CRLF)
    \     \      \     \               \_ check parity
     \     \      \     \_ command data (The length changes depending on the value of "command data size")
      \     \      \_ command data size (max 0xffff)
       \     \_ command (max 0xff)
        \_ command start prefix
```

### Command Response (Application -> Client)

Hexadecimal data starting with `*PIC:` and ending with `CRLF`.

The response status is specified by the first 8 bits.

The response data size is represented by the second 16 bits. Then there is the content of the response datas.

The check parity is the XOR of the values from response status to response data.

#### OK

```
*PIC:\x01\x04\x00\x01\x00\x00\x00\x04\r\nOK\r\n
<---><--><------><--------------><--><-------->
  \    \      \       \             \      \_ response end delimiter
   \    \      \       \             \_ check parity
    \    \      \       \_ response data (The length changes depending on the value of "response data size")
     \    \      \_ response data size (max 0xffff)
      \    \_ response status (0x01)
       \_ response start prefix
```

#### ERROR

```
*PIC:\x07\x04\x00\x01\x00\x00\x00\x02\r\nERROR\r\n
<---><--><------><--------------><--><----------->
  \    \      \       \            \       \_ response end delimiter
   \    \      \       \            \_ check parity
    \    \      \       \_ response data (The length changes depending on the value of "response data size")
     \    \      \_ response data size (max 0xffff)
      \    \_ response status (values from 0x02 to 0xff)
       \_ response start prefix
```

#### Reserved value of response status

| status | description |
|---|---|
| 0x01 | No error |
| 0x02 | Invalid command format error |
| 0x03 | Invalid parity error |
| 0x04 | Command not found error |
| 0x05 | Invalid data length error |
| 0x06 | Command fail error |


## Command Handler Interface

The command handler function receives the command parameter byte in the first argument and the command parameter size in the second argument.

### When returning some kind of response

Returns a value of type `bool`,` int`, `float`,`str`, or `bytes`.

```python
@app.handler(0x01)
def handler(data: bytes, data_size: int) -> Union[bool, int, float, str, bytes]:
    ....
    return response_data
```

### When returning no response

Returns nothing.

```python
@app.handler(0x01)
def handler(data: bytes, data_size: int):
    ....
    # nothing return
```

### If you want to return your domain error status

Raise an exception with the `status_code` attribute.
If you want to return error message etc. as response data, add `description` attribute.

```python
class DomainException(Exception):
    status_code = 0xff
    description = 'any error message'

@app.handler(0x01)
def handler(data: bytes, data_size: int):
    ....
    raise DomainException
```

## API

### PiCmd

#### `PiCmd.create(serial_port: str) -> PiCmd`

Take the serial port path as an argument and create an instance.

#### `@handler(command: int)`

Decorator that takes a command type as an argument and registers it as a handler.

#### `run()`

Start accepting and responding to commands.

## Change Log

### 0.3.0

Change the data format of the protocol.

### 0.2.0

Change request and resopnse prefix.

### 0.1.0

Initial release.

## License

MIT
