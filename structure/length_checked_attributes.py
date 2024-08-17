import re
from time import time

from metaclass_structure import make_signature
from typed_checked_attributes import Descriptor, PositiveNumber, String


class Sized(Descriptor):
    """A descriptor for enforcing a fixed size for a field"""

    def __init__(self, *args, maxlen, **kwargs):
        self.maxlen = maxlen
        super().__init__(*args, **kwargs)

    def __set__(self, instance, value):
        if len(value) > self.maxlen:
            raise ValueError(
                f"{value} exceeds {self.name}'s max length of {self.maxlen}"
            )
        super().__set__(instance, value)


class Regex(Descriptor):
    """A descriptor enforcing a regular expression match"""

    def __init__(self, *args, pattern, **kwargs):
        self.pattern = re.compile(pattern)
        super().__init__(*args, **kwargs)

    def __set__(self, instance, value):
        if not self.pattern.match(value):
            raise ValueError(f"{value} does not match {self.name}'s pattern")
        super().__set__(instance, value)


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
        # Changing the name attribute of the descriptor objects to the variable name
        for field in fields:
            clsdict[field].name = field

        clsobj = super().__new__(cls, name, bases, clsdict)
        sig = make_signature(fields)
        setattr(clsobj, "__signature__", sig)
        return clsobj


class Structure(metaclass=StructMeta):
    """Base class for all structures"""

    def __init__(self, *args, **kwargs):
        bound = self.__signature__.bind(*args, **kwargs)
        for name, val in bound.arguments.items():
            setattr(self, name, val)


class Stock(Structure):
    """A stock holding structure with ticker symbol, name,
    shares owned, and price paid.
    """

    # [A-Z]+$ means all characters must be capitalized ([A-Z]+) till the end ($)
    ticker = SizedRegexString(pattern="[A-Z]+$", maxlen=10)
    name = SizedString(maxlen=10)
    price = PositiveNumber()
    shares = PositiveNumber()


class Stock2:
    """Simple stock structure with ticker symbol, name, shares owned and price for each share"""

    def __init__(self, ticker: str, name: str, shares, price) -> None:
        self.ticker = ticker
        self.name = name
        self.price = price
        self.shares = shares


stock = Stock("MSFT", "Microsoft", 300, 10)
print(stock.ticker, stock.name, stock.price, stock.shares)
start = time()
for _ in range(1_000_000):
    stock = Stock("MSFT", "Microsoft", 300, 10)
    # stock.price = 180
    # stock.shares = 100

print("Time taken:", time() - start)
