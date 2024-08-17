# import logging
# import os
from functools import partial, wraps


def debug(func=None, *, prefix="", suffix=""):
    """
    Print the function signature and return the original function

    func: the function to be decorated
    """
    if func is None:
        return partial(debug, prefix=prefix, suffix=suffix)

    # if "DEBUG" not in os.environ:
    #     return func
    # log = logging.getLogger(func.__module__)
    msg = prefix + func.__qualname__

    @wraps(func)
    def wrapper(*args, **kwargs):
        # log.debug("%s(%s, %s)", msg, args, kwargs)
        # args_str = ", ".join(map(repr, args))
        # kwargs_str = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
        # args_kwargs_str = ", ".join(filter(None, (args_str, kwargs_str)))
        # print(f"{msg}({args_kwargs_str}) {suffix}")
        print(msg + suffix)
        return func(*args, **kwargs)

    return wrapper


def debugmethods(cls):
    """Add debugging to all methods of a class"""
    for name, val in vars(cls).items():
        if callable(val):
            setattr(cls, name, debug(val))
    return cls


def debugattr(cls):
    """Add debugging to all attributes of a class"""
    orig_getattribute = cls.__getattribute__

    def __getattribute__(self, name):
        print(f"Getting {name}")
        return orig_getattribute(self, name)

    cls.__getattribute__ = __getattribute__
    return cls


class DebugMeta(type):
    """Add debugging to all methods of child classes"""

    def __new__(cls, clsname, bases, clsdict):
        clsobj = super().__new__(cls, clsname, bases, clsdict)
        clsobj = debugmethods(clsobj)
        return clsobj


@debug(prefix="*** [DEBUG] ", suffix=" ***")
def add(x, y):
    """Add function"""
    return x + y


class Spam(metaclass=DebugMeta):
    """Spam class"""

    def bar(self):
        """bar method"""

    def foo(self):
        """foo method"""


@debugattr
class Person:
    """Person class"""

    def __init__(self, name, age):
        self.name = name
        self.age = age


add(y=1, x=2)

a = Spam()
a.bar()

b = Person("Bob", 42)
print(b.name, b.age)
