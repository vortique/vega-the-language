"""Recursive-descent parser for Vega the Language."""

from __future__ import annotations

from collections.abc import Sequence

from src.ast_nodes import (
    AbsoluteExpression,
    Assignment,
    BinaryExpression,
    BooleanDeclaration,
    BooleanLiteral,
    ConditionalBranch,
    ConditionalStatement,
    ExpressionNode,
    ExpressionStatement,
    FunctionCallStatement,
    FunctionDeclaration,
    FunctionParameter,
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
    StatementNode,
    StringDeclaration,
    StringLiteral,
    TryCatchStatement,
)
from src.lexer import Token, TokenType


DECLARATION_TYPES = {
    TokenType.SAYISAL,
    TokenType.DIZE,
    TokenType.BOOL,
    TokenType.LISTE,
}


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
            if self._peek().column != 1:
                raise self._error(self._peek(), "Unexpected indentation")
            statements.append(self._statement())

        return Program(tuple(statements))

    def _statement(self) -> StatementNode:
        if self._match(TokenType.SAYISAL):
            return self._numeric_declaration(self._previous())
        if self._match(TokenType.DIZE):
            return self._string_declaration(self._previous())
        if self._match(TokenType.BOOL):
            return self._boolean_declaration(self._previous())
        if self._match(TokenType.LISTE):
            return self._list_declaration(self._previous())
        if self._match(TokenType.YAZDIR):
            keyword = self._previous()
            statement = PrintStatement(
                keyword.line,
                keyword.column,
                self._call_argument("'yazdir'"),
            )
            self._end_statement()
            return statement
        if self._match(TokenType.EGER):
            return self._conditional_statement(self._previous())
        if self._match(TokenType.BELIRLE):
            return self._function_declaration(self._previous())
        if self._match(TokenType.DENE):
            return self._try_catch_statement(self._previous())
        if any(
            self._check(token_type)
            for token_type in (
                TokenType.UZUNLUK,
                TokenType.MUTLAK,
                TokenType.VERI,
                TokenType.ARALIK,
            )
        ):
            token = self._peek()
            statement = ExpressionStatement(
                token.line, token.column, self._expression()
            )
            self._end_statement()
            return statement
        if self._match(TokenType.IDENTIFIER):
            return self._identifier_statement(self._previous())

        raise self._error(self._peek(), "Expected a statement")

    def _numeric_declaration(self, keyword: Token) -> NumericDeclaration:
        name = self._consume(TokenType.IDENTIFIER, "Expected a variable name")
        self._consume(TokenType.EQUAL, "Expected '=' after variable name")
        statement = NumericDeclaration(
            keyword.line, keyword.column, name.lexeme, self._expression()
        )
        self._end_statement()
        return statement

    def _string_declaration(self, keyword: Token) -> StringDeclaration:
        name = self._consume(TokenType.IDENTIFIER, "Expected a variable name")
        self._consume(TokenType.EQUAL, "Expected '=' after variable name")
        statement = StringDeclaration(
            keyword.line, keyword.column, name.lexeme, self._expression()
        )
        self._end_statement()
        return statement

    def _boolean_declaration(self, keyword: Token) -> BooleanDeclaration:
        name = self._consume(TokenType.IDENTIFIER, "Expected a variable name")
        self._consume(TokenType.EQUAL, "Expected '=' after variable name")
        statement = BooleanDeclaration(
            keyword.line, keyword.column, name.lexeme, self._expression()
        )
        self._end_statement()
        return statement

    def _list_declaration(self, keyword: Token) -> ListDeclaration:
        name = self._consume(TokenType.IDENTIFIER, "Expected a list name")
        self._consume(TokenType.EQUAL, "Expected '=' after list name")
        statement = ListDeclaration(
            keyword.line,
            keyword.column,
            name.lexeme,
            self._expression(),
        )
        self._end_statement()
        return statement

    def _identifier_statement(self, name: Token) -> StatementNode:
        if self._match(TokenType.EQUAL):
            statement: StatementNode = Assignment(
                name.line, name.column, name.lexeme, self._expression()
            )
        elif self._match(TokenType.DOT):
            self._consume(TokenType.EKLE, "Expected 'ekle' after list name and '.'")
            delimited = self._match(TokenType.SLASH)
            statement = ListExtendStatement(
                name.line,
                name.column,
                name.lexeme,
                self._expression_list("Expected at least one value after 'ekle'"),
            )
            if delimited:
                self._consume(TokenType.SLASH, "Expected '/' after values")
        elif self._match(TokenType.ARTIR):
            statement = IncrementStatement(
                name.line, name.column, name.lexeme, 1
            )
        elif self._match(TokenType.AZALT):
            statement = IncrementStatement(
                name.line, name.column, name.lexeme, -1
            )
        elif self._match(TokenType.SLASH):
            arguments: tuple[ExpressionNode, ...] = ()
            if not self._check(TokenType.SLASH):
                arguments = self._expression_list("Expected a function argument")
            self._consume(TokenType.SLASH, "Expected '/' after function arguments")
            statement = FunctionCallStatement(
                name.line, name.column, name.lexeme, arguments
            )
        else:
            arguments = ()
            if not self._check(TokenType.NEWLINE) and not self._check(TokenType.EOF):
                arguments = self._expression_list("Expected a function argument")
            statement = FunctionCallStatement(
                name.line, name.column, name.lexeme, arguments
            )

        self._end_statement()
        return statement

    def _conditional_statement(self, keyword: Token) -> ConditionalStatement:
        branches = [self._conditional_branch(keyword)]

        while self._check_at_column(TokenType.IKINCIL, keyword.column):
            branch_keyword = self._advance()
            branches.append(self._conditional_branch(branch_keyword))

        else_body = None
        if self._check_at_column(TokenType.DEGILSE, keyword.column):
            self._advance()
            self._consume(TokenType.COLON, "Expected ':' after 'degilse'")
            else_body = self._indented_block(
                keyword.column, "Expected an indented block after 'degilse'"
            )

        return ConditionalStatement(
            keyword.line,
            keyword.column,
            tuple(branches),
            else_body,
        )

    def _conditional_branch(self, keyword: Token) -> ConditionalBranch:
        condition = self._expression()
        self._match(TokenType.COLON)
        body = self._indented_block(
            keyword.column,
            f"Expected an indented block after '{keyword.lexeme}'",
        )
        return ConditionalBranch(
            keyword.line, keyword.column, condition, body
        )

    def _function_declaration(self, keyword: Token) -> FunctionDeclaration:
        name = self._consume(TokenType.IDENTIFIER, "Expected a function name")
        self._consume(TokenType.SLASH, "Expected '/' after function name")
        parameters: list[FunctionParameter] = []

        if not self._check(TokenType.SLASH):
            while True:
                type_token = self._consume_declaration_type()
                parameter_name = self._consume(
                    TokenType.IDENTIFIER, "Expected a parameter name"
                )
                parameters.append(
                    FunctionParameter(
                        type_token.line,
                        type_token.column,
                        type_token.lexeme,
                        parameter_name.lexeme,
                    )
                )
                if not self._match(TokenType.COMMA):
                    break

        self._consume(TokenType.SLASH, "Expected '/' after function parameters")
        self._match(TokenType.COLON)
        body = self._indented_block(
            keyword.column, "Expected an indented function body"
        )
        return FunctionDeclaration(
            keyword.line,
            keyword.column,
            name.lexeme,
            tuple(parameters),
            body,
        )

    def _try_catch_statement(self, keyword: Token) -> TryCatchStatement:
        self._consume(TokenType.COLON, "Expected ':' after 'dene'")
        try_body = self._indented_block(
            keyword.column, "Expected an indented block after 'dene'"
        )

        if not self._check_at_column(TokenType.YAKALA, keyword.column):
            raise self._error(self._peek(), "Expected 'yakala' after 'dene' block")
        self._advance()
        self._consume(TokenType.COLON, "Expected ':' after 'yakala'")
        catch_body = self._indented_block(
            keyword.column, "Expected an indented block after 'yakala'"
        )
        return TryCatchStatement(
            keyword.line, keyword.column, try_body, catch_body
        )

    def _indented_block(
        self, parent_column: int, missing_message: str
    ) -> tuple[StatementNode, ...]:
        self._consume(TokenType.NEWLINE, "Expected a newline before block")
        self._skip_newlines()

        if self._check(TokenType.EOF) or self._peek().column <= parent_column:
            raise self._error(self._peek(), missing_message)

        indentation = self._peek().column
        statements: list[StatementNode] = []
        while not self._check(TokenType.EOF):
            if self._peek().column < indentation:
                break
            if self._peek().column > indentation:
                raise self._error(self._peek(), "Unexpected indentation")
            statements.append(self._statement())

        return tuple(statements)

    def _expression_list(self, missing_message: str) -> tuple[ExpressionNode, ...]:
        if self._check(TokenType.NEWLINE) or self._check(TokenType.EOF):
            raise self._error(self._peek(), missing_message)

        expressions = [self._expression()]
        while self._match(TokenType.COMMA):
            expressions.append(self._expression())
        return tuple(expressions)

    def _expression(self) -> ExpressionNode:
        return self._comparison()

    def _comparison(self) -> ExpressionNode:
        expression = self._term()

        while self._match(TokenType.GREATER, TokenType.LESS):
            operator = self._previous()
            expression = BinaryExpression(
                operator.line,
                operator.column,
                expression,
                operator.lexeme,
                self._term(),
            )

        return expression

    def _term(self) -> ExpressionNode:
        expression = self._factor()

        while self._match(TokenType.PLUS, TokenType.MINUS):
            operator = self._previous()
            expression = BinaryExpression(
                operator.line,
                operator.column,
                expression,
                operator.lexeme,
                self._factor(),
            )

        return expression

    def _factor(self) -> ExpressionNode:
        expression = self._unary()

        while self._check(TokenType.STAR) or self._slash_starts_division():
            operator = self._advance()
            expression = BinaryExpression(
                operator.line,
                operator.column,
                expression,
                operator.lexeme,
                self._unary(),
            )

        return expression

    def _unary(self) -> ExpressionNode:
        if self._match(TokenType.MINUS):
            token = self._previous()
            return NegativeExpression(token.line, token.column, self._unary())
        if self._match(TokenType.MUTLAK):
            token = self._previous()
            return AbsoluteExpression(
                token.line, token.column, self._call_argument("'mutlak'", unary=True)
            )
        if self._match(TokenType.VERI):
            token = self._previous()
            return InputExpression(
                token.line, token.column, self._call_argument("'veri'", unary=True)
            )
        if self._match(TokenType.UZUNLUK):
            token = self._previous()
            return LengthExpression(
                token.line, token.column, self._call_argument("'uzunluk'", unary=True)
            )
        if self._match(TokenType.ARALIK):
            token = self._previous()
            delimited = self._match(TokenType.SLASH)
            minimum = self._expression()
            self._consume(TokenType.COMMA, "Expected ',' between range bounds")
            maximum = self._expression()
            if delimited:
                self._consume(TokenType.SLASH, "Expected '/' after range bounds")
            return RangeExpression(token.line, token.column, minimum, maximum)
        return self._primary()

    def _primary(self) -> ExpressionNode:
        if self._match(TokenType.NUMBER):
            token = self._previous()
            return NumberLiteral(token.line, token.column, token.literal)
        if self._match(TokenType.STRING):
            token = self._previous()
            return StringLiteral(token.line, token.column, token.literal)
        if self._match(TokenType.DOGRU):
            token = self._previous()
            return BooleanLiteral(token.line, token.column, True)
        if self._match(TokenType.YANLIS):
            token = self._previous()
            return BooleanLiteral(token.line, token.column, False)
        if self._match(TokenType.IDENTIFIER):
            token = self._previous()
            return Identifier(token.line, token.column, token.lexeme)
        if self._match(TokenType.LISTE):
            return self._list_literal(self._previous())

        raise self._error(self._peek(), "Expected an expression")

    def _list_literal(self, keyword: Token) -> ListLiteral:
        self._consume(TokenType.DOT, "Expected '.' after 'liste'")
        self._consume(TokenType.YENI, "Expected 'yeni' after 'liste.'")
        delimited = self._match(TokenType.SLASH)
        elements = self._expression_list("Expected at least one list element")
        if delimited:
            self._consume(TokenType.SLASH, "Expected '/' after list elements")
        return ListLiteral(keyword.line, keyword.column, elements)

    def _call_argument(self, function_name: str, unary: bool = False) -> ExpressionNode:
        delimited = self._match(TokenType.SLASH)
        argument = self._expression() if delimited or not unary else self._unary()
        if delimited:
            self._consume(TokenType.SLASH, f"Expected '/' after {function_name} argument")
        return argument

    def _slash_starts_division(self) -> bool:
        if not self._check(TokenType.SLASH):
            return False
        return self._peek_next().type in {
            TokenType.MINUS,
            TokenType.MUTLAK,
            TokenType.VERI,
            TokenType.UZUNLUK,
            TokenType.ARALIK,
            TokenType.NUMBER,
            TokenType.STRING,
            TokenType.DOGRU,
            TokenType.YANLIS,
            TokenType.IDENTIFIER,
            TokenType.LISTE,
        }

    def _consume_declaration_type(self) -> Token:
        if self._peek().type in DECLARATION_TYPES:
            return self._advance()
        raise self._error(self._peek(), "Expected a parameter type")

    def _end_statement(self) -> None:
        if self._match(TokenType.NEWLINE):
            self._skip_newlines()
            return
        if self._check(TokenType.EOF):
            return
        raise self._error(self._peek(), "Expected a newline after statement")

    def _skip_newlines(self) -> None:
        while self._match(TokenType.NEWLINE):
            pass

    def _check_at_column(self, token_type: TokenType, column: int) -> bool:
        return self._check(token_type) and self._peek().column == column

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

    def _peek_next(self) -> Token:
        if self.current + 1 >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.current + 1]

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
