from typing import cast

from . import ast
from . import obj


TRUE = obj.Boolean(value=True)
FALSE = obj.Boolean(value=False)
NULL = obj.Null()


def evaluate(node: ast.Node):
    klass = type(node)

    if klass == ast.Program:
        program: ast.Program = cast(ast.Program, node)
        return evaluate_statements(program.statements)

    if klass == ast.ExpressionStatement:
        return evaluate(node.expression)

    if klass == ast.IntegerLiteral:
        return obj.Integer(value=node.value)

    if klass == ast.Boolean:
        return TRUE if node.value else FALSE

    return None


def evaluate_statements(statements):
    result = None
    for statement in statements:
        result = evaluate(statement)

    return result
