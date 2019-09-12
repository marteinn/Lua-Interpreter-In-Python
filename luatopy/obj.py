from dataclasses import dataclass

from enum import Enum, auto


class ObjType(Enum):
    INTEGER = auto()
    FLOAT = auto()
    BOOLEAN = auto()
    NULL = auto()
    RETURN = auto()
    ERROR = auto()


class Obj:
    def type(self) -> ObjType:
        pass

    def inspect(self) -> str:
        pass


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
