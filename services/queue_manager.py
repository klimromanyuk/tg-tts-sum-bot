"""Async queue for sequential GPU tasks."""

import asyncio

_queue: asyncio.Queue = None
_running = False

def init(maxsize=10):
    global _queue
    _queue = asyncio.Queue(maxsize=maxsize)

def get_queue() -> asyncio.Queue:
    return _queue

async def put(coro, callback=None) -> bool:
    """Returns False if queue is full."""
    if _queue.full():
        return False
    await _queue.put((coro, callback))
    return True

def qsize() -> int:
    return _queue.qsize() if _queue else 0

async def worker():
    global _running
    _running = True
    while _running:
        try:
            coro, callback = await asyncio.wait_for(_queue.get(), timeout=1.0)
        except asyncio.TimeoutError:
            continue
        try:
            result = await coro
            if callback:
                await callback(result)
        except Exception as e:
            if callback:
                await callback(e)
        finally:
            _queue.task_done()

def stop():
    global _running
    _running = False