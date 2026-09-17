"""Abstract syntax tree nodes for Vega the Language."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias


@dataclass(frozen=True, slots=True)
class Expression:
    """Base class for expressions with a one-based source location."""

    line: int
    column: int


@dataclass(frozen=True, slots=True)
class NumberLiteral(Expression):
    value: int | float


@dataclass(frozen=True, slots=True)
class StringLiteral(Expression):
    value: str


@dataclass(frozen=True, slots=True)
class BooleanLiteral(Expression):
    value: bool


@dataclass(frozen=True, slots=True)
class Identifier(Expression):
    name: str


@dataclass(frozen=True, slots=True)
class InputExpression(Expression):
    prompt: Expression


@dataclass(frozen=True, slots=True)
class LengthExpression(Expression):
    value: Expression


@dataclass(frozen=True, slots=True)
class AbsoluteExpression(Expression):
    value: Expression


@dataclass(frozen=True, slots=True)
class NegativeExpression(Expression):
    value: Expression


@dataclass(frozen=True, slots=True)
class BinaryExpression(Expression):
    left: Expression
    operator: str
    right: Expression


@dataclass(frozen=True, slots=True)
class Statement:
    """Base class for statements with a one-based source location."""

    line: int
    column: int


@dataclass(frozen=True, slots=True)
class NumericDeclaration(Statement):
    name: str
    initializer: Expression


@dataclass(frozen=True, slots=True)
class StringDeclaration(Statement):
    name: str
    initializer: Expression


@dataclass(frozen=True, slots=True)
class BooleanDeclaration(Statement):
    name: str
    initializer: Expression


@dataclass(frozen=True, slots=True)
class ListDeclaration(Statement):
    name: str
    elements: tuple[Expression, ...]


@dataclass(frozen=True, slots=True)
class Assignment(Statement):
    name: str
    value: Expression


@dataclass(frozen=True, slots=True)
class PrintStatement(Statement):
    value: Expression


@dataclass(frozen=True, slots=True)
class ListExtendStatement(Statement):
    name: str
    values: tuple[Expression, ...]


@dataclass(frozen=True, slots=True)
class ExpressionStatement(Statement):
    expression: Expression


@dataclass(frozen=True, slots=True)
class ConditionalBranch:
    line: int
    column: int
    condition: Expression
    body: tuple[Statement, ...]


@dataclass(frozen=True, slots=True)
class ConditionalStatement(Statement):
    branches: tuple[ConditionalBranch, ...]
    else_body: tuple[Statement, ...] | None


@dataclass(frozen=True, slots=True)
class FunctionParameter:
    line: int
    column: int
    type_name: str
    name: str


@dataclass(frozen=True, slots=True)
class FunctionDeclaration(Statement):
    name: str
    parameters: tuple[FunctionParameter, ...]
    body: tuple[Statement, ...]


@dataclass(frozen=True, slots=True)
class FunctionCallStatement(Statement):
    name: str
    arguments: tuple[Expression, ...]


@dataclass(frozen=True, slots=True)
class TryCatchStatement(Statement):
    try_body: tuple[Statement, ...]
    catch_body: tuple[Statement, ...]


ExpressionNode: TypeAlias = (
    NumberLiteral
    | StringLiteral
    | BooleanLiteral
    | Identifier
    | InputExpression
    | LengthExpression
    | AbsoluteExpression
    | NegativeExpression
    | BinaryExpression
)
StatementNode: TypeAlias = (
    NumericDeclaration
    | StringDeclaration
    | BooleanDeclaration
    | ListDeclaration
    | Assignment
    | PrintStatement
    | ListExtendStatement
    | ExpressionStatement
    | ConditionalStatement
    | FunctionDeclaration
    | FunctionCallStatement
    | TryCatchStatement
)


@dataclass(frozen=True, slots=True)
class Program:
    statements: tuple[StatementNode, ...]
    line: int = 1
    column: int = 1


__all__ = [
    "AbsoluteExpression",
    "Assignment",
    "BinaryExpression",
    "BooleanDeclaration",
    "BooleanLiteral",
    "ConditionalBranch",
    "ConditionalStatement",
    "Expression",
    "ExpressionNode",
    "ExpressionStatement",
    "FunctionCallStatement",
    "FunctionDeclaration",
    "FunctionParameter",
    "Identifier",
    "InputExpression",
    "LengthExpression",
    "ListDeclaration",
    "ListExtendStatement",
    "NegativeExpression",
    "NumberLiteral",
    "NumericDeclaration",
    "PrintStatement",
    "Program",
    "Statement",
    "StatementNode",
    "StringDeclaration",
    "StringLiteral",
    "TryCatchStatement",
]
