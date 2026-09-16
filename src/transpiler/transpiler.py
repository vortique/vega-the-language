"""Transpile a Vega abstract syntax tree to Python source code."""

from __future__ import annotations

from src.ast_nodes import (
    Assignment,
    ExpressionNode,
    ExpressionStatement,
    Identifier,
    InputExpression,
    LengthExpression,
    ListDeclaration,
    ListExtendStatement,
    NumberLiteral,
    NumericDeclaration,
    PrintStatement,
    Program,
    StatementNode,
    StringDeclaration,
    StringLiteral,
)


class Transpiler:
    """Generate deterministic Python source from a valid Vega AST."""

    def transpile(self, program: Program) -> str:
        if not program.statements:
            return ""
        lines = (self._statement(statement) for statement in program.statements)
        return "\n".join(lines) + "\n"

    def _statement(self, statement: StatementNode) -> str:
        if isinstance(statement, NumericDeclaration):
            name = self._name(statement.name)
            initializer = self._expression(statement.initializer)
            return f"{name} = {initializer}"
        if isinstance(statement, StringDeclaration):
            name = self._name(statement.name)
            initializer = self._expression(statement.initializer)
            return f"{name} = {initializer}"
        if isinstance(statement, ListDeclaration):
            elements = ", ".join(self._expression(item) for item in statement.elements)
            return f"{self._name(statement.name)} = [{elements}]"
        if isinstance(statement, Assignment):
            return f"{self._name(statement.name)} = {self._expression(statement.value)}"
        if isinstance(statement, PrintStatement):
            return f"print({self._expression(statement.value)})"
        if isinstance(statement, ListExtendStatement):
            values = ", ".join(self._expression(item) for item in statement.values)
            return f"{self._name(statement.name)}.extend([{values}])"
        if isinstance(statement, ExpressionStatement):
            return self._expression(statement.expression)
        raise TypeError(f"Unsupported Vega statement: {type(statement).__name__}")

    def _expression(self, expression: ExpressionNode) -> str:
        if isinstance(expression, NumberLiteral):
            return repr(expression.value)
        if isinstance(expression, StringLiteral):
            return repr(expression.value)
        if isinstance(expression, Identifier):
            return self._name(expression.name)
        if isinstance(expression, InputExpression):
            return f"input({self._expression(expression.prompt)})"
        if isinstance(expression, LengthExpression):
            return f"len({self._expression(expression.value)})"
        raise TypeError(f"Unsupported Vega expression: {type(expression).__name__}")

    @staticmethod
    def _name(name: str) -> str:
        return f"_vega_{name}"


def transpile(program: Program) -> str:
    """Transpile a Vega AST to Python source code."""

    return Transpiler().transpile(program)


__all__ = ["Transpiler", "transpile"]
