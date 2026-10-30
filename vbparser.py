
import re
from dataclasses import dataclass


# 1. TOKEN CLASS

@dataclass
class Token:
    type: str
    value: str
    line: int


# 2. LEXICAL ANALYZER

class Lexer:
    keywords = {
        "DIM": "DIM",
        "AS": "AS",
        "INTEGER": "TYPE",
        "STRING": "TYPE",
        "BOOLEAN": "TYPE",
        "IF": "IF",
        "THEN": "THEN",
        "ELSE": "ELSE",
        "END": "END",
        "TRUE": "BOOLEAN",
        "FALSE": "BOOLEAN",
    }

    token_specification = [
        ("COMMENT", r"'[^\n]*"),
        ("NUMBER", r"\d+"),
        ("STRING", r'"[^"\n]*"'),
        ("ID", r"[A-Za-z_][A-Za-z0-9_]*"),
        ("OP", r"<>|>=|<=|[+\-*/=><]"),
        ("LPAREN", r"\("),
        ("RPAREN", r"\)"),
        ("NEWLINE", r"\n"),
        ("SKIP", r"[ \t\r]+"),
        ("MISMATCH", r"."),
    ]

    def __init__(self, text):
        self.text = text

    def tokenize(self):
        tokens = []
        line = 1

        pattern = "|".join(
            f"(?P<{name}>{regex})"
            for name, regex in self.token_specification
        )

        for match in re.finditer(pattern, self.text):
            kind = match.lastgroup
            value = match.group()

            if kind == "NEWLINE":
                tokens.append(Token("NEWLINE", value, line))
                line += 1

            elif kind in ("SKIP", "COMMENT"):
                continue

            elif kind == "ID":
                token_type = self.keywords.get(
                    value.upper(), "ID"
                )
                tokens.append(Token(token_type, value, line))

            elif kind == "NUMBER":
                tokens.append(Token("NUMBER", value, line))

            elif kind == "STRING":
                tokens.append(Token("STRING", value, line))

            elif kind == "OP":
                tokens.append(Token(value, value, line))

            elif kind == "LPAREN":
                tokens.append(Token("(", value, line))

            elif kind == "RPAREN":
                tokens.append(Token(")", value, line))

            elif kind == "MISMATCH":
                raise SyntaxError(
                    f"Unexpected character {value!r} "
                    f"at line {line}"
                )

        tokens.append(Token("EOF", "", line))
        return tokens


# 3. ABSTRACT SYNTAX TREE CLASSES

@dataclass
class Program:
    statements: list


@dataclass
class Declaration:
    name: str
    datatype: str


@dataclass
class Assignment:
    name: str
    expression: object


@dataclass
class IfStatement:
    condition: object
    then_body: list
    else_body: list


@dataclass
class BinaryOp:
    left: object
    operator: str
    right: object


@dataclass
class Number:
    value: int


@dataclass
class String:
    value: str


@dataclass
class Boolean:
    value: bool


@dataclass
class Variable:
    name: str


