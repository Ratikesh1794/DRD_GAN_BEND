import asyncio
from functools import wraps

# Global event loop
loop = None

def get_or_create_eventloop():
    global loop
    if loop is None:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    return loop

def run_async(coro):
    loop = get_or_create_eventloop()
    return loop.run_until_complete(coro)

def async_handler(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        loop = get_or_create_eventloop()
        return loop.run_until_complete(f(*args, **kwargs))
    return wrapped 