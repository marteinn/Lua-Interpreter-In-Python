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
        exp: ast.ExpressionStatement = cast(ast.ExpressionStatement, node)
        return evaluate(exp.expression)

    if klass == ast.IntegerLiteral:
        integer_literal: ast.IntegerLiteral = cast(ast.IntegerLiteral, node)
        return obj.Integer(value=integer_literal.value)

    if klass == ast.Boolean:
        boolean: ast.Boolean = cast(ast.Boolean, node)
        return TRUE if boolean.value else FALSE

    if klass == ast.PrefixExpression:
        prefix_exp: ast.PrefixExpression = cast(ast.PrefixExpression, node)
        right: obj.Obj = evaluate(prefix_exp.right)
        return evaluate_prefix_expression(prefix_exp.operator, right)

    return None


def evaluate_statements(statements):
    result = None
    for statement in statements:
        result = evaluate(statement)

    return result


def evaluate_prefix_expression(operator, right: obj.Obj) -> obj.Obj:
    if operator == "not":
        return evaluate_not_operator_expression(right)
    return NULL


def evaluate_not_operator_expression(right: obj.Obj) -> obj.Boolean:
    if right == TRUE:
        return FALSE
    if right == FALSE:
        return TRUE
    if right == NULL:
        return TRUE
    return FALSE
