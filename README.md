# Lua interpreter in Python

This is my second take on writing a Lua-To-Python compiler, it includes:

- [x] Lexer
- [x] Parser
- [x] A internal AST representation
- [x] Repl
- [x] Interpeter


## Running repl

- `python repl.py`


## TODO
- [x] Introduce `;` as a separator
- [x] Named functions
- [x] Not defined variables should return `nil`
- [x] Modulo operator
- [x] `and` operator
- [x] `or` operator
- [ ] `elseif` statement
- [x] Variables with numbers in name
- [ ] Iterator for Table using `pairs`/`ipairs`
- [ ] `_G` for globals access
- [ ] `for` loop
- [ ] `while` loop
- [ ] `repeat` loop
- [ ] Short circuit / tenary operator
- [ ] Dot property syntax in Table for string keys
- [ ] Numbers beginning with `.` (Ex `.5`)
- [ ] Handle global vs local variables in lua style
- [ ] Function calls with single params should not require parens
- [ ] Metatable support for tables


## Supports
- Single and multiline comments
- Variable assignments
- Numbers
- Strings
- Tables
- Addition, multiplication and division
- If statements
- Comparison operators (`==`, `>=`, `>`, `<`, `<≠`, `~=`)
- String concat `..`
- `return`
- `function` declarations (both named and anymous with closures)
- `not` logical operator
- Negative values
- Table indexing
- Table count with `#`
- Non existing identifiers return nil
- Modulo operator


## References
- A lot of the work here is based on the book [Writing A Compiler In Go](https://compilerbook.com/)
- [My first take](https://github.com/marteinn/Lua-To-Python)
- [A Python Interpreter Written in Python](https://www.aosabook.org/en/500L/a-python-interpreter-written-in-python.html)
- [Let’s Build A Simple Interpreter. Part 7: Abstract Syntax Trees](https://ruslanspivak.com/lsbasi-part7/)
