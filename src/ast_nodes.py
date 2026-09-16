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
class Identifier(Expression):
    name: str


@dataclass(frozen=True, slots=True)
class InputExpression(Expression):
    prompt: Expression


@dataclass(frozen=True, slots=True)
class LengthExpression(Expression):
    value: Expression


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


ExpressionNode: TypeAlias = (
    NumberLiteral | StringLiteral | Identifier | InputExpression | LengthExpression
)
StatementNode: TypeAlias = (
    NumericDeclaration
    | StringDeclaration
    | ListDeclaration
    | Assignment
    | PrintStatement
    | ListExtendStatement
    | ExpressionStatement
)


@dataclass(frozen=True, slots=True)
class Program:
    statements: tuple[StatementNode, ...]
    line: int = 1
    column: int = 1


__all__ = [
    "Assignment",
    "Expression",
    "ExpressionNode",
    "ExpressionStatement",
    "Identifier",
    "InputExpression",
    "LengthExpression",
    "ListDeclaration",
    "ListExtendStatement",
    "NumberLiteral",
    "NumericDeclaration",
    "PrintStatement",
    "Program",
    "Statement",
    "StatementNode",
    "StringDeclaration",
    "StringLiteral",
]
