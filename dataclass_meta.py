def _make_init(annotations):
    """Make an __init__ method given a list of attribute annotations"""
    init_args = ", ".join(
        f"{arg}: {annotation.__qualname__}" for arg, annotation in annotations.items()
    )
    source_code = f"def __init__(self, {init_args}):\n"
    for arg in annotations.keys():
        source_code += f"    self.{arg} = {arg}\n"
    return source_code


class DataclassMeta(type):
    """Metaclass for dataclasses"""

    def __new__(cls, name, bases, clsdict, **kwargs):
        annotations = clsdict.get("__annotations__")
        if annotations:
            init_code = _make_init(annotations)
            exec(init_code, globals(), clsdict)
        return super().__new__(cls, name, bases, clsdict)


class Dataclass(metaclass=DataclassMeta):
    """Base class for dataclasses"""


class Point(Dataclass):
    x: int
    y: int


point = Point(x=1, y=2)
# print(point.x, point.y)
