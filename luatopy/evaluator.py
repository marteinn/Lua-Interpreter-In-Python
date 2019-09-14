from typing import cast, Optional

from . import ast
from . import obj


TRUE = obj.Boolean(value=True)
FALSE = obj.Boolean(value=False)
NULL = obj.Null()


def evaluate(node: ast.Node, env: obj.Environment):
    klass = type(node)

    if klass == ast.Program:
        program: ast.Program = cast(ast.Program, node)
        return evaluate_program(program, env)

    if klass == ast.ExpressionStatement:
        exp: ast.ExpressionStatement = cast(ast.ExpressionStatement, node)
        return evaluate(exp.expression, env)

    if klass == ast.IntegerLiteral:
        integer_literal: ast.IntegerLiteral = cast(ast.IntegerLiteral, node)
        return obj.Integer(value=integer_literal.value)

    if klass == ast.Boolean:
        boolean: ast.Boolean = cast(ast.Boolean, node)
        return native_bool_to_bool_obj(boolean.value)

    if klass == ast.PrefixExpression:
        prefix_exp: ast.PrefixExpression = cast(ast.PrefixExpression, node)
        prefix_right: obj.Obj = evaluate(prefix_exp.right, env)

        if is_error(prefix_right):
            return prefix_right

        return evaluate_prefix_expression(prefix_exp.operator, prefix_right)

    if klass == ast.InfixExpression:
        infix_exp: ast.InfixExpression = cast(ast.InfixExpression, node)

        infix_left: obj.Obj = evaluate(infix_exp.left, env)
        if is_error(infix_left):
            return infix_left

        infix_right: obj.Obj = evaluate(infix_exp.right, env)
        if is_error(infix_right):
            return infix_right

        return evaluate_infix_expression(
            infix_exp.operator, infix_left, infix_right
        )

    if klass == ast.BlockStatement:
        block_statement: ast.BlockStatement = cast(ast.BlockStatement, node)
        return evaluate_block_statement(block_statement, env)

    if klass == ast.IfExpression:
        if_exp: ast.IfExpression = cast(ast.IfExpression, node)
        return eval_if_expression(if_exp, env)

    if klass == ast.ReturnStatement:
        return_statement: ast.ReturnStatement = cast(ast.ReturnStatement, node)
        return_value: obj.Obj = evaluate(return_statement.value, env)
        if is_error(return_value):
            return return_value
        return obj.ReturnValue(return_value)

    if klass == ast.AssignStatement:
        assignment: ast.AssignStatement = cast(ast.AssignStatement, node)
        assignment_value: obj.Obj = evaluate(assignment.value, env)
        if is_error(assignment_value):
            return assignment_value
        env.set(assignment.name.value, assignment_value)
        return None

    if klass == ast.Identifier:
        identifier: ast.Identifier = cast(ast.Identifier, node)
        return evaluate_identifier(identifier, env)

    return None


def evaluate_identifier(identifier: ast.Identifier, env: obj.Environment) -> obj.Obj:
    val, found = env.get(identifier.value, NULL)
    if not found:
        return obj.Error.create("Identifier {0} not found", identifier.value)

    return val


def evaluate_program(program: ast.Program, env: obj.Environment):
    result = None
    for statement in program.statements:
        result = evaluate(statement, env)

        if type(result) == obj.ReturnValue:
            return_value: obj.ReturnValue = cast(obj.ReturnValue, result)
            return return_value.value
        if type(result) == obj.Error:
            return result

    return result


def evaluate_block_statement(
    block_statement: ast.BlockStatement, env: obj.Environment
):
    result = None
    for statement in block_statement.statements:
        result = evaluate(statement, env)
        if result != None:
            if result.type() in [obj.ObjType.RETURN, obj.ObjType.ERROR]:
                return result

    return result


def eval_if_expression(if_exp: ast.IfExpression, env: obj.Environment):
    condition = evaluate(if_exp.condition, env)

    if is_error(condition):
        return condition

    if is_truthy(condition):
        return evaluate(if_exp.consequence, env)
    elif if_exp.alternative:
        return evaluate(if_exp.alternative, env)

    return NULL


def is_truthy(obj: obj.Obj) -> bool:
    if obj == NULL:
        return False
    if obj == TRUE:
        return True
    if obj == FALSE:
        return False
    return True


def evaluate_statements(statements, env: obj.Environment):
    result = None
    for statement in statements:
        result = evaluate(statement, env)

        if type(result) == obj.ReturnValue:
            return_value: obj.ReturnValue = cast(obj.ReturnValue, result)
            return return_value.value

    return result


def evaluate_prefix_expression(operator: str, right: obj.Obj) -> obj.Obj:
    if operator == "not":
        return evaluate_not_operator_expression(right)
    if operator == "-":
        return evaluate_minus_operator_expression(right)

    return obj.Error.create(
        "Unknown operator {0}{0}", operator, right.inspect()
    )


def evaluate_not_operator_expression(right: obj.Obj) -> obj.Boolean:
    if right == TRUE:
        return FALSE
    if right == FALSE:
        return TRUE
    if right == NULL:
        return TRUE
    return FALSE


def evaluate_minus_operator_expression(right: obj.Obj) -> obj.Obj:
    if right.type() == obj.ObjType.BOOLEAN:
        return obj.Error.create(
            "Attempt to perform arithmetic on a boolean value"
        )

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

    if obj.ObjType.BOOLEAN in [left.type(), right.type()] and operator in [
        "+",
        "-",
        "*",
        "/",
    ]:
        return obj.Error.create(
            "Attempt to perform arithmetic on a boolean value"
        )

    # if left.type() != right.type():
    # return obj.Error.create("Type mismatch")

    if operator == "==":
        return native_bool_to_bool_obj(left == right)

    if operator == "~=":
        return native_bool_to_bool_obj(left != right)

    return obj.Error.create("Unknown infix operator {0}", operator)


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


def is_error(instance: obj.Obj) -> bool:
    if instance == None:
        return False

    return instance.type() == obj.ObjType.ERROR
