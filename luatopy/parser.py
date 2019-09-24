from typing import Optional, Dict, Callable, List, cast, Tuple
from enum import IntEnum, auto

from .token import TokenType, Token
from .lexer import Lexer
from . import ast


class Precedence(IntEnum):
    """
    From lua docs:
    --------------
    and   or
    <   >   <=  >=  ~=  ==
    ..
    +   -
    *   /
    not  - (unary)
    ^
    """

    LOWEST = 0
    EQUALS = 1
    LESSGREATER = 2
    CONCAT = 3
    SUM = 4
    PRODUCT = 5
    PREFIX = 6
    CALL = 7
    INDEX = 8


precedences: Dict[TokenType, Precedence] = {
    TokenType.PLUS: Precedence.SUM,
    TokenType.MINUS: Precedence.SUM,
    TokenType.ASTERISK: Precedence.PRODUCT,
    TokenType.SLASH: Precedence.PRODUCT,
    TokenType.PERCENT: Precedence.PRODUCT,
    TokenType.EQ: Precedence.EQUALS,
    TokenType.NOT_EQ: Precedence.EQUALS,
    TokenType.GT: Precedence.LESSGREATER,
    TokenType.GTE: Precedence.LESSGREATER,
    TokenType.LT: Precedence.LESSGREATER,
    TokenType.LTE: Precedence.LESSGREATER,
    TokenType.LPAREN: Precedence.CALL,
    TokenType.IF: Precedence.CALL,
    TokenType.CONCAT: Precedence.CONCAT,
    TokenType.LBRACKET: Precedence.INDEX,
}


