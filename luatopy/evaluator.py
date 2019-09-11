from typing import cast, Optional

from . import ast
from . import obj


TRUE = obj.Boolean(value=True)
FALSE = obj.Boolean(value=False)
NULL = obj.Null()


def evaluate(node: ast.Node):
    klass = type(node)

    if klass == ast.Program:
        program: ast.Program = cast(ast.Program, node)
        return evaluate_program(program)

    if klass == ast.ExpressionStatement:
        exp: ast.ExpressionStatement = cast(ast.ExpressionStatement, node)
        return evaluate(exp.expression)

    if klass == ast.IntegerLiteral:
        integer_literal: ast.IntegerLiteral = cast(ast.IntegerLiteral, node)
        return obj.Integer(value=integer_literal.value)

    if klass == ast.Boolean:
        boolean: ast.Boolean = cast(ast.Boolean, node)
        return native_bool_to_bool_obj(boolean.value)

    if klass == ast.PrefixExpression:
        prefix_exp: ast.PrefixExpression = cast(ast.PrefixExpression, node)
        prefix_right: obj.Obj = evaluate(prefix_exp.right)
        return evaluate_prefix_expression(prefix_exp.operator, prefix_right)

    if klass == ast.InfixExpression:
        infix_exp: ast.InfixExpression = cast(ast.InfixExpression, node)
        infix_left: obj.Obj = evaluate(infix_exp.left)
        infix_right: obj.Obj = evaluate(infix_exp.right)
        return evaluate_infix_expression(
            infix_exp.operator, infix_left, infix_right
        )

    if klass == ast.BlockStatement:
        block_statement: ast.BlockStatement = cast(ast.BlockStatement, node)
        return evaluate_block_statement(block_statement)

    if klass == ast.IfExpression:
        if_exp: ast.IfExpression = cast(ast.IfExpression, node)
        return eval_if_expression(if_exp)

    if klass == ast.ReturnStatement:
        return_statement: ast.ReturnStatement = cast(ast.ReturnStatement, node)
        return_value: obj.Obj = evaluate(return_statement.value)
        return obj.ReturnValue(return_value)

    return None


def evaluate_program(program: ast.Program):
    result = None
    for statement in program.statements:
        result = evaluate(statement)

        if type(result) == obj.ReturnValue:
            return_value: obj.ReturnValue = cast(obj.ReturnValue, result)
            return return_value.value

    return result


def evaluate_block_statement(block_statement: ast.BlockStatement):
    result = None
    for statement in block_statement.statements:
        result = evaluate(statement)
        if result != None and result.type() == obj.ObjType.RETURN:
            return result

    return result


def eval_if_expression(if_exp: ast.IfExpression):
    condition = evaluate(if_exp.condition)

    if is_truthy(condition):
        return evaluate(if_exp.consequence)
    elif if_exp.alternative:
        return evaluate(if_exp.alternative)
    return NULL


def is_truthy(obj: obj.Obj) -> bool:
    if obj == NULL:
        return False
    if obj == TRUE:
        return True
    if obj == FALSE:
        return False
    return True


def evaluate_statements(statements):
    result = None
    for statement in statements:
        result = evaluate(statement)

        if type(result) == obj.ReturnValue:
            return_value: obj.ReturnValue = cast(obj.ReturnValue, result)
            return return_value.value

    return result


def evaluate_prefix_expression(operator: str, right: obj.Obj) -> obj.Obj:
    if operator == "not":
        return evaluate_not_operator_expression(right)
    if operator == "-":
        return evaluate_minus_operator_expression(right)
    return NULL


def evaluate_not_operator_expression(right: obj.Obj) -> obj.Boolean:
    if right == TRUE:
        return FALSE
    if right == FALSE:
        return TRUE
    if right == NULL:
        return TRUE
    return FALSE


def evaluate_minus_operator_expression(right: obj.Obj) -> obj.Obj:
    if type(right) != obj.Integer:
        return NULL

    obj_int = cast(obj.Integer, right)
    return obj.Integer(value=0 - obj_int.value)


def evaluate_infix_expression(
    operator: str, left: obj.Obj, right: obj.Obj
) -> obj.Obj:
    if type(left) == obj.Integer and type(right) == obj.Integer:
        left_val = cast(obj.Integer, left)
        right_val = cast(obj.Integer, right)
        return evaluate_infix_integer_expression(operator, left_val, right_val)

    if operator == "==":
        return native_bool_to_bool_obj(left == right)

    if operator == "~=":
        return native_bool_to_bool_obj(left != right)

    return NULL


def evaluate_infix_integer_expression(
    operator, left: obj.Integer, right: obj.Integer
) -> obj.Obj:
    if operator == "+":
        return obj.Integer(left.value + right.value)

    if operator == "-":
        return obj.Integer(left.value - right.value)

    if operator == "*":
        return obj.Integer(left.value * right.value)

    if operator == "/":
        return obj.Float(left.value / right.value)

    if operator == ">":
        return native_bool_to_bool_obj(left.value > right.value)

    if operator == ">=":
        return native_bool_to_bool_obj(left.value >= right.value)

    if operator == "<":
        return native_bool_to_bool_obj(left.value < right.value)

    if operator == "<=":
        return native_bool_to_bool_obj(left.value <= right.value)

    if operator == "==":
        return native_bool_to_bool_obj(left.value == right.value)

    if operator == "~=":
        return native_bool_to_bool_obj(left.value != right.value)

    return NULL


def native_bool_to_bool_obj(value: bool) -> obj.Boolean:
    return TRUE if value else FALSE
