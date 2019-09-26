import re
from io import StringIO
from typing import Optional, Iterator

from .token import TokenType, Token


EOF_MARKER: str = "<<EOF>>"


class Lexer:
    def __init__(self, source: StringIO) -> None:
        self.source: str = source.getvalue()
        self.pos: int = 0
        self.read_pos: int = 0
        self.ch: str = ""

        self.read_char()

    def read_char(self) -> None:
        if self.read_pos >= len(self.source):
            self.ch = EOF_MARKER
        else:
            self.ch = self.source[self.read_pos]

        self.pos = self.read_pos
        self.read_pos = self.read_pos + 1

    def peek_ahead(self, steps: int = 0) -> str:
        if self.read_pos + steps >= len(self.source):
            return EOF_MARKER
        return self.source[self.read_pos + steps]

    def peek_behind(self, steps: int = 0) -> str:
        if self.read_pos - steps >= len(self.source):
            return EOF_MARKER
        return self.source[self.read_pos - steps]

    def skip_whitespace(self) -> None:
        while self.ch == " ":
            self.read_char()

    def tokens(self) -> Iterator[Token]:
        while True:
            token = self.next_token()
            yield token

            if token.token_type == TokenType.EOF:
                break

    def next_token(self) -> Token:
        self.skip_whitespace()

        if self.ch == EOF_MARKER:
            tok = Token(token_type=TokenType.EOF, literal=self.ch)
            self.read_char()
            return tok

        if self.ch == "\n":
            tok = Token(token_type=TokenType.NEWLINE, literal=self.ch)
            self.read_char()
            return tok

        if self.ch == ";":
            tok = Token(token_type=TokenType.SEMICOLON, literal=self.ch)
            self.read_char()
            return tok

        if self.ch == "%":
            tok = Token(token_type=TokenType.PERCENT, literal=self.ch)
            self.read_char()
            return tok

        if self.ch == "#":
            tok = Token(token_type=TokenType.HASH, literal=self.ch)
            self.read_char()
            return tok

        if self.ch == "(":
            tok = Token(token_type=TokenType.LPAREN, literal=self.ch)
            self.read_char()
            return tok

        if self.ch == ")":
            tok = Token(token_type=TokenType.RPAREN, literal=self.ch)
            self.read_char()
            return tok

        if self.ch == "{":
            tok = Token(token_type=TokenType.LBRACE, literal=self.ch)
            self.read_char()
            return tok

        if self.ch == "}":
            tok = Token(token_type=TokenType.RBRACE, literal=self.ch)
            self.read_char()
            return tok

        if self.ch == "[":
            tok = Token(token_type=TokenType.LBRACKET, literal=self.ch)
            self.read_char()
            return tok

        if self.ch == "]":
            tok = Token(token_type=TokenType.RBRACKET, literal=self.ch)
            self.read_char()
            return tok

        if self.ch == ",":
            tok = Token(token_type=TokenType.COMMA, literal=self.ch)
            self.read_char()
            return tok

        if self.ch == "+":
            tok = Token(token_type=TokenType.PLUS, literal=self.ch)
            self.read_char()
            return tok

        if self.ch == "*":
            tok = Token(token_type=TokenType.ASTERISK, literal=self.ch)
            self.read_char()
            return tok

        if self.ch == "/":
            tok = Token(token_type=TokenType.SLASH, literal=self.ch)
            self.read_char()
            return tok

        if self.ch == "=":
            if self.peek_ahead() == "=":
                literal = self.ch
                self.read_char()
                literal = literal + self.ch
                self.read_char()
                tok = Token(token_type=TokenType.EQ, literal=literal)
                return tok

            tok = Token(token_type=TokenType.ASSIGN, literal=self.ch)
            self.read_char()
            return tok

        if self.ch == ".":
            if self.peek_ahead(0) == ".":
                literal = self.ch
                self.read_char()
                literal = literal + self.ch
                self.read_char()
                tok = Token(token_type=TokenType.CONCAT, literal=literal)
                return tok

        if self.ch == "~":
            if self.peek_ahead(0) == "=":
                literal = self.ch
                self.read_char()
                literal = literal + self.ch
                self.read_char()
                tok = Token(token_type=TokenType.NOT_EQ, literal=literal)
                return tok

        if self.ch == ">":
            if self.peek_ahead(0) == "=":
                literal = self.ch
                self.read_char()
                literal = literal + self.ch
                self.read_char()
                tok = Token(token_type=TokenType.GTE, literal=literal)
                return tok

            literal = self.ch
            self.read_char()
            tok = Token(token_type=TokenType.GT, literal=literal)
            return tok

        if self.ch == "<":
            if self.peek_ahead(0) == "=":
                literal = self.ch
                self.read_char()
                literal = literal + self.ch
                self.read_char()
                tok = Token(token_type=TokenType.LTE, literal=literal)
                return tok

            literal = self.ch
            self.read_char()
            tok = Token(token_type=TokenType.LT, literal=literal)
            return tok

        if self.ch == "-":
            if (
                self.peek_ahead(0) == "-"
                and self.peek_ahead(1) == "["
                and self.peek_ahead(2) == "["
            ):
                comment = self.read_multiline_comment()
                tok = Token(token_type=TokenType.COMMENT, literal=comment)
                return tok

            if self.peek_ahead(0) == "-":
                comment = self.read_comment()
                tok = Token(token_type=TokenType.COMMENT, literal=comment)
                return tok

            tok = Token(token_type=TokenType.MINUS, literal=self.ch)
            self.read_char()
            return tok

        if is_letter(self.ch):
            identifier = self.read_identifier()

            if identifier == "nil":
                return Token(token_type=TokenType.NIL, literal=identifier)

            if identifier == "and":
                return Token(token_type=TokenType.AND, literal=identifier)

            if identifier == "or":
                return Token(token_type=TokenType.OR, literal=identifier)

            if identifier == "not":
                return Token(token_type=TokenType.NOT, literal=identifier)

            if identifier == "true":
                return Token(token_type=TokenType.TRUE, literal=identifier)

            if identifier == "false":
                return Token(token_type=TokenType.FALSE, literal=identifier)

            # TODO: Add is_keyword
            if identifier == "if":
                return Token(token_type=TokenType.IF, literal=identifier)

            if identifier == "then":
                return Token(token_type=TokenType.THEN, literal=identifier)

            if identifier == "else":
                return Token(token_type=TokenType.ELSE, literal=identifier)

            if identifier == "end":
                return Token(token_type=TokenType.END, literal=identifier)

            if identifier == "function":
                return Token(token_type=TokenType.FUNCTION, literal=identifier)

            if identifier == "return":
                return Token(token_type=TokenType.RETURN, literal=identifier)

            return Token(token_type=TokenType.IDENTIFIER, literal=identifier)

        if is_digit(self.ch):
            value = self.read_number()
            return Token(token_type=TokenType.INT, literal=value)

        if self.ch == '"':
            value = self.read_string('"')
            return Token(token_type=TokenType.STR, literal=value)

        if self.ch == "'":
            value = self.read_string("'")
            return Token(token_type=TokenType.STR, literal=value)

        tok = Token(token_type=TokenType.ILLEGAL, literal=self.ch)
        self.read_char()
        return tok

    def read_identifier(self) -> str:
        start_position = self.pos
        while self.ch != EOF_MARKER and (is_letter(
            self.ch) or is_digit(self.ch)
        ):
            self.read_char()
        return self.source[start_position : self.pos]

    def read_number(self) -> str:
        start_position = self.pos
        while self.ch != EOF_MARKER and is_digit(self.ch):
            self.read_char()
        return self.source[start_position : self.pos]

    def read_string(self, indicator: str = '"') -> str:
        self.read_char()

        start_position = self.pos
        out: str = self.ch

        while True:
            self.read_char()

            if self.ch == "\\" and self.peek_ahead(0) == indicator:
                self.read_char()
                out += indicator
                continue

            if self.ch == indicator or self.ch == EOF_MARKER:
                break

            out = out + self.ch

        self.read_char()
        return out

    def read_comment(self) -> str:
        start_position = self.pos
        while self.ch != "\n":
            self.read_char()
        return self.source[start_position + 2 : self.pos]

    def read_multiline_comment(self) -> str:
        start_position = self.pos
        while not (
            self.ch == "]"
            and self.peek_ahead(0) == "]"
            and self.peek_ahead(1) == "-"
            and self.peek_ahead(2) == "-"
        ):
            self.read_char()

        for _ in range(0, 4):
            self.read_char()

        return self.source[start_position + 4 : self.pos - 4]


def is_letter(char) -> bool:
    return bool(re.search(r"[a-zA-Z]|_", char))


def is_digit(char) -> bool:
    return bool(re.search(r"[0-9]", char))
