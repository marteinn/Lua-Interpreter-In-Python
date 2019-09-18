from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple

from .token import Token


class Program:
    def __init__(self, statements):
        self.statements = statements

    def to_code(self) -> str:
        out = [x.to_code() for x in self.statements]
        return "\n".join(out)


@dataclass
class Node:
    token: Token

    def to_code(self) -> str:
        pass


@dataclass
class Identifier(Node):
    value: str

    def to_code(self) -> str:
        return self.value


class Statement(Node):
    pass


class Expression(Node):
    pass


@dataclass
class ReturnStatement(Statement):
    value: Expression

    def to_code(self) -> str:
        return "return {0}".format(self.value.to_code())


@dataclass
class Boolean(Node):
    value: bool

    def to_code(self) -> str:
        return "true" if self.value else "false"


@dataclass
class AssignStatement(Statement):
    name: Identifier
    value: Node

    def to_code(self) -> str:
        return "{0} = {1}".format(self.name.value, self.value.to_code())


@dataclass
class ExpressionStatement(Statement):
    expression: Expression

    def to_code(self) -> str:
        if not self.expression:
            return ""
        return self.expression.to_code()


@dataclass
class IntegerLiteral(Node):
    value: int

    def to_code(self) -> str:
        return str(self.value)


@dataclass
class StringLiteral(Node):
    value: str

    def to_code(self) -> str:
        return '"{0}"'.format(self.value)


@dataclass
class PrefixExpression(Expression):
    right: Node
    operator: str

    def to_code(self) -> str:
        if len(self.operator) > 1:
            return "({0} {1})".format(self.operator, self.right.to_code())
        return "({0}{1})".format(self.operator, self.right.to_code())


@dataclass
class InfixExpression(Expression):
    left: Node
    operator: str
    right: Node

    def to_code(self) -> str:
        return "({0} {1} {2})".format(
            self.left.to_code(), self.operator, self.right.to_code()
        )


@dataclass
class BlockStatement(Statement):
    statements: List[Node] = field(default_factory=list)

    def to_code(self) -> str:
        out = [x.to_code() for x in self.statements]
        return "\n".join(out)


@dataclass
class IfExpression(Expression):
    condition: Expression
    consequence: BlockStatement
    alternative: BlockStatement

    def to_code(self) -> str:
        out = "if {0} then ".format(self.condition.to_code())
        out = out + self.consequence.to_code()
        if self.alternative:
            out = out + " else "
            out = out + self.alternative.to_code()
        out = out + " end"
        return out


@dataclass
class FunctionLiteral(Node):
    body: BlockStatement
    parameters: List[Identifier] = field(default_factory=list)
    name: Optional[Identifier] = None

    def to_code(self) -> str:
        signature = ", ".join([x.value for x in self.parameters])

        if self.name:
            out = "function {0} ({1}) ".format(self.name.value, signature)
        else:
            out = "function ({0}) ".format(signature)

        body_code = self.body.to_code().strip()
        if body_code:
            out = out + body_code + " "
        return out + "end"


@dataclass
class CallExpression(Expression):
    function: Node
    arguments: List[Expression]

    def to_code(self) -> str:
        out = "{0}({1})".format(
            self.function.to_code(),
            ", ".join([x.to_code() for x in self.arguments]),
        )
        return out


@dataclass
class TableLiteral(Expression):
    elements: List[Expression]
    pairs: List[Tuple[Expression, Expression]] = field(
        default_factory=list
    )

    def to_code(self) -> str:
        out = "{"
        if self.elements:
            out = out + "{0}".format(
                ", ".join([x.to_code() for x in self.elements])
            )

        if self.elements and self.pairs:
            out = out + ", "

        if self.pairs:
            out = out + ", ".join(
                [f"{x[0].to_code()} = {x[1].to_code()}" for x in self.pairs]
            )

        out = out + "}"
        return out


@dataclass
class IndexExpression(Expression):
    left: Expression
    index: Expression

    def to_code(self) -> str:
        return "({0}[{1}])".format(self.left.to_code(), self.index.to_code())
