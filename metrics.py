import time
import logging

logger = logging.getLogger("metrics")

def timer(name: str):
    def deco(fn):
        def wrapper(*args, **kwargs):
            t0 = time.perf_counter()
            try:
                return fn(*args, **kwargs)
            finally:
                dt = time.perf_counter() - t0
                logger.info("timer.%s=%.4fs", name, dt)
        return wrapper
    return deco
