from numbers import Number

from metaclass_structure import Structure


class Descriptor:
    """Implement the descriptor protocol for class attributes"""

    def __init__(self, name=None, **kwargs):
        self.name = name
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value

    def __delete__(self, instance):
        del instance.__dict__[self.name]


class Typed(Descriptor):
    """Type checking descriptor"""

    expected_type = type(None)

    def __set__(self, instance, value):
        if not isinstance(value, self.expected_type):
            raise TypeError(f"Expected {str(self.expected_type)}")
        # super() calls __set__() from the next one in the MRO having it,
        # not from the parent class
        super().__set__(instance, value)


class NumberChecked(Typed):
    """A number checking descriptor"""

    expected_type = Number


class Integer(Typed):
    """An integer checking descriptor"""

    expected_type = int


class Float(Typed):
    """A float checking descriptor"""

    expected_type = float


class String(Typed):
    """A string checking descriptor"""

    expected_type = str


class Positive(Descriptor):
    """A positive number checking descriptor"""

    def __set__(self, instance, value):
        if value <= 0:
            raise ValueError("Expected a positive number")
        super().__set__(instance, value)


class PositiveNumber(NumberChecked, Positive):
    """A positive number checking descriptor"""


class PositiveInteger(Integer, Positive):
    """A positive integer checking descriptor"""


class PositiveFloat(Float, Positive):
    """A positive float checking descriptor"""


class Good(Structure):
    """A structure with typed attributes"""

    _fields = ["name", "price", "quantity"]

    name = String("name")
    price = PositiveNumber("price")
    quantity = PositiveInteger("quantity")


def main():
    """Main function"""

    food = Good("Banana", quantity=4, price=10)
    print(food.name, food.price, food.quantity)


if __name__ == "__main__":
    main()
