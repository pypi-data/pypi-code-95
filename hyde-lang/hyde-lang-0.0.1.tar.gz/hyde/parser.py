from hyde.errors import BaseError
from hyde.token import TokenType
import hyde.expressions as Expressions
import hyde.statements as Statements


class ParseError(BaseError):
    pass


class Parser:

    STATEMENT_BOUNDARY_TOKENS = [
        TokenType.CLASS,
        TokenType.FUN,
        TokenType.VAR,
        TokenType.FOR,
        TokenType.IF,
        TokenType.WHILE,
        TokenType.PRINT,
        TokenType.RETURN
    ]

    def __init__(self, runtime, tokens):
        self.runtime = runtime
        self.tokens  = tokens
        
        self.current = 0

    def parse(self):
        statements = []

        while not self.is_at_end():
            statements.append(self.declaration())

        return statements

    # Grammar rules
    def block(self):
        statements = []
        
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())

        self.consume(TokenType.RIGHT_BRACE, "Expected '}' after block.")

        return statements

    def declaration(self):
        try:
            if self.match(TokenType.CLASS):
                return self.class_declaration()
            elif self.match(TokenType.FUN):
                return self.function("function")
            elif self.match(TokenType.VAR):
                return self.var_declaration()

            return self.statement()
        except ParseError as _ex:
            self.synchronize()

    def expression(self):
        return self.assignment()

    def function(self, kind):
        name = self.consume(TokenType.IDENTIFIER, f'Expected {kind} name.')

        self.consume(TokenType.LEFT_PAREN, f"Expected '(' after {kind} name.")

        parameters = []
        if not self.check(TokenType.RIGHT_PAREN):
            first_loop = True
            
            while first_loop or self.match(TokenType.COMMA):
                first_loop = False

                parameters.append(
                    self.consume(TokenType.IDENTIFIER, 'Expected parameter name')
                )

        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after parameters.")
        self.consume(TokenType.LEFT_BRACE, f"Expected '{{' before {kind} body.")

        body = self.block()

        return Statements.Function(name, parameters, body)

    def statement(self):
        if self.match(TokenType.FOR):
            return self.for_statement()
        elif self.match(TokenType.IF):
            return self.if_statement()
        elif self.match(TokenType.PRINT):
            return self.print_statement()
        elif self.match(TokenType.RETURN):
            return self.return_statement()
        elif self.match(TokenType.WHILE):
            return self.while_statement()
        elif self.match(TokenType.LEFT_BRACE):
            return Statements.Block(self.block())

        return self.expression_statement()

    def class_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, 'Expected class name.')
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before class body.")

        methods = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            methods.append(self.function('method'))

        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after class body.")

        return Statements.ClassDef(name, methods)

    def var_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, 'Expected variable name.')

        initializer = None

        if self.match(TokenType.EQUAL):
            initializer = self.expression()

        self.consume(TokenType.SEMICOLON, "Expected ';' after variable definition.")

        return Statements.Var(name, initializer)

    def for_statement(self):
        '''
        Parses for statements into a while statement
        '''
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'for'.")

        if self.match(TokenType.SEMICOLON):
            initializer = None
        elif self.match(TokenType.VAR):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()

        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()

        self.consume(TokenType.SEMICOLON, "Expected ';' after loop condition.")

        increment = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()

        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after for clauses.")

        body = self.statement()

        if increment is not None:
            body = Statements.Block([body, Statements.Expression(increment)])

        if condition is None:
            condition = Expressions.Literal(True)

        body = Statements.WhileStmt(condition, body)

        if initializer is not None:
            body = Statements.Block([initializer, body])

        return body
            
    def if_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after condition.")

        then_branch = self.statement()
        else_branch = None

        if self.match(TokenType.ELSE):
            else_branch = self.statement()

        return Statements.IfStmt(condition, then_branch, else_branch)

    def print_statement(self):
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after value.")

        return Statements.Print(value)

    def return_statement(self):
        keyword = self.previous()
        value = None
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()
    
        self.consume(TokenType.SEMICOLON, "Expected ';' after return value.")

        return Statements.ReturnStmt(keyword, value)

    def while_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expected '(' after 'while'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after condition.")
        body = self.statement()

        return Statements.WhileStmt(condition, body)

    def expression_statement(self):
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after value.")

        return Statements.Expression(value)

    def comparison(self):
        expr = self.term()

        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = Expressions.Binary(expr, operator, right)

        return expr

    def term(self):
        expr = self.factor()

        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Expressions.Binary(expr, operator, right)

        return expr

    def factor(self):
        expr = self.unary()

        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.factor()
            expr = Expressions.Binary(expr, operator, right)

        return expr

    def unary(self):
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()

            return Expressions.Unary(operator, right)

        return self.call()

    def primary(self):
        if self.match(TokenType.FALSE):
            return Expressions.Literal(False)
        elif self.match(TokenType.TRUE):
            return Expressions.Literal(True)
        elif self.match(TokenType.NIL):
            return Expressions.Literal(None)
        elif self.match(TokenType.NUMBER, TokenType.STRING):
            return Expressions.Literal(self.previous().literal)
        elif self.match(TokenType.THIS):
            return Expressions.This(self.previous())
        elif self.match(TokenType.IDENTIFIER):
            return Expressions.Variable(self.previous())
        elif self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression")

            return Expressions.Grouping(expr)

        self.error(self.peek(), 'Expected an expression.')

    def equality(self):
        expr = self.comparison()

        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Expressions.Binary(expr, operator, right)

        return expr

    def and_stmt(self):
        expr =  self.equality()

        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expr = Expressions.Logical(expr, operator, right)

        return expr

    def or_stmt(self):
        expr = self.and_stmt()

        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.and_stmt()
            expr = Expressions.Logical(expr, operator, right)

        return expr

    def assignment(self):
        expr = self.or_stmt()

        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expr, Expressions.Variable):
                name = expr.name
                
                return Expressions.Assign(name, value)
            elif isinstance(expr, Expressions.Get):
                return Expressions.Set(expr.object, expr.name, value)

            self.error(equals, 'Invalid assignment target.')

        return expr

    def call(self):
        expr = self.primary()

        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            elif self.match(TokenType.DOT):
                name = self.consume(TokenType.IDENTIFIER, "Expected property name after '.'.")
                expr = Expressions.Get(expr, name)
            else:
                break

        return expr

    def finish_call(self, callee):
        arguments = []

        if not self.check(TokenType.RIGHT_PAREN):
            arguments.append(self.expression())

            while self.match(TokenType.COMMA):
                arguments.append(self.expression())

        paren = self.consume(TokenType.RIGHT_PAREN, "Expected ')' after arguments.")

        return Expressions.Call(callee, paren, arguments)

    # Primitive operations for managing stack pointer
    def match(self, *token_types):
        for token_type in token_types:
            if self.check(token_type):
                self.advance()
                
                return True
        
        return False

    def check(self, token_type):
        if self.is_at_end():
            return False
        
        return self.peek().type == token_type

    def advance(self):
        if not self.is_at_end():
            self.current += 1

        return self.previous()

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]

    def consume(self, token_type, message):
        if self.check(token_type):
            return self.advance()

        self.error(self.peek(), message)

    def synchronize(self):
        self.advance()

        while not self.is_at_end():
            if self.previous() == TokenType.SEMICOLON:
                return

            if self.peek() in self.STATEMENT_BOUNDARY_TOKENS:
                return

            self.advance()

    def is_at_end(self):
        return self.peek().type == TokenType.EOF

    def error(self, token, message):
        '''
        Reports error to Hyde runtime and re-raises error
        '''
        error = ParseError(token, message)
        self.runtime.error(error)

        raise error
