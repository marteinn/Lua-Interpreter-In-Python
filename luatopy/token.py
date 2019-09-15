from enum import Enum, auto

from dataclasses import dataclass


class TokenType(Enum):
    ILLEGAL = auto()
    EOF = auto()
    NEWLINE = auto()

    IDENTIFIER = auto()
    INT = auto()
    STR = auto()
    NIL = auto()
    TRUE = auto()
    FALSE = auto()

    COMMENT = auto()

    ASSIGN = auto()
    PLUS = auto()
    MINUS = auto()
    ASTERISK = auto()
    SLASH = auto()
    SEMICOLON = auto()

    EQ = auto()
    NOT_EQ = auto()

    GT = auto()
    GTE = auto()
    LT = auto()
    LTE = auto()

    AND = auto()
    OR = auto()
    NOT = auto()

    LPAREN = auto()
    RPAREN = auto()

    COMMA = auto()
    ADD = auto()

    # Keywords
    FUNCTION = auto()
    IF = auto()
    ELSE = auto()
    THEN = auto()
    END = auto()
    RETURN = auto()


@dataclass
class Token:
    token_type: TokenType
    literal: str
