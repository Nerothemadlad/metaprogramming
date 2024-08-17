from inspect import Parameter, Signature


def make_signature(names):
    """Make signatures for class attributes"""
    return Signature(Parameter(name, Parameter.POSITIONAL_OR_KEYWORD) for name in names)


class StructMeta(type):
    """Metaclass for Structure"""

    def __new__(cls, clsname, bases, clsdict):
        clsobj = super().__new__(cls, clsname, bases, clsdict)
        sig = make_signature(clsobj._fields)
        setattr(clsobj, "__signature__", sig)
        return clsobj


class Structure(metaclass=StructMeta):
    """Structure base class with metaclass for all classes"""

    _fields = []

    def __init__(self, *args, **kwargs):
        bound_args = self.__signature__.bind(*args, **kwargs)
        for name, val in bound_args.arguments.items():
            setattr(self, name, val)

    def __repr__(self):
        args = ", ".join(repr(getattr(self, name)) for name in self._fields)
        return f"{type(self).__name__}({args})"


class Crypto(Structure):
    """Class to represent a crypto currency"""

    _fields = ["ticker", "price", "amount"]


class Person(Structure):
    """Class to represent a person"""

    _fields = ["name", "age", "height"]
