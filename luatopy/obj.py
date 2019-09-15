from dataclasses import dataclass, field
from typing import Any, Dict, Tuple, List, Optional
from enum import Enum, auto

from luatopy import ast


class ObjType(Enum):
    INTEGER = auto()
    FLOAT = auto()
    BOOLEAN = auto()
    NULL = auto()
    RETURN = auto()
    ERROR = auto()
    FUNCTION = auto()


class Obj:
    def type(self) -> ObjType:
        pass

    def inspect(self) -> str:
        pass


class Environment:
    def __init__(self, outer: Optional["Environment"] = None):
        self.store: Dict[str, Obj] = {}
        self.outer: Optional["Environment"] = outer

    def get(self, name: str, default: Obj) -> Tuple[Obj, bool]:
        val = self.store.get(name, default)
        found = self.contains(name)

        if not found and self.outer:
            return self.outer.get(name, default)

        return (val, found)

    def contains(self, name: str) -> bool:
        return name in self.store

    def set(self, name: str, value: Obj) -> Obj:
        self.store[name] = value
        return value

    def __str__(self):
        combined = self.store
        if self.outer:
            combined = {**self.outer.store, **self.store}
        return str(combined)

    @staticmethod
    def create_enclosed(outer: "Environment") -> "Environment":
        return Environment(outer=outer)


@dataclass
class Integer(Obj):
    value: int = 0

    def type(self) -> ObjType:
        return ObjType.INTEGER

    def inspect(self) -> str:
        return str(self.value)


@dataclass
class Float(Obj):
    value: float = 0.0

    def type(self) -> ObjType:
        return ObjType.FLOAT

    def inspect(self) -> str:
        return str(self.value)


@dataclass
class Boolean(Obj):
    value: bool = False

    def type(self) -> ObjType:
        return ObjType.BOOLEAN

    def inspect(self) -> str:
        return "true" if self.value else "false"


class Null(Obj):
    def type(self) -> ObjType:
        return ObjType.NULL

    def inspect(self) -> str:
        return "nil"


@dataclass
class ReturnValue(Obj):
    value: Obj

    def type(self) -> ObjType:
        return ObjType.RETURN

    def inspect(self) -> str:
        return self.value.inspect()


@dataclass
class Error(Obj):
    message: str

    @staticmethod
    def create(str_format, *args):
        return Error(message=str_format.format(*args))

    def type(self) -> ObjType:
        return ObjType.ERROR

    def inspect(self) -> str:
        return "ERROR: {}".format(self.message)


@dataclass
class Function(Obj):
    body: ast.BlockStatement
    env: Environment
    parameters: List[ast.Identifier] = field(default_factory=list)

    def type(self) -> ObjType:
        return ObjType.FUNCTION

    def inspect(self) -> str:
        out: str = ""
        signature = ", ".join([x.value for x in self.parameters])

        out = "function ({0})\n".format(signature)
        out = out + self.body.to_code()
        out = out + "\nend"
        return out
