from io import StringIO
import unittest

from luatopy.lexer import Lexer
from luatopy.parser import Parser
from luatopy import obj
from luatopy import evaluator


class EvaluatorTest(unittest.TestCase):
    def test_integer_expressions(self):
        tests = [
            ("1", 1),
            ("10", 10),
            ("-1", -1),
            ("-10", -10),
            ("5 + 5 + 3 + 7", 20),
            ("5 - 5", 0),
            ("1 * 5 * 5", 25),
            ("-10 * 5 + 5 * (2 + 2)", -30),
        ]

        for source, expected in tests:
            evaluated = source_to_eval(source)

            self.assertEqual(type(evaluated), obj.Integer)
            self.assertEqual(evaluated.value, expected)

    def test_float_expressions(self):
        tests = [
            ("4 / 2", 2.0),
        ]

        for source, expected in tests:
            evaluated = source_to_eval(source)

            self.assertEqual(type(evaluated), obj.Float)
            self.assertEqual(evaluated.value, expected)

    def test_boolean_expressions(self):
        tests = [
            ("false", False),
            ("true", True),
            ("1 > 2", False),
            ("1 >= 2", False),
            ("1 < 2", True),
            ("1 <= 2", True),
            ("1 == 1", True),
            ("1 ~= 1", False),
            ("1 == 2", False),
            ("1 ~= 2", True),
            ("(2 > 1) == true", True),
            ("(2 < 1) == false", True),
        ]

        for source, expected in tests:
            evaluated = source_to_eval(source)

            self.assertEqual(type(evaluated), obj.Boolean)
            self.assertEqual(evaluated.value, expected)

    def test_not_prefix_operator(self):
        tests = [
            ("not false", True),
            ("not 5", False),
            ("not 0", False),
            ("not not 0", True),
            ("not not true", True),
        ]

        for source, expected in tests:
            evaluated = source_to_eval(source)

            self.assertEqual(type(evaluated), obj.Boolean)
            self.assertEqual(evaluated.value, expected)

    def test_if_else_expressions(self):
        tests = [
            ("if true then 10 end", 10),
            ("if 1 then 10 end", 10),
            ("if false then 10 end", evaluator.NULL),
            ("if 10 > 5 then 10 end", 10),
            ("if 5 < 2 then 10 end", evaluator.NULL),
            ("if false then 10 else 5 end", 5),
            ("if true then 10 else 5 end", 10),
        ]

        for source, expected in tests:
            evaluated = source_to_eval(source)

            if evaluated == evaluator.NULL:
                self.assertEqual(evaluated, expected)
            else:
                self.assertEqual(evaluated.value, expected)

    def test_return_statements(self):
        tests = [
            ("return 5", 5),
            ("""return 5
10
""", 5),
            ("return 5*5", 25),
            ("""10
return 5
""", 5),
            ("""
             if true then
                if true then
                    return 10
                end
                return 5
             end
             """, 10),
        ]

        for source, expected in tests:
            evaluated = source_to_eval(source)

            self.assertEqual(type(evaluated), obj.Integer)
            self.assertEqual(evaluated.value, expected)

    def test_error_handling(self):
        tests = [
            ("1 + true", "Attempt to perform arithmetic on a boolean value"),
            ("-true", "Attempt to perform arithmetic on a boolean value"),
            (
"""1 + true
5
""", "Attempt to perform arithmetic on a boolean value"),
            ("true + false", "Attempt to perform arithmetic on a boolean value"),
            (
                "if true then true + false end",
                "Attempt to perform arithmetic on a boolean value"
            ),
            (
                "if true then if true then true + false end end",
                "Attempt to perform arithmetic on a boolean value"
            ),
(
"""5
true + false
6
""", "Attempt to perform arithmetic on a boolean value"),
            (
                "if true then if true then return true + false end return 5 end",
                "Attempt to perform arithmetic on a boolean value"
            ),
            (
                "if true + false then 1 else 2 end",
                "Attempt to perform arithmetic on a boolean value"
            ),
            ("foobar", "Identifier foobar not found"),  # TODO: lua returns nil
        ]

        for source, expected in tests:
            evaluated = source_to_eval(source)

            self.assertEqual(type(evaluated), obj.Error)
            self.assertEqual(evaluated.message, expected)

    def test_assignments(self):
        tests = [
            ("""a = 5
a""", 5),
            ("""a = 5 * 5
a""", 25),
            ("""a = 5
b = a
b""", 5),

            ("""a = 5
b = a
c = a + b
c""", 10),
        ]

        for source, expected in tests:
            evaluated = source_to_eval(source)

            self.assertEqual(type(evaluated), obj.Integer)
            self.assertEqual(evaluated.value, expected)


    def test_function_declaration(self):
        tests = [
            ("function (a) a + 1 end", "function (a) (a + 1) end"),
        ]

        for source, expected in tests:
            evaluated = source_to_eval(source)

            self.assertEqual(type(evaluated), obj.Function)
            self.assertEqual(evaluated.inspect(), expected)


def source_to_eval(source) -> obj.Obj:
    lexer = Lexer(StringIO(source))
    parser = Parser(lexer)
    program = parser.parse_program()
    env = obj.Environment()
    return evaluator.evaluate(program, env)
