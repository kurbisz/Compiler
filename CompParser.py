import sly
from sly.lex import *
from sly.yacc import *

from CompLexer import CalcLexer
from CompManager import CompManager
from CompUtils import *


class CalcParser(sly.Parser):

    tokens = CalcLexer.tokens
    
    def __init__(self) -> None:
        super().__init__()
        self.manager = CompManager()


    @_('procedures main')
    def program_all(self, p):
        self.is_comm = True
        return 0
    

    @_('')
    def procedures(self, p):
        pass
    
    @_('procedures PROCEDURE proc_head IS VAR proc_declarations BEGIN commands END')
    def procedures(self, p):
        pass
    
    @_('procedures PROCEDURE proc_head IS BEGIN commands END')
    def procedures(self, p):
        pass


    @_('PROGRAM IS VAR declarations BEGIN commands END')
    def main(self, p):
        pass

    @_('PROGRAM IS BEGIN commands END')
    def main(self, p):
        pass


    @_('commands command')
    def commands(self, p):
        pass

    @_('command')
    def commands(self, p):
        pass


    @_('IDENTIFIER ASSIGN expression SEMICOLON')
    def command(self, p):
        self.manager.store(p.IDENTIFIER)

    @_('IF condition THEN commands ELSE commands ENDIF')
    def command(self, p):
        pass

    @_('IF condition THEN commands ENDIF')
    def command(self, p):
        pass

    @_('WHILE condition DO commands ENDWHILE')
    def command(self, p):
        pass

    @_('REPEAT commands UNTIL condition SEMICOLON')
    def command(self, p):
        pass

    @_('proc_head SEMICOLON')
    def command(self, p):
        pass

    @_('READ IDENTIFIER SEMICOLON')
    def command(self, p):
        self.manager.read(p.IDENTIFIER)

    @_('WRITE value SEMICOLON')
    def command(self, p):
        if is_int(p.value):
            self.manager.write_value(p.value)
        else:
            self.manager.write(p.value)


    @_('IDENTIFIER L_BRACKET declarations R_BRACKET')
    def proc_head(self, p):
        pass


    @_('proc_declarations COMMA IDENTIFIER')
    def proc_declarations(self, p):
        pass

    @_('IDENTIFIER')
    def proc_declarations(self, p):
        pass


    @_('declarations COMMA IDENTIFIER')
    def declarations(self, p):
        self.manager.add_declaration(p.IDENTIFIER)

    @_('IDENTIFIER')
    def declarations(self, p):
        self.manager.add_declaration(p.IDENTIFIER)


    @_('value')
    def expression(self, p):
        if is_int(p.value):
            self.manager.set(p.value)
        else:
            self.manager.load(p.value)

    @_('value ADD value')
    def expression(self, p):
        vars = are_variables(p.value0, p.value1)
        if vars == -1:
            self.manager.set(p.value0 + p.value1)
        elif vars == 0:
            self.manager.addVarToVal(p.value0, p.value1)
        elif vars == 1:
            self.manager.addVarToVal(p.value1, p.value0)
        else:
            self.manager.addVarToVar(p.value0, p.value1)

    @_('value SUB value')
    def expression(self, p):
        pass

    @_('value MUL value')
    def expression(self, p):
        pass

    @_('value DIV value')
    def expression(self, p):
        pass

    @_('value MOD value')
    def expression(self, p):
        pass


    @_('value EQ value')
    def condition(self, p):
        pass

    @_('value NE value')
    def condition(self, p):
        pass

    @_('value GT value')
    def condition(self, p):
        pass

    @_('value LT value')
    def condition(self, p):
        pass

    @_('value GE value')
    def condition(self, p):
        pass

    @_('value LE value')
    def condition(self, p):
        pass

    
    @_('NUM')
    def value(self, p):
        return p.NUM

    @_('IDENTIFIER')
    def value(self, p):
        return p.IDENTIFIER


    def error(self, token):
        print(f"Blad {(token if token else '')}")
        return None
    