# Visual Basic Language Parser

## Project Description
This project implements a parser for a subset of the Visual Basic programming language using Python.

It accepts Visual Basic source code as input, performs lexical analysis, generates tokens, checks syntax using a recursive-descent parser, and produces an Abstract Syntax Tree (AST).

## Objectives
- Accept Visual Basic source code from the user.
- Identify keywords, identifiers, operators, numbers and strings.
- Validate source code using grammar rules.
- Generate an Abstract Syntax Tree.
- Detect and report lexical and syntax errors.

## Technologies Used
- **Programming Language:** Python 3
- **Regular Expressions:** Python `re` module
- **Dataclasses:** Python `dataclasses` module
- **Parsing Technique:** Recursive-Descent Parsing

## Supported Language Constructs
- Variable declarations using `Dim`
- Integer, String and Boolean datatypes
- Assignment statements
- Arithmetic expressions
- Relational operators
- Parenthesized expressions
- If-Then and If-Then-Else statements
- Single-line comments

## Grammar Rules

```text
Program       → Statement*

Statement     → Declaration
              | Assignment
              | IfStatement

Declaration   → DIM ID AS TYPE

Assignment    → ID = Expression

IfStatement   → IF Expression THEN
                Statement*
                (ELSE Statement*)?
                END IF

Expression    → Comparison

Comparison    → Arithmetic
              | Arithmetic RelOp Arithmetic

Arithmetic    → Term (("+" | "-") Term)*

Term          → Factor (("*" | "/") Factor)*

Factor        → NUMBER
              | STRING
              | BOOLEAN
              | ID
              | "(" Expression ")"

RelOp         → ">" | "<" | ">=" | "<=" | "=" | "<>"
```

This is a simplified context-free grammar designed for the supported subset of Visual Basic.

## How to Run

1. Install Python 3.
2. Clone or download this repository.
3. Open the project folder in a terminal.
4. Run the following command:

```bash
python vbparser.py
```

5. Enter Visual Basic source code.
6. Type `END` on a separate line to finish input.

## Sample Input

```vb
Dim x As Integer
Dim y As Integer
x = 10
y = x + 20
```

## Expected Output

The program displays:
- Generated tokens
- Parsing success or error message
- Abstract Syntax Tree (AST)

## Project Structure

```text
Visual-Basic-Parser/
│
├── vbparser.py
├── README.md
├── valid_input.png
└── invalid_input.png
```

## Limitations
- Supports only a subset of Visual Basic syntax.
- Does not perform semantic analysis or type checking.

## Future Enhancements
- Support for loops and functions.
- Semantic analysis and symbol table implementation.

## Reference
Microsoft Visual Basic Language Reference:
https://learn.microsoft.com/en-us/dotnet/visual-basic/language-reference/

