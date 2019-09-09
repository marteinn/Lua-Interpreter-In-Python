from dataclasses import dataclass

from enum import Enum, auto


class ObjType(Enum):
    INTEGER = auto()
    BOOLEAN = auto()


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
