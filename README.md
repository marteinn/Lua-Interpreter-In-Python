# Lua to Python 2

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
- [ ] Not defined variables should return `nil`
- [ ] Handle global vs local variables in lua style
- [ ] Different types of loops


## References
- A lot of the work here is based on the book [Writing A Compiler In Go](https://compilerbook.com/)
- [My first take](https://github.com/marteinn/Lua-To-Python)
- [A Python Interpreter Written in Python](https://www.aosabook.org/en/500L/a-python-interpreter-written-in-python.html)
- [Let’s Build A Simple Interpreter. Part 7: Abstract Syntax Trees](https://ruslanspivak.com/lsbasi-part7/)
