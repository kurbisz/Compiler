import sly
from sly.lex import *
from sly.yacc import *

from CompManager import CompManager
from CompUtils import *
from precompiler.PreLexer import PreLexer


class PreParser(sly.Parser):

    tokens = PreLexer.tokens
    
    def __init__(self) -> None:
        super().__init__()
        self.manager = CompManager()


    @_('procedures main')
    def program_all(self, p):
        return p.procedures + p.main
    

    
    @_('procedures PROCEDURE proc_head_decl IS VAR declarations BEGIN commands END')
    def procedures(self, p):
        ret_str = p.procedures
        ret_str += "PROCEDURE " 
        ret_str += p.proc_head_decl 
        ret_str += " IS"
        ret_str += "\nVAR " 
        ret_str += p.declarations 
        ret_str += "\nBEGIN\n" 
        ret_str += p.commands 
        ret_str += "\nEND"
        ret_str += "\n\n"
        return ret_str
        
    
    @_('procedures PROCEDURE proc_head_decl IS BEGIN commands END')
    def procedures(self, p):
        ret_str = p.procedures
        ret_str += "PROCEDURE " 
        ret_str += p.proc_head_decl 
        ret_str += " IS\nBEGIN\n"
        ret_str += p.commands 
        ret_str += "\nEND"
        ret_str += "\n\n"
        return ret_str

    @_('')
    def procedures(self, p):
        return ""


    @_('PROGRAM IS VAR declarations BEGIN commands END')
    def main(self, p):
        ret_str = "PROGRAM IS"
        ret_str += "\nVAR "
        ret_str += p.declarations
        ret_str += "\nBEGIN\n"
        ret_str += p.commands
        ret_str += "\nEND"
        return ret_str

    @_('PROGRAM IS BEGIN commands END')
    def main(self, p):
        ret_str = "PROGRAM IS"
        ret_str += "\nBEGIN\n"
        ret_str += p.commands
        ret_str += "\nEND"
        return ret_str


    @_('commands command')
    def commands(self, p):
        ret_str = p.commands
        ret_str += "\n"
        ret_str += p.command
        return ret_str

    @_('command')
    def commands(self, p):
        return p.command


    @_('IDENTIFIER ASSIGN expression SEMICOLON')
    def command(self, p):
        return p.IDENTIFIER + " := " + p.expression + " ;"

    @_('IF condition THEN commands ELSE commands ENDIF')
    def command(self, p):
        if type(p.condition) == bool:
            if p.condition:
                return p.commands0
            else:
                return p.commands1
        ret_str = "IF " + p.condition + " THEN\n"
        ret_str += p.commands0
        ret_str += "\nELSE\n"
        ret_str += p.commands1
        ret_str += "\nENDIF"
        return ret_str

    @_('IF condition THEN commands ENDIF')
    def command(self, p):
        if type(p.condition) == bool:
            if p.condition:
                return p.commands
            else:
                return ""
        ret_str = "IF " + p.condition + " THEN\n"
        ret_str += p.commands
        ret_str += "\nENDIF"
        return ret_str


    @_('WHILE condition DO commands ENDWHILE')
    def command(self, p):
        if type(p.condition) == bool:
            if not p.condition:
                return ""
        ret_str = "WHILE " + p.condition + " DO\n"
        ret_str += p.commands
        ret_str += "\nENDWHILE"
        return ret_str


    @_('REPEAT commands UNTIL condition SEMICOLON')
    def command(self, p):
        if type(p.condition) == bool:
            if p.condition:
                return p.commands
        ret_str = "REPEAT\n"
        ret_str += p.commands
        ret_str += "\nUNTIL " + p.condition + " ;"
        return ret_str

    @_('proc_head SEMICOLON')
    def command(self, p):
        return p.proc_head + " ;"

    @_('READ IDENTIFIER SEMICOLON')
    def command(self, p):
        return "READ " + p.IDENTIFIER + " ;"

    @_('WRITE value SEMICOLON')
    def command(self, p):
        return "WRITE " + str(p.value) + " ;"


    @_('IDENTIFIER L_BRACKET call_declarations R_BRACKET')
    def proc_head(self, p):
        return p.IDENTIFIER + "(" + p.call_declarations + ")"


    @_('IDENTIFIER L_BRACKET proc_declarations R_BRACKET')
    def proc_head_decl(self, p):
        return p.IDENTIFIER + "(" + p.proc_declarations + ")"


    @_('proc_declarations COMMA IDENTIFIER')
    def proc_declarations(self, p):
        return p.proc_declarations + ", " + p.IDENTIFIER

    @_('IDENTIFIER')
    def proc_declarations(self, p):
        return p.IDENTIFIER


    @_('call_declarations COMMA IDENTIFIER')
    def call_declarations(self, p):
        return p.call_declarations + ", " + p.IDENTIFIER

    @_('IDENTIFIER')
    def call_declarations(self, p):
        return p.IDENTIFIER


    @_('declarations COMMA IDENTIFIER')
    def declarations(self, p):
        return p.declarations + ", " + p.IDENTIFIER

    @_('IDENTIFIER')
    def declarations(self, p):
        return p.IDENTIFIER


    @_('value')
    def expression(self, p):
        return str(p.value)

    @_('value ADD value')
    def expression(self, p):
        return str(p.value0) + " + " + str(p.value1)

    @_('value SUB value')
    def expression(self, p):
        return str(p.value0) + " - " + str(p.value1)

    @_('value MUL value')
    def expression(self, p):
        return str(p.value0) + " * " + str(p.value1)

    @_('value DIV value')
    def expression(self, p):
        return str(p.value0) + " / " + str(p.value1)

    @_('value MOD value')
    def expression(self, p):
        return str(p.value0) + " % " + str(p.value1)

    @_('value EQ value')
    def condition(self, p):
        vars = are_variables(p.value0, p.value1)
        if vars == -1:
            return p.value0 == p.value1
        return str(p.value0) + " = " + str(p.value1)

    @_('value NE value')
    def condition(self, p):
        vars = are_variables(p.value0, p.value1)
        if vars == -1:
            return p.value0 != p.value1
        return str(p.value0) + " != " + str(p.value1)

    @_('value GT value')
    def condition(self, p):
        vars = are_variables(p.value0, p.value1)
        if vars == -1:
            return p.value0 > p.value1
        if vars == 1 and p.value0 == 0:
            return False
        return str(p.value0) + " > " + str(p.value1)

    @_('value LT value')
    def condition(self, p):
        vars = are_variables(p.value0, p.value1)
        if vars == -1:
            return p.value0 < p.value1
        if vars == 0 and p.value1 == 0:
            return False
        return str(p.value0) + " < " + str(p.value1)

    @_('value GE value')
    def condition(self, p):
        vars = are_variables(p.value0, p.value1)
        if vars == -1:
            return p.value0 >= p.value1
        if vars == 0 and p.value1 == 0:
            return True
        return str(p.value0) + " >= " + str(p.value1)

    @_('value LE value')
    def condition(self, p):
        vars = are_variables(p.value0, p.value1)
        if vars == -1:
            return p.value0 <= p.value1
        if vars == 1 and p.value0 == 0:
            return True
        return str(p.value0) + " <= " + str(p.value1)

    
    @_('NUM')
    def value(self, p):
        return p.NUM

    @_('IDENTIFIER')
    def value(self, p):
        return p.IDENTIFIER


    def error(self, token):
        print(f"Blad {(token if token else '')}")
        return None
    