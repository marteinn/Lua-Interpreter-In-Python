from io import StringIO
import unittest

from luatopy.lexer import Lexer
from luatopy.parser import Parser
from luatopy import ast


class ParserTest(unittest.TestCase):
    def test_prefix_parsing(self):
        tests = (
            ("-1", "(-1)"), ("not 1", "(not 1)"), ("not not 1", "(not (not 1))"),
            ('#{1, 2}', '(#{1 = 1, 2 = 2})'),
            ('#"hello"', '(#"hello")'),
        )

        for source, expected in tests:
            self.assertEqual(program_from_source(source).to_code(), expected)

    def test_influx_parsing(self):
        tests = (
            ("1 + 2", "(1 + 2)"),
            ("2-3", "(2 - 3)"),
            ("5 * 5", "(5 * 5)"),
            ("5 / 5", "(5 / 5)"),
            ("5 == 2", "(5 == 2)"),
            ("5 ~= 2", "(5 ~= 2)"),
            ("5 > 2", "(5 > 2)"),
            ("5 < 2", "(5 < 2)"),
            ("5 >= 2", "(5 >= 2)"),
            ("5 <= 2", "(5 <= 2)"),
            ("5 % 10", "(5 % 10)"),
            ("true and false", "(true and false)"),
            ("false or true", "(false or true)"),
        )

        for source, expected in tests:
            self.assertEqual(program_from_source(source).to_code(), expected)

    def test_string_influx_parsing(self):
        tests = (('"hello " .. "world"', '("hello " .. "world")'),)

        for source, expected in tests:
            self.assertEqual(program_from_source(source).to_code(), expected)

    def test_operator_precedence(self):
        tests = (
            ("1 + 2", "(1 + 2)"),
            ("1 + 2 + 3", "((1 + 2) + 3)"),
            ("-1 + 2", "((-1) + 2)"),
            ("1 + 2 * 3", "(1 + (2 * 3))"),
            ("1 + 2 / 3", "(1 + (2 / 3))"),
            ("1 * 2 + 3 / 4", "((1 * 2) + (3 / 4))"),
            ("a + b", "(a + b)"),
            ("a + b * c + d / e - f", "(((a + (b * c)) + (d / e)) - f)"),
            ("a == b", "(a == b)"),
            ("a == true", "(a == true)"),
            ("b ~= true", "(b ~= true)"),
            ("a+b(c*d)+e", "((a + b((c * d))) + e)"),
            ("add(a + b * c + d / e - f)", "add((((a + (b * c)) + (d / e)) - f))"),
            ("a * {1, 2}[b * c] * d", "((a * ({1 = 1, 2 = 2}[(b * c)])) * d)"),
        )

        for source, expected in tests:
            self.assertEqual(program_from_source(source).to_code(), expected)

    def test_operator_precedence_groups(self):
        tests = (
            ("-(1 + 2)", "(-(1 + 2))"),
            ("1 + (2 + 3)", "(1 + (2 + 3))"),
            ("1 + (2 + (1 - 3))", "(1 + (2 + (1 - 3)))"),
        )

        for source, expected in tests:
            self.assertEqual(program_from_source(source).to_code(), expected)

    def test_semicolon_delimiter(self):
        tests = (("1; b", 2), ("a = 1; b = 2;", 2), ("1 + 2; 3 + 3;d = 5; 5 * 5", 4))

        for source, expected in tests:
            program = program_from_source(source)
            self.assertEqual(len(program.statements), expected)

    def test_integer_literal(self):
        program = program_from_source("1")

        statement = program.statements[0]
        self.assertIs(type(statement), ast.ExpressionStatement)
        self.assertIs(type(statement.expression), ast.IntegerLiteral)

    def test_identifier(self):
        program = program_from_source("a")

        statement = program.statements[0]
        self.assertIs(type(statement), ast.ExpressionStatement)
        self.assertIs(type(statement.expression), ast.Identifier)

    def test_booleans(self):
        program = program_from_source("true")

        statement = program.statements[0]
        self.assertIs(type(statement), ast.ExpressionStatement)
        self.assertIs(type(statement.expression), ast.Boolean)
        self.assertIs(statement.expression.value, True)

    def test_variable_assign(self):
        self.assertEqual(program_from_source("a = 1").to_code(), "a = 1")
        self.assertEqual(program_from_source("a = b").to_code(), "a = b")
        self.assertEqual(program_from_source("a = false").to_code(), "a = false")

    def test_multiple_variable_assign(self):
        source = """a = 1
        b = 2
        c = true
        """

        program = program_from_source(source)
        self.assertEqual(len(program.statements), 3)
        self.assertEqual(program.statements[0].to_code(), "a = 1")
        self.assertEqual(program.statements[1].to_code(), "b = 2")
        self.assertEqual(program.statements[2].to_code(), "c = true")

    def test_if_statements(self):
        tests = (
            ("if 1 > 2 then 1 end", "if (1 > 2) then 1 end"),
            ("if 1 > 2 then 1 else 5 end", "if (1 > 2) then 1 else 5 end"),
            (
                "if 1 > 2 then if true then 1 end end",
                "if (1 > 2) then if true then 1 end end",
            ),
        )

        for source, expected in tests:
            self.assertEqual(program_from_source(source).to_code(), expected)

    def test_function_statements(self):
        tests = (
            ("function (x, y) x*y end", "function (x, y) (x * y) end"),
            ("function () 1 end", "function () 1 end"),
            ("function (x, y, z) 1 end", "function (x, y, z) 1 end"),
            ("function () end", "function () end"),
            ("function () return 1 end", "function () return 1 end"),
            ("function foo () return 1 end", "function foo () return 1 end"),
        )

        for source, expected in tests:
            self.assertEqual(program_from_source(source).to_code(), expected)

    def test_named_function_statements(self):
        tests = (
            ("function bar () 1 end", "function bar () 1 end"),
        )

        for source, expected in tests:
            self.assertEqual(program_from_source(source).to_code(), expected)

    def test_function_calls(self):
        tests = (
            ("abc(1, 2)", "abc(1, 2)"),
            ("random(m, 1+1*2)", "random(m, (1 + (1 * 2)))"),
        )

        for source, expected in tests:
            self.assertEqual(program_from_source(source).to_code(), expected)

    def test_return_statements(self):
        tests = (
            ("return 1", "return 1"),
            ("return 1+b", "return (1 + b)"),
            ("return false", "return false"),
        )

        for source, expected in tests:
            self.assertEqual(program_from_source(source).to_code(), expected)

    def test_string_literal(self):
        program = program_from_source('"hello world"')

        statement = program.statements[0]
        self.assertIs(type(statement), ast.ExpressionStatement)
        self.assertIs(type(statement.expression), ast.StringLiteral)

    def test_table_literal(self):
        program = program_from_source('{1, 2, "hello"}')

        statement = program.statements[0]
        self.assertIs(type(statement), ast.ExpressionStatement)
        self.assertIs(type(statement.expression), ast.TableLiteral)

    def test_table_key_value(self):
        tests = [
            ('{key = 1, ["key2"] = 2}', '{"key" = 1, "key2" = 2}'),
            ("{1, key = 2}", '{1 = 1, "key" = 2}'),
            ("{[a + b] = 2}", "{(a + b) = 2}"),
            ("{[a] = 2}", "{a = 2}"),
            ("{a = {1, 2}}", '{"a" = {1 = 1, 2 = 2}}'),
            ("{[1] = 2}", "{1 = 2}"),
            ('{"hello", "goodbye"}', '{1 = "hello", 2 = "goodbye"}'),
        ]

        for source, expected in tests:
            self.assertEqual(program_from_source(source).to_code(), expected)

    def test_parsing_index_expressions(self):
        program = program_from_source("values[1]")

        statement = program.statements[0]
        self.assertIs(type(statement), ast.ExpressionStatement)
        self.assertIs(type(statement.expression), ast.IndexExpression)
        self.assertIs(statement.expression.index.value, 1)


def program_from_source(source):
    lexer = Lexer(StringIO(source))
    parser = Parser(lexer)
    program = parser.parse_program()

    if len(parser.errors) > 0:
        print(parser.errors[0])

    return program
