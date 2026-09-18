"""Transpile a Vega abstract syntax tree to Python source code."""

from __future__ import annotations

from src.ast_nodes import (
    AbsoluteExpression,
    Assignment,
    BinaryExpression,
    BooleanDeclaration,
    BooleanLiteral,
    ConditionalStatement,
    ExpressionNode,
    ExpressionStatement,
    FunctionCallStatement,
    FunctionDeclaration,
    Identifier,
    IncrementStatement,
    InputExpression,
    LengthExpression,
    ListDeclaration,
    ListExtendStatement,
    ListLiteral,
    NegativeExpression,
    NumberLiteral,
    NumericDeclaration,
    PrintStatement,
    Program,
    RangeExpression,
    Statement,
    StringDeclaration,
    StringLiteral,
    TryCatchStatement,
)


class Transpiler:
    """Generate deterministic Python source from a valid Vega AST."""

    def transpile(self, program: Program) -> str:
        lines: list[str] = []
        for statement in program.statements:
            lines.extend(self._statement_lines(statement))
        if not lines:
            return ""
        return "\n".join(lines) + "\n"

    def _statement_lines(
        self, statement: Statement, indentation: int = 0
    ) -> list[str]:
        prefix = "    " * indentation

        if isinstance(
            statement,
            (NumericDeclaration, StringDeclaration, BooleanDeclaration),
        ):
            name = self._name(statement.name)
            initializer = self._expression(statement.initializer)
            if isinstance(statement, NumericDeclaration) and isinstance(
                statement.initializer, InputExpression
            ):
                initializer = f"int({initializer})"
            return [f"{prefix}{name} = {initializer}"]
        if isinstance(statement, ListDeclaration):
            initializer = self._expression(statement.initializer)
            return [f"{prefix}{self._name(statement.name)} = {initializer}"]
        if isinstance(statement, Assignment):
            value = self._expression(statement.value)
            return [f"{prefix}{self._name(statement.name)} = {value}"]
        if isinstance(statement, IncrementStatement):
            operator = "+=" if statement.amount > 0 else "-="
            return [f"{prefix}{self._name(statement.name)} {operator} 1"]
        if isinstance(statement, PrintStatement):
            return [f"{prefix}print({self._expression(statement.value)})"]
        if isinstance(statement, ListExtendStatement):
            values = ", ".join(
                self._expression(item) for item in statement.values
            )
            name = self._name(statement.name)
            return [f"{prefix}{name}.extend([{values}])"]
        if isinstance(statement, ExpressionStatement):
            return [f"{prefix}{self._expression(statement.expression)}"]
        if isinstance(statement, FunctionCallStatement):
            arguments = ", ".join(
                self._expression(item) for item in statement.arguments
            )
            return [f"{prefix}{self._name(statement.name)}({arguments})"]
        if isinstance(statement, ConditionalStatement):
            return self._conditional_lines(statement, indentation)
        if isinstance(statement, FunctionDeclaration):
            parameters = ", ".join(
                self._name(parameter.name) for parameter in statement.parameters
            )
            lines = [
                f"{prefix}def {self._name(statement.name)}({parameters}):"
            ]
            lines.extend(self._block_lines(statement.body, indentation + 1))
            return lines
        if isinstance(statement, TryCatchStatement):
            lines = [f"{prefix}try:"]
            lines.extend(self._block_lines(statement.try_body, indentation + 1))
            lines.append(f"{prefix}except Exception:")
            lines.extend(self._block_lines(statement.catch_body, indentation + 1))
            return lines
        raise TypeError(f"Unsupported Vega statement: {type(statement).__name__}")

    def _conditional_lines(
        self, statement: ConditionalStatement, indentation: int
    ) -> list[str]:
        prefix = "    " * indentation
        lines: list[str] = []

        for index, branch in enumerate(statement.branches):
            keyword = "if" if index == 0 else "elif"
            condition = self._expression(branch.condition)
            lines.append(f"{prefix}{keyword} {condition}:")
            lines.extend(self._block_lines(branch.body, indentation + 1))

        if statement.else_body is not None:
            lines.append(f"{prefix}else:")
            lines.extend(self._block_lines(statement.else_body, indentation + 1))
        return lines

    def _block_lines(
        self, statements: tuple[Statement, ...], indentation: int
    ) -> list[str]:
        lines: list[str] = []
        for statement in statements:
            lines.extend(self._statement_lines(statement, indentation))
        return lines

    def _expression(self, expression: ExpressionNode) -> str:
        if isinstance(expression, NumberLiteral):
            return repr(expression.value)
        if isinstance(expression, StringLiteral):
            return repr(expression.value)
        if isinstance(expression, BooleanLiteral):
            return "True" if expression.value else "False"
        if isinstance(expression, Identifier):
            return self._name(expression.name)
        if isinstance(expression, InputExpression):
            return f"input({self._expression(expression.prompt)})"
        if isinstance(expression, LengthExpression):
            return f"len({self._expression(expression.value)})"
        if isinstance(expression, AbsoluteExpression):
            return f"abs({self._expression(expression.value)})"
        if isinstance(expression, NegativeExpression):
            value = self._expression(expression.value)
            if isinstance(expression.value, NumberLiteral):
                return f"-{value}"
            return f"-({value})"
        if isinstance(expression, BinaryExpression):
            left = self._expression(expression.left)
            right = self._expression(expression.right)
            return f"({left} {expression.operator} {right})"
        if isinstance(expression, ListLiteral):
            elements = ", ".join(
                self._expression(item) for item in expression.elements
            )
            return f"[{elements}]"
        if isinstance(expression, RangeExpression):
            minimum = self._expression(expression.minimum)
            maximum = self._expression(expression.maximum)
            return f"list(range(({minimum} + 1), ({maximum} + 1)))"
        raise TypeError(f"Unsupported Vega expression: {type(expression).__name__}")

    @staticmethod
    def _name(name: str) -> str:
        return f"_vega_{name}"


def transpile(program: Program) -> str:
    """Transpile a Vega AST to Python source code."""

    return Transpiler().transpile(program)


__all__ = ["Transpiler", "transpile"]
