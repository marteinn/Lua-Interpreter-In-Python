from io import StringIO

import click

from luatopy.lexer import Lexer
from luatopy.parser import Parser
from luatopy.obj import Environment
from luatopy import evaluator


@click.command()
@click.option('--tokens', is_flag=True, help='Show lexer tokens')
@click.option('--ast-code', is_flag=True, help='Show AST code')
def run(tokens, ast_code):
    print("luatopy repl")
    if tokens:
        print("* Config: Show lexer tokens")

    if ast_code:
        print("* Config: Show ast code")

    env = Environment()
    while True:
        source = input(">>> ")
        lexer = Lexer(StringIO(source))
        if tokens:
            print(list(lexer.tokens()))

        parser = Parser(lexer)
        program = parser.parse_program()

        if parser.errors:
            for err in parser.errors:
                print("ERROR: {0}".format(err))

        if ast_code:
            print(program.to_code())

        evaluated = evaluator.evaluate(program, env)
        if evaluated:
            print(evaluated.inspect())


if __name__ == '__main__':
    run()
