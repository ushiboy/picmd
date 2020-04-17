pi-cmd
=====

(wip)

## Spec

```
@picmd.handler(command=0x01)
def handler1(data, data_size):
    return response_data

@picmd.handler(command=0x02)
def handler2(data, data_size):
    ....
    # nothing return

class DomainException(Exception):
    status_code = 0xff
    description = "any message"

@picmd.handler(command=0x03)
def handler3(data, data_size):
    raise DomainException
```
