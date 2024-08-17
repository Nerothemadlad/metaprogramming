class LoggedAttr:
    __set_name = True

    def __init__(self, name=None):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__[self.name]


class Managed:
    descriptor = LoggedAttr("descriptor")


assert Managed.descriptor.name == "descriptor"


class configure_descriptors:
    def __init__(self, **kwargs):
        self.descs = {dname: dcls(dname) for dname, dcls in kwargs.items()}

    def __call__(self, class_):
        for dname, descriptor in self.descs.items():
            setattr(class_, dname, descriptor)
        return class_


@configure_descriptors(descriptor=LoggedAttr)
class DecoratedManaged:
    """The descriptor is provided by the decorator"""


assert DecoratedManaged.descriptor.name == "descriptor"


class MetaDescriptor(type):
    def __new__(cls, clsname, bases, clsdict):
        for attrname, cls_attr in clsdict.items():
            mangled_attr = f"_{cls_attr.__class__.__name__}__set_name"
            if hasattr(cls_attr, mangled_attr):
                setattr(cls_attr, "name", attrname)
        return super().__new__(cls, clsname, bases, clsdict)


class MetaManaged(metaclass=MetaDescriptor):
    descriptor = LoggedAttr()


assert MetaManaged.descriptor.name == "descriptor"


class LoggedAttr2:
    def __set_name__(self, owner, name):
        self.owner = owner
        self.name = name


class Managed2:
    descriptor = LoggedAttr2()


assert Managed2.descriptor.name == "descriptor"