# 4. SYNTAX ANALYZER / PARSER

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        return self.tokens[self.pos]

    def match(self, token_type):
        if self.current().type == token_type:
            token = self.current()
            self.pos += 1
            return token
        return None

    def expect(self, token_type):
        token = self.match(token_type)

        if token is None:
            current = self.current()
            raise SyntaxError(
                f"Expected {token_type}, got "
                f"{current.type} at line {current.line}"
            )

        return token

    def skip_newlines(self):
        while self.match("NEWLINE"):
            pass

    def parse(self):
        statements = []
        self.skip_newlines()

        while self.current().type != "EOF":
            statements.append(self.statement())
            self.skip_newlines()

        return Program(statements)

    def statement(self):
        token_type = self.current().type

        if token_type == "DIM":
            return self.declaration()

        if token_type == "IF":
            return self.if_statement()

        if token_type == "ID":
            return self.assignment()

        raise SyntaxError(
            f"Invalid statement at line {self.current().line}"
        )

    def declaration(self):
        self.expect("DIM")
        name = self.expect("ID").value
        self.expect("AS")
        datatype = self.expect("TYPE").value

        return Declaration(name, datatype)

    def assignment(self):
        name = self.expect("ID").value
        self.expect("=")
        expression = self.expression()

        return Assignment(name, expression)

    def if_statement(self):
        self.expect("IF")
        condition = self.expression()
        self.expect("THEN")
        self.skip_newlines()

        then_body = []

        while self.current().type not in ("ELSE", "END", "EOF"):
            then_body.append(self.statement())
            self.skip_newlines()

        else_body = []

        if self.match("ELSE"):
            self.skip_newlines()

            while self.current().type not in ("END", "EOF"):
                else_body.append(self.statement())
                self.skip_newlines()

        self.expect("END")
        self.expect("IF")

        return IfStatement(condition, then_body, else_body)

    def expression(self):
        return self.comparison()

    def comparison(self):
        node = self.arithmetic()

        if self.current().type in (">", "<", ">=", "<=", "=", "<>"):
            operator = self.current().value
            self.pos += 1
            right = self.arithmetic()
            node = BinaryOp(node, operator, right)

        return node

    def arithmetic(self):
        node = self.term()

        while self.current().type in ("+", "-"):
            operator = self.current().value
            self.pos += 1
            right = self.term()
            node = BinaryOp(node, operator, right)

        return node

    def term(self):
        node = self.factor()

        while self.current().type in ("*", "/"):
            operator = self.current().value
            self.pos += 1
            right = self.factor()
            node = BinaryOp(node, operator, right)

        return node

    def factor(self):
        token = self.current()

        if token.type == "NUMBER":
            self.pos += 1
            return Number(int(token.value))

        if token.type == "STRING":
            self.pos += 1
            return String(token.value[1:-1])

        if token.type == "BOOLEAN":
            self.pos += 1
            return Boolean(token.value.upper() == "TRUE")

        if token.type == "ID":
            self.pos += 1
            return Variable(token.value)

        if self.match("("):
            node = self.expression()
            self.expect(")")
            return node

        raise SyntaxError(
            f"Invalid expression at line {token.line}"
        )


# 5. CONVERT AST INTO A TREE STRUCTURE

def ast_to_tree(node):
    if isinstance(node, Program):
        return ("Program", [ast_to_tree(s) for s in node.statements])

    if isinstance(node, Declaration):
        return (
            f"Declaration: {node.name} As {node.datatype}", []
        )

    if isinstance(node, Assignment):
        return (
            f"Assignment: {node.name}",
            [ast_to_tree(node.expression)]
        )

    if isinstance(node, BinaryOp):
        return (
            f"BinaryOp: {node.operator}",
            [ast_to_tree(node.left), ast_to_tree(node.right)]
        )

    if isinstance(node, Number):
        return (f"Number: {node.value}", [])

    if isinstance(node, String):
        return (f"String: {node.value}", [])

    if isinstance(node, Boolean):
        return (f"Boolean: {node.value}", [])

    if isinstance(node, Variable):
        return (f"Variable: {node.name}", [])

    if isinstance(node, IfStatement):
        children = [
            ("Condition", [ast_to_tree(node.condition)]),
            ("Then", [ast_to_tree(s) for s in node.then_body])
        ]

        if node.else_body:
            children.append(
                ("Else", [ast_to_tree(s) for s in node.else_body])
            )

        return ("IfStatement", children)

    if isinstance(node, tuple):
        return node

    return ("Unknown", [])


def print_tree(tree, prefix="", is_last=True, root=True):
    label, children = tree

    if root:
        print(label)
    else:
        branch = "└── " if is_last else "├── "
        print(prefix + branch + label)

    child_prefix = prefix if root else (
        prefix + ("    " if is_last else "│   ")
    )

    for i, child in enumerate(children):
        print_tree(
            child,
            child_prefix,
            i == len(children) - 1,
            False
        )


def print_ast(node):
    print_tree(ast_to_tree(node))


# 6. MAIN PROGRAM

if __name__ == "__main__":
    print("Enter Visual Basic source code.")
    print("Type END on a separate line to finish input:\n")

    source_lines = []

    while True:
        line = input()

        if line.strip().upper() == "END":
            break

        source_lines.append(line)

    source_code = "\n".join(source_lines)

    try:
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()

        print("\nTokens:")
        for token in tokens:
            if token.type not in ("EOF", "NEWLINE"):
                print(f"{token.type}: {token.value}")

        parser = Parser(tokens)
        ast = parser.parse()

        print("\nParsing successful!")
        print("\nAbstract Syntax Tree:\n")
        print_ast(ast)

    except SyntaxError as error:
        print("\nParsing failed:", error)
