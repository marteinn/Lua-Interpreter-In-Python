from typing import Any, Dict, Optional, List

from luatopy import obj
from luatopy.obj import TRUE, FALSE, NULL


builtins: Dict[str, Any] = {}


def register(store, name, fn):
    store[name] = obj.Builtin(fn=fn)
    return store


def builtin_type(*args: obj.Obj) -> obj.Obj:
    if len(args) == 0:
        return obj.Error.create("Missing arguments")

    value = args[0]
    value_type: Optional[str] = None
    if type(value) == obj.String:
        value_type = "string"
    if type(value) == obj.Integer:
        value_type = "number"
    if type(value) == obj.Boolean:
        value_type = "boolean"

    if not value_type:
        return NULL
    return obj.String(value=value_type)


builtins = register(builtins, "type", builtin_type)


def builtin_print(*args: obj.Obj) -> obj.Obj:
    out: List[str] = [x.inspect() for x in args]
    # TODO: Add a way to detect stdout and how to write
    return obj.String(value="   ".join(out))


builtins = register(builtins, "print", builtin_print)
