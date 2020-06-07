import pytest
from picmd._register import HandlerRegister

def test_handler():
    r = HandlerRegister()

    @r.handler(0x01)
    def h1(data, size):
        pass

    with pytest.raises(ValueError):
        @r.handler(256)
        def h2(data, size):
            pass

    assert len(r.handlers) == 1
    assert r.handlers[0] == (0x01, h1)
