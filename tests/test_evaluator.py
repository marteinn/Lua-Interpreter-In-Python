from io import StringIO
import unittest

from luatopy.lexer import Lexer
from luatopy.parser import Parser
from luatopy import obj
from luatopy import evaluator


class EvaluatorTest(unittest.TestCase):
    def test_integer_expressions(self):
        tests = [
            ("10", 10),
            ("1", 1),
        ]

        for source, expected in tests:
            evaluated = source_to_eval(source)

            self.assertEqual(type(evaluated), obj.Integer)
            self.assertEqual(evaluated.value, expected)

    def test_boolean_expressions(self):
        tests = [
            ("false", False),
            ("true", True),
        ]

        for source, expected in tests:
            evaluated = source_to_eval(source)

            self.assertEqual(type(evaluated), obj.Boolean)
            self.assertEqual(evaluated.value, expected)


def source_to_eval(source) -> obj.Obj:
    lexer = Lexer(StringIO(source))
    parser = Parser(lexer)
    program = parser.parse_program()
    return evaluator.evaluate(program)
