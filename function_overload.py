def overload(f):
    """Mark a function as overloaded."""
    f.__overloads__ = True
    return f


def is_subdict(subdict, dictionary):
    """Check if a dictionary is a subset of another"""
    return dictionary | subdict == dictionary


def dict_slicing(dictionary, start=None, end=None):
    """Return a slice of a dictionary"""
    return {
        key: value
        for key, value in dictionary.items()
        if key in tuple(dictionary.keys())[start:end]
    }


class OverloadList(list):
    """A list storing overloaded functions of a class"""


class OverloadFunctions:
    """A class representing overloaded functions of a class"""

    def __set_name__(self, owner, name):
        self.name = name
        self.owner = owner
        self.fullname = self.owner.__name__ + "." + self.name

    def __init__(self, overload_list):
        self.overload_list = overload_list

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return BoundOverloadedMethod(
            self.overload_list, instance, owner, self.name, self.fullname
        )

    def __repr__(self):
        hex_id = str(hex(id(self)))[2:]
        full_id = "0x" + f"{hex_id.upper():0>16}"
        return f"<{self.__class__.__name__} {self.fullname} at {full_id}>"

    def __call__(self, *args, **kwargs):
        args = args[1:] if args[0] == self.owner else args
        args_len = len(args)
        args_types = [type(arg) for arg in args]
        kwargs_types = {key: type(value) for key, value in kwargs.items()}

        for func in self.overload_list:
            func_args = func.__annotations__
            func_arg_types = list(func_args.values())[:args_len]
            func_kwargs_types = dict_slicing(func_args, args_len)

            if args_types == func_arg_types and is_subdict(
                kwargs_types, func_kwargs_types
            ):
                try:
                    return func(self.owner, *args, **kwargs)
                except TypeError:
                    pass
        raise TypeError(
            f"No overload for {self.fullname}({self.owner.__name__}, {', '.join(map(repr, args))})"
        )


class BoundOverloadedMethod(OverloadFunctions):
    """A class representing bound overloaded methods of an instance"""

    def __init__(self, overload_list, instance, owner, name, fullname):
        self.overload_list = overload_list
        self.instance = instance
        self.owner = owner
        self.name = name
        self.fullname = fullname

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.fullname} of {self.instance}>"


class OverloadDict(dict):
    """A custom dict to handle overloaded functions"""

    def __setitem__(self, key, value):
        prior_val_type = type(self.get(key))
        overloaded = getattr(value, "__overloads__", False)
        if overloaded:
            if prior_val_type is not OverloadList:
                super().__setitem__(key, OverloadList())
            self[key].append(value)
            return

        if prior_val_type is OverloadList:
            args = ", ".join(
                f"{arg}: {arg_type.__name__}"
                for arg, arg_type in value.__annotations__.items()
            )
            func_repr = f"{value.__qualname__}({args})"
            owner = value.__qualname__.split(".")[0]
            raise TypeError(
                f"{func_repr} is overloaded and cannot be overwritten.\nPlease overload all functions named {key} in class {owner} succeeding {func_repr}."
            )
        super().__setitem__(key, value)


class OverloadMeta(type):
    """Metaclass for classes with functions overloading"""

    @classmethod
    def __prepare__(cls, name, bases, **kwds):
        return OverloadDict()

    def __new__(cls, name, bases, clsdict, **kwds):
        overload_clsdict = {
            key: OverloadFunctions(value) if isinstance(value, OverloadList) else value
            for key, value in clsdict.items()
        }
        return super().__new__(cls, name, bases, overload_clsdict, **kwds)


class OverloadBase(metaclass=OverloadMeta):
    """Base class for classes with functions overloading to inherit from"""


class Overload(OverloadBase):
    def f(self, x: int):
        print("OverloadFunctions function f with x: int")

    @overload
    def f(self, x: str, y: int):
        print("OverloadFunctions function f with x: str, y: int")

    @overload
    def f(self, x: str, y: str):
        print("OverloadFunctions function f with x: str, y: str")


test = Overload()
# print(Overload.f)
# print(test.f)
Overload.f(Overload, "a", 2)
test.f("a", "b")
