"""Recursive-descent parser for Vega the Language."""

from __future__ import annotations

from collections.abc import Sequence

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
from src.lexer import Token, TokenType


class ParserError(SyntaxError):
    """Raised when a token sequence does not follow the Vega grammar."""

    def __init__(self, message: str, token: Token) -> None:
        self.message = message
        self.token = token
        self.line = token.line
        self.column = token.column
        super().__init__(f"{message} at line {token.line}, column {token.column}")


class Parser:
    """Build a Vega AST from lexer tokens."""

    def __init__(self, tokens: Sequence[Token]) -> None:
        if not tokens:
            raise ValueError("Parser requires a token sequence ending in EOF")
        if tokens[-1].type is not TokenType.EOF:
            raise ValueError("Parser token sequence must end in EOF")
        self.tokens = tokens
        self.current = 0

    def parse(self) -> Program:
        statements: list[StatementNode] = []
        self._skip_newlines()

        while not self._check(TokenType.EOF):
            statements.append(self._statement())
            if self._check(TokenType.EOF):
                break
            if not self._match(TokenType.NEWLINE):
                raise self._error(self._peek(), "Expected a newline after statement")
            self._skip_newlines()

        return Program(tuple(statements))

    def _statement(self) -> StatementNode:
        if self._match(TokenType.SAYISAL):
            return self._numeric_declaration(self._previous())
        if self._match(TokenType.DIZE):
            return self._string_declaration(self._previous())
        if self._match(TokenType.LISTE):
            return self._list_declaration(self._previous())
        if self._match(TokenType.YAZDIR):
            keyword = self._previous()
            return PrintStatement(keyword.line, keyword.column, self._expression())
        if self._check(TokenType.UZUNLUK):
            token = self._peek()
            return ExpressionStatement(token.line, token.column, self._expression())
        if self._match(TokenType.IDENTIFIER):
            return self._identifier_statement(self._previous())

        raise self._error(self._peek(), "Expected a statement")

    def _numeric_declaration(self, keyword: Token) -> NumericDeclaration:
        name = self._consume(TokenType.IDENTIFIER, "Expected a variable name")
        self._consume(TokenType.EQUAL, "Expected '=' after variable name")
        return NumericDeclaration(
            keyword.line, keyword.column, name.lexeme, self._expression()
        )

    def _string_declaration(self, keyword: Token) -> StringDeclaration:
        name = self._consume(TokenType.IDENTIFIER, "Expected a variable name")
        self._consume(TokenType.EQUAL, "Expected '=' after variable name")
        return StringDeclaration(
            keyword.line, keyword.column, name.lexeme, self._expression()
        )

    def _list_declaration(self, keyword: Token) -> ListDeclaration:
        name = self._consume(TokenType.IDENTIFIER, "Expected a list name")
        self._consume(TokenType.EQUAL, "Expected '=' after list name")
        self._consume(TokenType.LISTE, "Expected 'liste.yeni' after '='")
        self._consume(TokenType.DOT, "Expected '.' after 'liste'")
        self._consume(TokenType.YENI, "Expected 'yeni' after 'liste.'")
        return ListDeclaration(
            keyword.line,
            keyword.column,
            name.lexeme,
            self._expression_list("Expected at least one list element"),
        )

    def _identifier_statement(self, name: Token) -> StatementNode:
        if self._match(TokenType.EQUAL):
            return Assignment(
                name.line, name.column, name.lexeme, self._expression()
            )
        if self._match(TokenType.DOT):
            self._consume(TokenType.EKLE, "Expected 'ekle' after list name and '.'")
            return ListExtendStatement(
                name.line,
                name.column,
                name.lexeme,
                self._expression_list("Expected at least one value after 'ekle'"),
            )
        raise self._error(self._peek(), "Expected '=' or '.ekle' after identifier")

    def _expression_list(self, missing_message: str) -> tuple[ExpressionNode, ...]:
        if self._check(TokenType.NEWLINE) or self._check(TokenType.EOF):
            raise self._error(self._peek(), missing_message)

        expressions = [self._expression()]
        while self._match(TokenType.COMMA):
            expressions.append(self._expression())
        return tuple(expressions)

    def _expression(self) -> ExpressionNode:
        if self._match(TokenType.NUMBER):
            token = self._previous()
            return NumberLiteral(token.line, token.column, token.literal)
        if self._match(TokenType.STRING):
            token = self._previous()
            return StringLiteral(token.line, token.column, token.literal)
        if self._match(TokenType.IDENTIFIER):
            token = self._previous()
            return Identifier(token.line, token.column, token.lexeme)
        if self._match(TokenType.VERI):
            token = self._previous()
            return InputExpression(token.line, token.column, self._expression())
        if self._match(TokenType.UZUNLUK):
            token = self._previous()
            return LengthExpression(token.line, token.column, self._expression())

        raise self._error(self._peek(), "Expected an expression")

    def _skip_newlines(self) -> None:
        while self._match(TokenType.NEWLINE):
            pass

    def _match(self, *token_types: TokenType) -> bool:
        if any(self._check(token_type) for token_type in token_types):
            self._advance()
            return True
        return False

    def _consume(self, token_type: TokenType, message: str) -> Token:
        if self._check(token_type):
            return self._advance()
        raise self._error(self._peek(), message)

    def _check(self, token_type: TokenType) -> bool:
        return self._peek().type is token_type

    def _advance(self) -> Token:
        if not self._check(TokenType.EOF):
            self.current += 1
        return self._previous()

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]

    @staticmethod
    def _error(token: Token, message: str) -> ParserError:
        if token.type is TokenType.EOF:
            return ParserError(f"{message}; found end of input", token)
        return ParserError(f"{message}; found {token.lexeme!r}", token)


def parse(tokens: Sequence[Token]) -> Program:
    """Parse a token sequence produced by the Vega lexer."""

    return Parser(tokens).parse()


__all__ = ["Parser", "ParserError", "parse"]
