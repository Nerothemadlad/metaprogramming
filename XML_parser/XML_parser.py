import os
import sys
from types import ModuleType
from xml.etree.ElementTree import parse


def _xml_to_code(filename):
    document = parse(filename)
    code = "from helpers import *\n"
    for st in document.findall("structure"):
        code += _xml_struct_code(st)
    return code


def _xml_struct_code(st):
    stname = st.get("name")
    code = f"class {stname}(Structure):\n"
    for field in st.findall("field"):
        stname = field.text.strip()
        datatype = field.get("type")
        kwargs = ", ".join(
            f"{key}={val}" for key, val in field.items() if key != "type"
        )
        code += f"    {stname} = {datatype}({kwargs})\n"
    return code


class XMLImporter:
    """A custom finder class that can be used to load xml files"""

    @staticmethod
    def find_module(fullname, path=None):
        """Find a module, given its full name and a path to search."""
        # fullname is the name of the to be imported module
        # path is the path setting (for packages)
        filepath = os.path.join(sys.path[0], fullname + ".xml")
        if os.path.exists(filepath):
            return XMLLoader(filepath)

        return None


class XMLLoader:
    """Custom loader class that can be used to load xml files"""

    def __init__(self, path) -> None:
        self._path = path

    def load_module(self, fullname):
        """Load a module, given its full name."""
        if fullname in sys.modules:
            return sys.modules[fullname]

        module = ModuleType(fullname)
        # Register the new module to the sys.modules cache
        sys.modules[fullname] = module
        module.__file__ = self._path
        module.__loader__ = self
        code = _xml_to_code(self._path)
        exec(code, module.__dict__, module.__dict__)
        return module


def install_import_hook():
    """Install a custom import hook to load xml files"""
    sys.meta_path.append(XMLImporter)


install_import_hook()

import datastruct

stock = datastruct.Stock("GOOG", "Google", price=2800, shares=100)
print(stock.ticker, stock.name, stock.price, stock.shares)
# stock.name = "Google Inc."
