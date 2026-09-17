"""Lexer for Vega the Language."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any


class TokenType(str, Enum):
    """Kinds of tokens currently used by Vega."""

    SAYISAL = "SAYISAL"
    DIZE = "DIZE"
    BOOL = "BOOL"
    DOGRU = "DOGRU"
    YANLIS = "YANLIS"
    YAZDIR = "YAZDIR"
    VERI = "VERI"
    UZUNLUK = "UZUNLUK"
    MUTLAK = "MUTLAK"
    LISTE = "LISTE"
    YENI = "YENI"
    EKLE = "EKLE"
    EGER = "EGER"
    IKINCIL = "IKINCIL"
    DEGILSE = "DEGILSE"
    BELIRLE = "BELIRLE"
    DENE = "DENE"
    YAKALA = "YAKALA"
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    STRING = "STRING"
    EQUAL = "EQUAL"
    GREATER = "GREATER"
    LESS = "LESS"
    MINUS = "MINUS"
    DOT = "DOT"
    COMMA = "COMMA"
    COLON = "COLON"
    SLASH = "SLASH"
    NEWLINE = "NEWLINE"
    EOF = "EOF"


KEYWORDS: dict[str, TokenType] = {
    "sayisal": TokenType.SAYISAL,
    "dize": TokenType.DIZE,
    "bool": TokenType.BOOL,
    "dogru": TokenType.DOGRU,
    "yanlis": TokenType.YANLIS,
    "yazdir": TokenType.YAZDIR,
    "veri": TokenType.VERI,
    "uzunluk": TokenType.UZUNLUK,
    "mutlak": TokenType.MUTLAK,
    "liste": TokenType.LISTE,
    "yeni": TokenType.YENI,
    "ekle": TokenType.EKLE,
    "eger": TokenType.EGER,
    "ikincil": TokenType.IKINCIL,
    "degilse": TokenType.DEGILSE,
    "belirle": TokenType.BELIRLE,
    "dene": TokenType.DENE,
    "yakala": TokenType.YAKALA,
}


@dataclass(frozen=True, slots=True)
class Token:
    """A token and its location in the source file (both are one-based)."""

    type: TokenType
    lexeme: str
    literal: Any
    line: int
    column: int


class LexerError(SyntaxError):
    """Raised when the input contains an invalid or incomplete token."""

    def __init__(self, message: str, line: int, column: int) -> None:
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"{message} at line {line}, column {column}")


class Lexer:
    """Turn Vega source text into a sequence of :class:`Token` objects."""

    def __init__(self, source: str) -> None:
        self.source = source
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1
        self.start_line = 1
        self.start_column = 1
        self.tokens: list[Token] = []

    def scan_tokens(self) -> list[Token]:
        """Scan the complete input and return tokens terminated by ``EOF``."""

        while not self._is_at_end():
            self.start = self.current
            self.start_line = self.line
            self.start_column = self.column
            self._scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line, self.column))
        return self.tokens

    tokenize = scan_tokens

    def _scan_token(self) -> None:
        char = self._advance()

        if char in " \t\f\v":
            return
        if char == "\r":
            # Treat CRLF as a single newline, but also support old-style CR.
            if self._peek() == "\n":
                self._advance()
            self._add_token(TokenType.NEWLINE)
            self.line += 1
            self.column = 1
            return
        if char == "\n":
            self._add_token(TokenType.NEWLINE)
            self.line += 1
            self.column = 1
            return
        if char == "#":
            self._comment()
            return
        if char == "=":
            self._add_token(TokenType.EQUAL)
            return
        if char == ">":
            self._add_token(TokenType.GREATER)
            return
        if char == "<":
            self._add_token(TokenType.LESS)
            return
        if char == "-":
            self._add_token(TokenType.MINUS)
            return
        if char == ".":
            self._add_token(TokenType.DOT)
            return
        if char == ",":
            self._add_token(TokenType.COMMA)
            return
        if char == ":":
            self._add_token(TokenType.COLON)
            return
        if char == "/":
            self._add_token(TokenType.SLASH)
            return
        if char in {'"', "“"}:
            self._string(char)
            return
        if char.isdecimal():
            self._number()
            return
        if self._is_identifier_start(char):
            self._identifier()
            return

        raise LexerError(
            f"Unexpected character {char!r}", self.start_line, self.start_column
        )

    def _comment(self) -> None:
        while self._peek() not in {"\n", "\r", "\0"}:
            self._advance()

    def _string(self, opening_quote: str) -> None:
        closing_quote = "”" if opening_quote == "“" else '"'
        value: list[str] = []

        while not self._is_at_end():
            char = self._advance()
            if char == closing_quote:
                self._add_token(TokenType.STRING, "".join(value))
                return
            if char in {"\n", "\r"}:
                raise LexerError(
                    "Unterminated string", self.start_line, self.start_column
                )
            if char == "\\":
                if self._is_at_end():
                    break
                escaped = self._advance()
                escapes = {
                    "n": "\n",
                    "r": "\r",
                    "t": "\t",
                    '"': '"',
                    "\\": "\\",
                    "“": "“",
                    "”": "”",
                }
                if escaped not in escapes:
                    raise LexerError(
                        f"Unknown escape sequence \\{escaped}",
                        self.line,
                        self.column - 2,
                    )
                value.append(escapes[escaped])
            else:
                value.append(char)

        raise LexerError("Unterminated string", self.start_line, self.start_column)

    def _number(self) -> None:
        while self._peek().isdecimal():
            self._advance()

        is_decimal = False
        if self._peek() == "." and self._peek_next().isdecimal():
            is_decimal = True
            self._advance()
            while self._peek().isdecimal():
                self._advance()

        lexeme = self.source[self.start : self.current]
        literal: int | float = float(lexeme) if is_decimal else int(lexeme)
        self._add_token(TokenType.NUMBER, literal)

    def _identifier(self) -> None:
        while self._is_identifier_part(self._peek()):
            self._advance()

        lexeme = self.source[self.start : self.current]
        self._add_token(KEYWORDS.get(lexeme, TokenType.IDENTIFIER))

    @staticmethod
    def _is_identifier_start(char: str) -> bool:
        return char == "_" or char.isalpha()

    @staticmethod
    def _is_identifier_part(char: str) -> bool:
        return char == "_" or char.isalpha() or char.isdecimal()

    def _is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def _advance(self) -> str:
        char = self.source[self.current]
        self.current += 1
        self.column += 1
        return char

    def _peek(self) -> str:
        if self._is_at_end():
            return "\0"
        return self.source[self.current]

    def _peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def _add_token(self, token_type: TokenType, literal: Any = None) -> None:
        self.tokens.append(
            Token(
                token_type,
                self.source[self.start : self.current],
                literal,
                self.start_line,
                self.start_column,
            )
        )


def tokenize(source: str) -> list[Token]:
    """Tokenize Vega source text."""

    return Lexer(source).scan_tokens()


def tokenize_file(path: str | Path) -> list[Token]:
    """Read and tokenize a UTF-8 encoded Vega source file."""

    return tokenize(Path(path).read_text(encoding="utf-8"))


__all__ = [
    "KEYWORDS",
    "Lexer",
    "LexerError",
    "Token",
    "TokenType",
    "tokenize",
    "tokenize_file",
]
