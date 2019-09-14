from dataclasses import dataclass, field
from typing import Any, Dict, Tuple, List
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
    def __init__(self):
        self.store: Dict[str, Obj] = {}

    def get(self, name: str, default: Obj) -> Tuple[Obj, bool]:
        val = self.store.get(name, default)
        return (val, self.contains(name))

    def contains(self, name: str) -> bool:
        return name in self.store

    def set(self, name: str, value: Obj) -> Obj:
        self.store[name] = value
        return value


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

        out = "function ({0}) ".format(signature)
        out = out + self.body.to_code()
        out = out + " end"
        return out
