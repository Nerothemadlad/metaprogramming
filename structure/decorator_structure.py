from inspect import Parameter, Signature


def make_signature(names):
    """Make signatures for class attributes"""
    return Signature(Parameter(name, Parameter.POSITIONAL_OR_KEYWORD) for name in names)


def add_signature(*names):
    """Add signatures to a class"""

    def decorate(cls):
        cls.__signature__ = make_signature(names)
        return cls

    return decorate


class Structure:
    """Structure base class for all classes"""

    __signature__ = make_signature([])

    def __init__(self, *args, **kwargs):
        bound_args = self.__signature__.bind(*args, **kwargs)
        for name, val in bound_args.arguments.items():
            setattr(self, name, val)


@add_signature("ticker", "shares", "price")
class Stock(Structure):
    """Class to represent a stock"""


@add_signature("x", "y")
class Point(Structure):
    """Class to represent a point"""


a = Stock("F", price=18, shares=100)
print(a.ticker, a.shares, a.price)
