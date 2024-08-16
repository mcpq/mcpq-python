import builtins
from functools import partial
from pathlib import Path

filename = Path(__file__).stem
print = partial(print, f"[{filename}]:")
std_dir = builtins.dir


def source_order_dir(obj):
    if isinstance(obj, type):
        mro = obj.mro()
        mro = [mro[0]] + list(reversed(mro[1:]))
        return [name for cls in mro for name in cls.__dict__.keys()]
    return std_dir(obj)


def setup(app):
    print("Patching 'dir' function globally")
    builtins.dir = source_order_dir
