from io import StringIO
import unittest

from luatopy.lexer import Lexer
from luatopy.token import TokenType


class LexerTest(unittest.TestCase):
    def test_binary_op(self):
        source = """1 + 2
2-1
        """
        lexer = Lexer(StringIO(source))

        tokens = [
            (TokenType.INT, "1"),
            (TokenType.PLUS, "+"),
            (TokenType.INT, "2"),
            (TokenType.NEWLINE, "\n"),
            (TokenType.INT, "2"),
            (TokenType.MINUS, "-"),
            (TokenType.INT, "1"),
            (TokenType.NEWLINE, "\n"),
            (TokenType.EOF, "<<EOF>>"),
        ]

        for expected_token in tokens:
            token = lexer.next_token()

            self.assertEqual(expected_token[0], token.token_type)
            self.assertEqual(expected_token[1], token.literal)

    def test_that_eof_gets_retruned(self):
        source = ""
        lexer = Lexer(StringIO(source))

        tokens = [
            (TokenType.EOF, "<<EOF>>"),
        ]

        for expected_token in tokens:
            token = lexer.next_token()

            self.assertEqual(expected_token[0], token.token_type)
            self.assertEqual(expected_token[1], token.literal)

    def test_that_tokens_are_created_according_to_source(self):
        source = """num = 42
cat  = 5
-- Hello
--[[
Goodbye
]]--
cookie == 9
a = nil
a and b
a or b
a not b
myfun()
a,b
a ~= b
stra .. strb
1 > 2
2 >= 2
1 < 2
2 <= 2
2 * 2
"""

        lexer = Lexer(StringIO(source))

        tokens = [
            (TokenType.IDENTIFIER, "num"), (TokenType.ASSIGN, "="), (TokenType.INT, "42"),
            (TokenType.NEWLINE, "\n"),
            (TokenType.IDENTIFIER, "cat"), (TokenType.ASSIGN, "="), (TokenType.INT, "5"),
            (TokenType.NEWLINE, "\n"),
            (TokenType.COMMENT, " Hello"),
            (TokenType.NEWLINE, "\n"),
            (TokenType.COMMENT, "\nGoodbye\n"),
            (TokenType.NEWLINE, "\n"),
            (TokenType.IDENTIFIER, "cookie"), (TokenType.EQ, "=="), (TokenType.INT, "9"),
            (TokenType.NEWLINE, "\n"),
            (TokenType.IDENTIFIER, "a"), (TokenType.ASSIGN, "="), (TokenType.NIL, "nil"),
            (TokenType.NEWLINE, "\n"),
            (TokenType.IDENTIFIER, "a"), (TokenType.AND, "and"), (TokenType.IDENTIFIER, "b"),
            (TokenType.NEWLINE, "\n"),
            (TokenType.IDENTIFIER, "a"), (TokenType.OR, "or"), (TokenType.IDENTIFIER, "b"),
            (TokenType.NEWLINE, "\n"),
            (TokenType.IDENTIFIER, "a"), (TokenType.NOT, "not"), (TokenType.IDENTIFIER, "b"),
            (TokenType.NEWLINE, "\n"),
            (TokenType.IDENTIFIER, "myfun"), (TokenType.LPAREN, "("), (TokenType.RPAREN, ")"),
            (TokenType.NEWLINE, "\n"),
            (TokenType.IDENTIFIER, "a"), (TokenType.COMMA, ","), (TokenType.IDENTIFIER, "b"),
            (TokenType.NEWLINE, "\n"),
            (TokenType.IDENTIFIER, "a"), (TokenType.NOT_EQ, "~="), (TokenType.IDENTIFIER, "b"),
            (TokenType.NEWLINE, "\n"),
            (TokenType.IDENTIFIER, "stra"), (TokenType.CONCAT, ".."), (TokenType.IDENTIFIER, "strb"),
            (TokenType.NEWLINE, "\n"),
            (TokenType.INT, "1"), (TokenType.GT, ">"), (TokenType.INT, "2"),
            (TokenType.NEWLINE, "\n"),
            (TokenType.INT, "2"), (TokenType.GTE, ">="), (TokenType.INT, "2"),
            (TokenType.NEWLINE, "\n"),
            (TokenType.INT, "1"), (TokenType.LT, "<"), (TokenType.INT, "2"),
            (TokenType.NEWLINE, "\n"),
            (TokenType.INT, "2"), (TokenType.LTE, "<="), (TokenType.INT, "2"),
            (TokenType.NEWLINE, "\n"),
            (TokenType.INT, "2"), (TokenType.ASTERISK, "*"), (TokenType.INT, "2"),
            (TokenType.NEWLINE, "\n"),
            (TokenType.EOF, "<<EOF>>"),
        ]

        for expected_token in tokens:
            token = lexer.next_token()

            self.assertEqual(expected_token[0], token.token_type)
            self.assertEqual(expected_token[1], token.literal)

    def test_bool_tokens(self):
        source = """true
a = false
"""

        lexer = Lexer(StringIO(source))

        tokens = [
            (TokenType.TRUE, "true"),
            (TokenType.NEWLINE, "\n"),

            (TokenType.IDENTIFIER, "a"),
            (TokenType.ASSIGN, "="),
            (TokenType.FALSE, "false"),
            (TokenType.NEWLINE, "\n"),

            (TokenType.EOF, "<<EOF>>"),
        ]

        for expected_token in tokens:
            token = lexer.next_token()

            self.assertEqual(expected_token[0], token.token_type)
            self.assertEqual(expected_token[1], token.literal)

    def test_if_statement_keywords(self):
        source = "if true then 1 else 2 end"

        lexer = Lexer(StringIO(source))

        tokens = [
            (TokenType.IF, "if"),
            (TokenType.TRUE, "true"),
            (TokenType.THEN, "then"),
            (TokenType.INT, "1"),
            (TokenType.ELSE, "else"),
            (TokenType.INT, "2"),
            (TokenType.END, "end"),
            (TokenType.EOF, "<<EOF>>"),
        ]

        for expected_token in tokens:
            token = lexer.next_token()

            self.assertEqual(expected_token[0], token.token_type)
            self.assertEqual(expected_token[1], token.literal)

    def test_function_tokens(self):
        source = "function fib(n) return 1 end"
        lexer = Lexer(StringIO(source))

        tokens = [
            (TokenType.FUNCTION, "function"),
            (TokenType.IDENTIFIER, "fib"),
            (TokenType.LPAREN, "("),
            (TokenType.IDENTIFIER, "n"),
            (TokenType.RPAREN, ")"),
            (TokenType.RETURN, "return"),
            (TokenType.INT, "1"),
            (TokenType.END, "end"),
            (TokenType.EOF, "<<EOF>>"),
        ]

        for expected_token in tokens:
            token = lexer.next_token()

            self.assertEqual(expected_token[0], token.token_type)
            self.assertEqual(expected_token[1], token.literal)

    def test_call_tokens(self):
        source = "abc(n, 1+2, 3)"
        lexer = Lexer(StringIO(source))

        tokens = [
            (TokenType.IDENTIFIER, "abc"),
            (TokenType.LPAREN, "("),
            (TokenType.IDENTIFIER, "n"),
            (TokenType.COMMA, ","),
            (TokenType.INT, "1"),
            (TokenType.PLUS, "+"),
            (TokenType.INT, "2"),
            (TokenType.COMMA, ","),
            (TokenType.INT, "3"),
            (TokenType.RPAREN, ")"),
            (TokenType.EOF, "<<EOF>>"),
        ]

        for expected_token in tokens:
            token = lexer.next_token()

            self.assertEqual(expected_token[0], token.token_type)
            self.assertEqual(expected_token[1], token.literal)

    def test_semicolon_delimiter(self):
        source = "1; 2"
        lexer = Lexer(StringIO(source))

        tokens = [
            (TokenType.INT, "1"),
            (TokenType.SEMICOLON, ";"),
            (TokenType.INT, "2"),
            (TokenType.EOF, "<<EOF>>"),
        ]

        for expected_token in tokens:
            token = lexer.next_token()

            self.assertEqual(expected_token[0], token.token_type)
            self.assertEqual(expected_token[1], token.literal)

    def test_string_type(self):
        source = """"a random string"
"escape\\" value"
'another string'
'with escaped\\' indicator'
"""
        lexer = Lexer(StringIO(source))

        tokens = [
            (TokenType.STR, "a random string"),
            (TokenType.NEWLINE, "\n"),
            (TokenType.STR, 'escape" value'),
            (TokenType.NEWLINE, "\n"),
            (TokenType.STR, "another string"),
            (TokenType.NEWLINE, "\n"),
            (TokenType.STR, "with escaped' indicator"),
            (TokenType.NEWLINE, "\n"),
            (TokenType.EOF, "<<EOF>>"),
        ]

        for expected_token in tokens:
            token = lexer.next_token()

            self.assertEqual(expected_token[0], token.token_type)
            self.assertEqual(expected_token[1], token.literal)

    def test_table_list_declaration(self):
        source = "{1, 2}"

        lexer = Lexer(StringIO(source))

        tokens = [
            (TokenType.LBRACE, "{"),
            (TokenType.INT, "1"),
            (TokenType.COMMA, ","),
            (TokenType.INT, "2"),
            (TokenType.RBRACE, "}"),
            (TokenType.EOF, "<<EOF>>"),
        ]

        for expected_token in tokens:
            token = lexer.next_token()

            self.assertEqual(expected_token[0], token.token_type)
            self.assertEqual(expected_token[1], token.literal)

    def test_table_hashmap_declaration(self):
        source = "{random = 2}"

        lexer = Lexer(StringIO(source))

        tokens = [
            (TokenType.LBRACE, "{"),
            (TokenType.IDENTIFIER, "random"),
            (TokenType.ASSIGN, "="),
            (TokenType.INT, "2"),
            (TokenType.RBRACE, "}"),
            (TokenType.EOF, "<<EOF>>"),
        ]

        for expected_token in tokens:
            token = lexer.next_token()

            self.assertEqual(expected_token[0], token.token_type)
            self.assertEqual(expected_token[1], token.literal)

    def test_table_length_hash_char(self):
        source = "#{1, 2}"

        lexer = Lexer(StringIO(source))

        tokens = [
            (TokenType.HASH, "#"),
            (TokenType.LBRACE, "{"),
            (TokenType.INT, "1"),
            (TokenType.COMMA, ","),
            (TokenType.INT, "2"),
            (TokenType.RBRACE, "}"),
            (TokenType.EOF, "<<EOF>>"),
        ]

        for expected_token in tokens:
            token = lexer.next_token()

            self.assertEqual(expected_token[0], token.token_type)
            self.assertEqual(expected_token[1], token.literal)
