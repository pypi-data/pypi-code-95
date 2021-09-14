from hyde.errors import BaseError
from hyde.token import Token, TokenType

class TokenizerError(BaseError):
    pass


class Tokenizer:

    SINGLE_CHARACTER_TOKENS = {
        '(': TokenType.LEFT_PAREN,
        ')': TokenType.RIGHT_PAREN,
        '{': TokenType.LEFT_BRACE,
        '}': TokenType.RIGHT_BRACE,
        ',': TokenType.COMMA,
        '.': TokenType.DOT,
        '-': TokenType.MINUS,
        '+': TokenType.PLUS,
        ';': TokenType.SEMICOLON,
        '/': TokenType.SLASH,
        '*': TokenType.STAR
    }

    DOUBLE_CHARACTER_TOKENS = {
              # Single (!)       # Double (!=)
        '!': (TokenType.BANG,    TokenType.BANG_EQUAL),
        '=': (TokenType.EQUAL,   TokenType.EQUAL_EQUAL),
        '<': (TokenType.LESS,    TokenType.LESS_EQUAL),
        '>': (TokenType.GREATER, TokenType.GREATER_EQUAL)
    }

    COMMENT_TOKENS = {
        '#': TokenType.POUND
    }

    SKIPPABLE_TOKENS = [' ', '\r', '\t', '\n']

    RESERVED_TOKENS = {
        'and':    TokenType.AND,
        'class':  TokenType.CLASS,
        'else':   TokenType.ELSE,
        'false':  TokenType.FALSE,
        'fun':    TokenType.FUN,
        'for':    TokenType.FOR,
        'if':     TokenType.IF,
        'nil':    TokenType.NIL,
        'or':     TokenType.OR,
        'print':  TokenType.PRINT,
        'return': TokenType.RETURN,
        'super':  TokenType.SUPER,
        'this':   TokenType.THIS,
        'true':   TokenType.TRUE,
        'var':    TokenType.VAR,
        'while':  TokenType.WHILE
    }

    def __init__(self, runtime, source):
        self.runtime = runtime
        self.source  = source
        self.tokens  = []

        self.start   = 0
        self.current = 0
        self.line    = 1

    def scan_tokens(self):
        while not self.is_at_end():
            self.start = self.current
            self.scan_single_token()

        self.tokens.append(Token(TokenType.EOF, '', None, self.line))

        return self.tokens

    def is_at_end(self):
        return self.current >= len(self.source)

    def scan_single_token(self):
        c = self.advance()

        if c in self.SINGLE_CHARACTER_TOKENS:
            self.add_token(self.SINGLE_CHARACTER_TOKENS[c])
        elif c in self.DOUBLE_CHARACTER_TOKENS:
            if self.match('='):
                self.add_token(self.DOUBLE_CHARACTER_TOKENS[c][1])
            else:
                self.add_token(self.DOUBLE_CHARACTER_TOKENS[c][0])
        elif c in self.COMMENT_TOKENS:
            while self.peek() != '\n' and not self.is_at_end():
                self.advance()
        elif c in self.SKIPPABLE_TOKENS:
            if c == '\n':
                self.line += 1
        elif c == '"':
            self.string()
        else:
            if c.isdigit():
                self.number()
            elif c.isidentifier():
                self.identifier()
            else:
                self.error(f'Unexpected character {c}.')

    def add_token(self, token_type, literal=None):
        text = self.source[self.start:self.current]
        token = Token(token_type, text, literal, self.line)

        self.tokens.append(token)

    def advance(self):
        character = self.source[self.current]
        self.current += 1

        return character

    def match(self, expected):
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False

        self.current += 1

        return True

    def peek(self):
        if self.is_at_end():
            return '\0'

        return self.source[self.current]

    def peek_two(self):
        if self.current + 1 >= len(self.source):
            return '\0'

        return self.source[self.current + 1]

    def string(self):
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == '\n':
                self.line += 1
            self.advance()

        if self.is_at_end():
            self.error('Unterminated string.')

        self.advance()

        value = self.source[self.start + 1:self.current - 1] # Trims the surrounding quotes
        self.add_token(TokenType.STRING, literal=value)

    def number(self):
        while self.peek().isdigit():
            self.advance()

        if self.peek() == '.' and self.peek_two().isdigit(): # Consume the .
            self.advance()

            while self.peek().isdigit():
                self.advance()

        value = float(self.source[self.start:self.current])
        self.add_token(TokenType.NUMBER, literal=value)

    def identifier(self):
        while self.peek().isidentifier():
            self.advance()

        text = self.source[self.start:self.current]
        
        if text in self.RESERVED_TOKENS:
            self.add_token(self.RESERVED_TOKENS[text])
        else:
            self.add_token(TokenType.IDENTIFIER)

    def error(self, message):
        # TODO: Hacky, need to build up a fake error in order to display the line and message correctly.
        ex = TokenizerError(Token(None, None, None, self.line), message)
        self.runtime.error(ex)