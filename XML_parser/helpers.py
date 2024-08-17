import re
from numbers import Number


def _make_init(fields):
    """Make an __init__ method given a list of field names"""

    source_code = f'def __init__(self, {", ".join(fields)}):\n'
    for field in fields:
        source_code += f"    self.{field} = {field}\n"
    return source_code


def _make_setter(descriptor_class):
    """Make a __set__ method for a descriptor class"""

    source_code = "def __set__(self, instance, value):\n"
    for descriptor in descriptor_class.__mro__:
        if "set_code" in descriptor.__dict__:
            for line in descriptor.set_code():
                source_code += f"    {line}\n"
    return source_code


class DescriptorMeta(type):
    """Metaclass for descriptors"""

    # Code generation muss be done in the __init__ method instead of the __new__ method
    # because the class have to be created first to provide the required __mro__ for _make_setter()
    def __init__(cls, clsname, bases, clsdict):
        if "__set__" not in clsdict:
            # Make the set code
            exec(_make_setter(cls), globals(), clsdict)
            setattr(cls, "__set__", clsdict["__set__"])
        else:
            raise TypeError("Define set_code() instead of __set__()")


class Descriptor(metaclass=DescriptorMeta):
    """Implement the descriptor protocol for class attributes"""

    def __init__(self, name=None, **kwargs):
        self.name = name
        for key, value in kwargs.items():
            setattr(self, key, value)

    @staticmethod
    def set_code():
        """Return the source code for __set__()"""
        return ["instance.__dict__[self.name] = value"]

    def __delete__(self, instance):
        raise AttributeError("Can't delete attribute")


class Typed(Descriptor):
    """Type checking descriptor"""

    expected_type = type(None)

    @staticmethod
    def set_code():
        """Return the source code for __set__()"""
        return [
            "if not isinstance(value, self.expected_type):",
            '    raise TypeError(f"Expected value of type {str(self.expected_type.__name__)}")',
        ]


class NumberChecked(Typed):
    """A number checking descriptor"""

    expected_type = Number


class Integer(Typed):
    """An integer checking descriptor"""

    expected_type = int


class String(Typed):
    """A string checking descriptor"""

    expected_type = str


class Positive(Descriptor):
    """A positive number checking descriptor"""

    @staticmethod
    def set_code():
        """Return the source code for __set__()"""
        return ["if value <= 0:", "    raise ValueError('Expected a positive number')"]


class Sized(Descriptor):
    """A descriptor for enforcing a fixed size for a field"""

    def __init__(self, *args, maxlen=float("inf"), **kwargs):
        self.maxlen = maxlen
        super().__init__(*args, **kwargs)

    @staticmethod
    def set_code():
        """Return the source code for __set__()"""
        return [
            "if len(value) > self.maxlen:",
            "    raise ValueError(f'{value} exceeds max length {self.maxlen} for attribute {self.name}')",
        ]


class Regex(Descriptor):
    """A descriptor enforcing a regular expression match"""

    def __init__(self, *args, pattern="", **kwargs):
        self.pattern = re.compile(pattern)
        super().__init__(*args, **kwargs)

    @staticmethod
    def set_code():
        """Return the source code for __set__()"""
        return [
            "if not self.pattern.match(value):",
            "    raise ValueError(f'{value} does not match the pattern for attribute {self.name}')",
        ]


class PositiveNumber(NumberChecked, Positive):
    """A positive number checking descriptor"""


class SizedString(String, Sized):
    """A string of a fixed size"""


class SizedRegexString(SizedString, Regex):
    """A string of a fixed size matching a regular expression"""


class NoDuplicatesDict(dict):
    """A dictionary that prevents duplicate keys"""

    def __setitem__(self, key, value):
        if key in self:
            raise ValueError(f"{key} already defined")
        super().__setitem__(key, value)


class StructMeta(type):
    """Metaclass for all structure"""

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        return NoDuplicatesDict()

    def __new__(cls, name, bases, clsdict):
        fields = [
            key for key, value in clsdict.items() if isinstance(value, Descriptor)
        ]
        for field in fields:
            clsdict[field].name = field

        if fields:
            exec(_make_init(fields), globals(), clsdict)
        clsobj = super().__new__(cls, name, bases, clsdict)
        return clsobj


class Structure(metaclass=StructMeta):
    """Base class for all structures to inherit from"""
