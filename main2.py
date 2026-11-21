
from functools import wraps


def repeat(times: int):
    if times < 1:
        raise ValueError("Количество вызовов должно быть не меньше 1")
    n = times
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal n
            result = None
            for _ in range(times):
                if n<1:
                    raise RuntimeError("Функция была вызвана слишком много раз")
                n -= 1
                result = func(*args, **kwargs)
            return result

        return wrapper

    return decorator


@repeat(3)
def ping():
    return "pong"

print(ping())
print(ping())
print(ping())  # This will raise a RuntimeError since the function has been called too many times