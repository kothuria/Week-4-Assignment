from typing import Iterable, List, Any

def batch(iterable: Iterable[Any], size: int) -> Iterable[list]:
    buf: List[Any] = []
    for item in iterable:
        buf.append(item)
        if len(buf) >= size:
            yield buf
            buf = []
    if buf:
        yield buf
