from functools import partial
from pathlib import Path

filename = Path(__file__).stem
print = partial(print, f"[{filename}]:")


def process_signature(app, what, name, obj, options, signature, return_annotation):
    """
    Event handler for autodoc-process-signature.
    Modify the signature of the documented objects here.

    Parameters:
    - app: Sphinx application object
    - what: Type of the object ('module', 'class', 'exception', 'function', 'method', 'attribute')
    - name: Fully qualified name of the object
    - obj: The documented object
    - options: Options given to the directive
    - signature: The signature string (if any)
    - return_annotation: The return type annotation (if any)
    """

    if what == "class" and name:
        classname = (name.split(".")[-1] if "." in name else name).strip()
        args = signature.split(",")
        types = [sig.split(":")[1] for sig in args if ":" in sig]
        lasts = [t.split(".")[-1] if "." in t else t for t in types]
        lasts = [l.strip() for l in lasts]
        if classname.startswith("_") or any(l.startswith("_") for l in lasts):
            print(f"Delete signature of {classname}")
            signature = ""
    if what != "data" and name.split(".")[-1].startswith("_"):
        print("DEBUG DATA", what, name)

    return signature, return_annotation


def setup(app):
    app.connect("autodoc-process-signature", process_signature)
