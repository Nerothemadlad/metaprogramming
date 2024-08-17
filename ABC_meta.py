def abstractmethod(f):
    """Mark a method as abstract"""
    f.__is_abstractmethod__ = True
    return f


def has_abstractmethods(cls):
    """Check if a class has abstract methods"""
    not_overridden = []
    clsdict = cls.__dict__
    for base in cls.__mro__[1:]:
        for name, method in base.__dict__.items():
            if (
                name not in clsdict
                and callable(method)
                and hasattr(method, "__is_abstractmethod__")
            ):
                if method.__is_abstractmethod__:
                    not_overridden.append(name)
    return not_overridden


class ABCMeta(type):
    """ABCMeta is a metaclass that allows for the creation of abstract base classes (ABCs)"""

    def __call__(cls, *args, **kwds):
        print("call:", cls, args, kwds)
        abstract = has_abstractmethods(cls)
        if abstract:
            raise TypeError(
                ", ".join(abstract) + f" must be implemented in subclass {cls.__name__}"
            )
        return super().__call__(*args, **kwds)


class ABC(metaclass=ABCMeta):
    """ABC is an abstract base class that allows for the creation of abstract base classes (ABCs)"""

    @abstractmethod
    def f(self):
        pass

    @abstractmethod
    def g(self):
        pass


class Uninstantiable_Class(ABC):
    """Uninstantiable class with unimplemented abstract method"""

    def f(self):
        pass


class Instantiable_Class(ABC):
    """Instantiatable class"""

    def __init__(self, name) -> None:
        self.name = name

    def f(self):
        pass

    def g(self):
        pass


# a = Uninstantiable_Class()
b = Instantiable_Class("Bob")