class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer: Lexer = lexer
        self.errors: List[str] = []

        self.prefix_parse_fns: Dict[TokenType, Callable] = {
            TokenType.IDENTIFIER: self.parse_identifier,
            TokenType.INT: self.parse_integer_literal,
            TokenType.STR: self.parse_string_literal,
            TokenType.MINUS: self.parse_prefix_expression,
            TokenType.HASH: self.parse_prefix_expression,
            TokenType.TRUE: self.parse_boolean_literal,
            TokenType.FALSE: self.parse_boolean_literal,
            TokenType.LPAREN: self.parse_grouped_expression,
            TokenType.IF: self.parse_if_expression,
            TokenType.FUNCTION: self.parse_function_literal,
            TokenType.NOT: self.parse_prefix_expression,
            TokenType.LBRACE: self.parse_table_literal,  # {
        }

        self.infix_parse_fns: Dict[
            TokenType, Callable[[ast.Node], ast.Node]
        ] = {
            TokenType.PLUS: self.parse_infix_expression,
            TokenType.MINUS: self.parse_infix_expression,
            TokenType.ASTERISK: self.parse_infix_expression,
            TokenType.PERCENT: self.parse_infix_expression,
            TokenType.SLASH: self.parse_infix_expression,
            TokenType.EQ: self.parse_infix_expression,
            TokenType.NOT_EQ: self.parse_infix_expression,
            TokenType.GT: self.parse_infix_expression,
            TokenType.GTE: self.parse_infix_expression,
            TokenType.LT: self.parse_infix_expression,
            TokenType.LTE: self.parse_infix_expression,
            TokenType.LPAREN: self.parse_call_expression,
            TokenType.CONCAT: self.parse_infix_expression,
            TokenType.LBRACKET: self.parse_index_expression,
        }

        self.table_prefix_fns = {
            TokenType.IDENTIFIER: self.parse_table_identifier_pair,
            TokenType.LBRACKET: self.parse_table_expression_pair,
        }

        self.cur_token: Token = self.lexer.next_token()
        self.peek_token: Token = self.lexer.next_token()

        # self.next_token()
        # self.next_token()

    def next_token(self) -> None:
        self.cur_token = self.peek_token
        self.peek_token = self.lexer.next_token()

    def parse_program(self) -> ast.Program:
        statements = []
        while self.cur_token.token_type != TokenType.EOF:
            if self.cur_token.token_type in [
                TokenType.NEWLINE,
                TokenType.SEMICOLON,
            ]:
                self.next_token()
                continue

            statement = self.parse_statement()
            statements.append(statement)
            self.next_token()

        return ast.Program(statements)

    def parse_statement(self) -> ast.Node:
        if (
            self.cur_token.token_type == TokenType.IDENTIFIER
            and self.peek_token.token_type == TokenType.ASSIGN
        ):
            return self.parse_assignment_statement()

        if self.cur_token.token_type == TokenType.RETURN:
            return self.parse_return_statement()

        return self.parse_expression_statement()

    def parse_assignment_statement(self):
        token = self.cur_token

        self.next_token()
        self.next_token()  # We already know the next statement is =

        value = self.parse_expression(Precedence.LOWEST)

        if self.peek_token.token_type in [
            TokenType.NEWLINE,
            TokenType.SEMICOLON,
        ]:
            self.next_token()

        statement = ast.AssignStatement(
            token=token,
            name=ast.Identifier(token=token, value=token.literal),
            value=value,
        )
        return statement

    def parse_return_statement(self) -> ast.ReturnStatement:
        token = self.cur_token
        self.next_token()

        value = self.parse_expression(Precedence.LOWEST)
        return ast.ReturnStatement(token=token, value=value)

    def parse_if_expression(self):
        token = self.cur_token

        self.next_token()
        condition = self.parse_expression(Precedence.LOWEST)

        if not self.expect_peek(TokenType.THEN):
            return None

        consequence = self.parse_block_statement()
        alternative = None

        if self.cur_token.token_type == TokenType.ELSE:
            alternative = self.parse_block_statement()

        return ast.IfExpression(
            token=token,
            condition=condition,
            consequence=consequence,
            alternative=alternative,
        )

    def parse_block_statement(self):
        token = self.cur_token
        statements: List[ast.Statement] = []

        self.next_token()

        while (
            self.cur_token.token_type != TokenType.END
            and self.cur_token.token_type != TokenType.ELSE
            and self.cur_token.token_type != TokenType.EOF
        ):
            statement = self.parse_statement()

            if statement:
                statements.append(statement)

            self.next_token()

        return ast.BlockStatement(token=token, statements=statements)

    def parse_expression_statement(self) -> ast.ExpressionStatement:
        expression = self.parse_expression(Precedence.LOWEST)

        return ast.ExpressionStatement(
            token=self.cur_token, expression=expression
        )

    def parse_expression(self, precedence: Precedence):
        prefix_fn = self.prefix_parse_fns.get(self.cur_token.token_type, None)

        if not prefix_fn:
            self.errors.append(
                "No prefix fn found for {0}".format(self.cur_token.token_type)
            )
            # Add error reporting
            return None

        left_expression = prefix_fn()

        while (
            self.peek_token.token_type
            not in [TokenType.NEWLINE, TokenType.SEMICOLON]
            and precedence < self.peek_precedence()
        ):
            infix_fn = self.infix_parse_fns.get(
                self.peek_token.token_type, None
            )
            if not infix_fn:
                return left_expression

            self.next_token()
            left_expression = infix_fn(left_expression)

        return left_expression

    def parse_identifier(self):
        value = self.cur_token.literal
        return ast.Identifier(token=self.cur_token, value=value)

    def parse_integer_literal(self) -> ast.IntegerLiteral:
        literal = self.cur_token.literal
        value = int(literal)
        return ast.IntegerLiteral(token=self.cur_token, value=value)

    def parse_string_literal(self) -> ast.StringLiteral:
        literal = self.cur_token.literal
        value = literal
        return ast.StringLiteral(token=self.cur_token, value=value)

    def parse_boolean_literal(self) -> ast.Boolean:
        literal = self.cur_token.literal
        value = literal == "true"
        return ast.Boolean(token=self.cur_token, value=value)

    def parse_function_literal(self):
        token = self.cur_token
        name = None

        if self.peek_token.token_type == TokenType.IDENTIFIER:
            self.next_token()
            name = ast.Identifier(
                token=self.cur_token, value=self.cur_token.literal
            )

        if not self.expect_peek(TokenType.LPAREN):
            return None

        parameters = self.parse_function_parameters()

        body = self.parse_block_statement()
        return ast.FunctionLiteral(
            token=token, parameters=parameters, body=body, name=name
        )

    def parse_function_parameters(self):
        identifiers: List[Identifier] = []

        if self.peek_token.token_type == TokenType.RPAREN:
            self.next_token()
            return identifiers

        self.next_token()
        identifier = ast.Identifier(
            token=self.cur_token, value=self.cur_token.literal
        )
        identifiers.append(identifier)

        while self.peek_token.token_type == TokenType.COMMA:
            self.next_token()
            self.next_token()

            identifier = ast.Identifier(
                token=self.cur_token, value=self.cur_token.literal
            )
            identifiers.append(identifier)

        if not self.expect_peek(TokenType.RPAREN):
            return None

        return identifiers

    def cur_precedence(self) -> Precedence:
        return precedences.get(self.cur_token.token_type, Precedence.LOWEST)

    def peek_precedence(self) -> Precedence:
        return precedences.get(self.peek_token.token_type, Precedence.LOWEST)

    def parse_prefix_expression(self) -> ast.PrefixExpression:
        token = self.cur_token

        self.next_token()
        right = self.parse_expression(Precedence.PREFIX)

        return ast.PrefixExpression(
            token=token, right=right, operator=token.literal
        )

    def parse_infix_expression(self, left: ast.Node) -> ast.InfixExpression:
        token = self.cur_token

        precedence = self.cur_precedence()

        self.next_token()
        right = self.parse_expression(precedence)

        return ast.InfixExpression(
            token=token, left=left, operator=token.literal, right=right
        )

    def parse_call_expression(self, function: ast.Node) -> ast.CallExpression:
        token = self.cur_token
        arguments = self.parse_call_arguments()

        return ast.CallExpression(
            token=token, function=function, arguments=arguments
        )

    def parse_call_arguments(self):
        arguments: List[ast.Expression] = []

        if self.peek_token.token_type == TokenType.RPAREN:
            self.next_token()
            return arguments

        self.next_token()
        arguments.append(self.parse_expression(Precedence.LOWEST))

        while self.peek_token.token_type == TokenType.COMMA:
            self.next_token()
            self.next_token()

            identifier = ast.Identifier(
                token=self.cur_token, value=self.cur_token.literal
            )

            arguments.append(self.parse_expression(Precedence.LOWEST))

        if not self.expect_peek(TokenType.RPAREN):
            return None

        return arguments

    def parse_grouped_expression(self):
        self.next_token()

        expression = self.parse_expression(Precedence.LOWEST)

        if not self.expect_peek(TokenType.RPAREN):
            return None

        return expression

    def expect_peek(self, token_type: TokenType) -> bool:
        if self.peek_token.token_type != token_type:
            self.errors.append(
                "Expected next token to be {0}, got {1}".format(
                    token_type, self.peek_token.token_type
                )
            )
            return False

        self.next_token()
        return True

    def parse_table_literal(self) -> ast.TableLiteral:
        token = self.cur_token
        elements = self.parse_table_expression_list()
        return ast.TableLiteral(token=token, elements=elements)

    def parse_table_expression_list(self):
        elements: List[Tuple[ast.Expression, ast.Expression]] = []

        if self.peek_token.token_type == TokenType.RBRACE:
            self.next_token()
            return []

        self.next_token()

        index: int = 1

        while True:
            parse_fn = self.table_prefix_fns.get(
                self.cur_token.token_type, self.parse_table_expression_value
            )
            element, pair = parse_fn()

            if element:
                elements.append(
                    (ast.IntegerLiteral(token=None, value=index), element)
                )
                index = index + 1
            elif pair:
                elements.append(pair)

            if self.peek_token.token_type == TokenType.RBRACE:
                break

            if not self.expect_peek(TokenType.COMMA):
                return None

            self.next_token()  # Bypass comma

        if not self.expect_peek(TokenType.RBRACE):
            return None

        return elements

    def parse_table_identifier_pair(self):
        key_token: Token = self.cur_token

        self.next_token()
        self.next_token()

        expression = self.parse_expression(Precedence.LOWEST)
        return (
            None,
            (
                ast.StringLiteral(token=key_token, value=key_token.literal),
                expression,
            ),
        )

    def parse_table_expression_value(self):
        expression = self.parse_expression(Precedence.LOWEST)
        return (expression, None)

    def parse_table_expression_pair(self):
        self.next_token()

        key_expression = self.parse_expression(Precedence.LOWEST)

        self.next_token()
        self.next_token()
        self.next_token()

        value_expression = self.parse_expression(Precedence.LOWEST)

        return (None, (key_expression, value_expression))

    def parse_index_expression(self, left: ast.Node):
        left_expression = cast(ast.Expression, left)
        token = self.cur_token

        self.next_token()
        index = self.parse_expression(Precedence.LOWEST)

        if not self.expect_peek(TokenType.RBRACKET):
            return None

        return ast.IndexExpression(
            token=token, left=left_expression, index=index
        )
