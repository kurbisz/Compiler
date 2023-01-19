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
        self.manager : PreStore = PreStore()
        self.fake_comp_manager : CompManager = CompManager()



    @_('procedures main')
    def program_all(self, p):
        return self.manager, (p.procedures + p.main)

    
    @_('procedures PROCEDURE proc_head_decl IS VAR declarations BEGIN commands END')
    def procedures(self, p):
        ret_str = p.procedures
        ret_str += "PROCEDURE " 
        ret_str += p.proc_head_decl 
        ret_str += " IS"
        ret_str += "\nVAR " 
        ret_str += p.declarations 
        ret_str += "\nBEGIN\n" 
        ret_str += "!!!\n"
        ret_str += p.commands[0] 
        ret_str += "\nEND"
        ret_str += "\n\n"
        proc_name = p.proc_head_decl.split(" ")[0]
        self.manager.proc_names[proc_name].cmds = p.commands[0]
        self.manager.proc_names[proc_name].var_declarations = p.declarations.split(" , ")
        return ret_str
        
    
    @_('procedures PROCEDURE proc_head_decl IS BEGIN commands END')
    def procedures(self, p):
        ret_str = p.procedures
        ret_str += "PROCEDURE " 
        ret_str += p.proc_head_decl 
        ret_str += " IS\nBEGIN\n"
        ret_str += "!!!\n"
        ret_str += p.commands[0]
        ret_str += "\nEND"
        ret_str += "\n\n"
        proc_name = p.proc_head_decl.split(" ")[0]
        self.manager.proc_names[proc_name].cmds = p.commands[0]
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
        ret_str += "!!!\n"
        ret_str += p.commands[0]
        ret_str += "\nEND"
        return ret_str

    @_('PROGRAM IS BEGIN commands END')
    def main(self, p):
        ret_str = "PROGRAM IS"
        ret_str += "\nBEGIN\n"
        ret_str += p.commands[0]
        ret_str += "\nEND"
        return ret_str


    @_('commands command')
    def commands(self, p):
        cmd = p.command[0]
        initialized = p.command[1]
        ret_str = p.commands[0]
        ret_str += "\n"
        ret_str += cmd
        return ret_str, initialized + p.commands[1]

    @_('command')
    def commands(self, p):
        cmd = p.command[0]
        initialized = p.command[1]
        return cmd, initialized


    @_('IDENTIFIER ASSIGN expression SEMICOLON')
    def command(self, p):
        return " " + p.IDENTIFIER + " := " + p.expression + " ;", [p.IDENTIFIER]

    @_('IF condition THEN commands ELSE commands ENDIF')
    def command(self, p):
        if type(p.condition) == bool:
            if p.condition:
                return p.commands0[0], p.commands0[1]
            else:
                return p.commands1[0], p.commands1[1]
        if p.commands0[0] == p.commands1[0]:
            return p.commands0[0], p.commands0[1]
        ret_str = "IF " + p.condition + " THEN\n"
        ret_str += "!!!\n"
        ret_str += p.commands0[0]
        ret_str += "\nELSE\n"
        ret_str += "!!!\n"
        ret_str += p.commands1[0]
        ret_str += "\nENDIF"
        return ret_str, p.commands0[1] + p.commands1[1]

    @_('IF condition THEN commands ENDIF')
    def command(self, p):
        if type(p.condition) == bool:
            if p.condition:
                return p.commands[0], p.commands[1]
            else:
                return "", []
        ret_str = "IF " + p.condition + " THEN\n"
        ret_str += "!!!\n"
        ret_str += p.commands[0]
        ret_str += "\nENDIF"
        return ret_str, p.commands[1]


    @_('WHILE condition DO commands ENDWHILE')
    def command(self, p):
        cond = p.condition
        if type(cond) == bool:
            if not p.condition:
                return "", []
            else:
                cond = "1 > 0"
        ret_str = "!!!\n"
        ret_str += "WHILE " + cond + " DO\n^^^ " + " , ".join(p.commands[1]) + "\n"
        ret_str += p.commands[0]
        ret_str += "\nENDWHILE"
        return ret_str, p.commands[1]


    @_('REPEAT commands UNTIL condition SEMICOLON')
    def command(self, p):
        cond = p.condition
        if type(p.condition) == bool:
            if p.condition:
                return p.commands[0], p.commands[1]
            else:
                cond = "1 < 0"
        ret_str = "!!!\n"
        ret_str += "REPEAT\n^^^ " + " , ".join(p.commands[1]) + "\n"
        ret_str += p.commands[0]
        ret_str += "\nUNTIL " + cond + " ;"
        return ret_str, p.commands[1]

    @_('proc_head SEMICOLON')
    def command(self, p):
        return p.proc_head[0] + " ;", p.proc_head[1]

    @_('READ IDENTIFIER SEMICOLON')
    def command(self, p):
        return "READ " + p.IDENTIFIER + " ;", [p.IDENTIFIER]

    @_('WRITE value SEMICOLON')
    def command(self, p):
        return "WRITE " + str(p.value) + " ;", []


    @_('IDENTIFIER L_BRACKET call_declarations R_BRACKET')
    def proc_head(self, p):
        self.manager.proc_names[p.IDENTIFIER].used_times += 1
        return p.IDENTIFIER + " ( " + p.call_declarations[0] + " )", p.call_declarations[1]


    @_('IDENTIFIER L_BRACKET proc_declarations R_BRACKET')
    def proc_head_decl(self, p):
        self.manager.proc_names[p.IDENTIFIER] = PreProcedure(p.proc_declarations)
        return p.IDENTIFIER + " ( " + p.proc_declarations + " )"


    @_('proc_declarations COMMA IDENTIFIER')
    def proc_declarations(self, p):
        return p.proc_declarations + " , " + p.IDENTIFIER

    @_('IDENTIFIER')
    def proc_declarations(self, p):
        return p.IDENTIFIER


    @_('call_declarations COMMA IDENTIFIER')
    def call_declarations(self, p):
        return p.call_declarations[0] + " , " + p.IDENTIFIER, p.call_declarations[1] + [p.IDENTIFIER]

    @_('IDENTIFIER')
    def call_declarations(self, p):
        return p.IDENTIFIER, [p.IDENTIFIER]


    @_('declarations COMMA IDENTIFIER')
    def declarations(self, p):
        return p.declarations + " , " + p.IDENTIFIER

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
        if are_variables(p.value0, p.value1) == 0:
            if (val := p.value1) not in self.manager.numbers:
                self.manager.numbers.append(val)
        return str(p.value0) + " - " + str(p.value1)

    @_('value MUL value')
    def expression(self, p):
        a = p.value0
        b = p.value1
        if move_to_procedure("*", a, b):
            if is_i(a) and is_i(b):
                self.manager.mul_cost += len(self.fake_comp_manager.multiply(int(a), int(b)))
                self.manager.mul_am += 1
            elif is_i(a) and not is_i(b):
                self.fake_comp_manager.add_declaration("b", False)
                self.fake_comp_manager.set_initialized("b")
                self.manager.mul_cost += len(self.fake_comp_manager.multiply("b", int(a)))
                self.manager.mul_am += 1
                self.fake_comp_manager.variables.clear()
                self.fake_comp_manager._CompManager__clear_p0()
            elif not is_i(a) and is_i(b):
                self.fake_comp_manager.add_declaration("a", False)
                self.fake_comp_manager.set_initialized("a")
                self.manager.mul_cost += len(self.fake_comp_manager.multiply("a", int(b)))
                self.manager.mul_am += 1
                self.fake_comp_manager.variables.clear()
                self.fake_comp_manager._CompManager__clear_p0()
            else:
                self.fake_comp_manager.add_declaration("a", False)
                self.fake_comp_manager.set_initialized("a")
                self.fake_comp_manager.add_declaration("b", False)
                self.fake_comp_manager.set_initialized("b")
                self.manager.mul_cost += len(self.fake_comp_manager.multiply("a", "b"))
                self.manager.mul_am += 1
                self.fake_comp_manager.variables.clear()
                self.fake_comp_manager._CompManager__clear_p0()
        return str(p.value0) + " * " + str(p.value1)

    @_('value DIV value')
    def expression(self, p):
        if move_to_procedure("/", p.value0, p.value1):
            self.manager.div_am += 1
        return str(p.value0) + " / " + str(p.value1)

    @_('value MOD value')
    def expression(self, p):
        if move_to_procedure("%", p.value0, p.value1):
            self.manager.mod_am += 1
        return str(p.value0) + " % " + str(p.value1)

    @_('value EQ value')
    def condition(self, p):
        vars = are_variables(p.value0, p.value1)
        if vars == -1:
            return p.value0 == p.value1
        if vars == 0:
            if (val := p.value1) not in self.manager.numbers:
                self.manager.numbers.append(val)
        elif vars == 1:
            if (val := p.value0) not in self.manager.numbers:
                self.manager.numbers.append(val)
        return str(p.value0) + " = " + str(p.value1)

    @_('value NE value')
    def condition(self, p):
        vars = are_variables(p.value0, p.value1)
        if vars == -1:
            return p.value0 != p.value1
        if vars == 0:
            if (val := p.value1) not in self.manager.numbers:
                self.manager.numbers.append(val)
        elif vars == 1:
            if (val := p.value0) not in self.manager.numbers:
                self.manager.numbers.append(val)
        return str(p.value0) + " != " + str(p.value1)

    @_('value GT value')
    def condition(self, p):
        vars = are_variables(p.value0, p.value1)
        if vars == -1:
            return p.value0 > p.value1
        if vars == 1 and p.value0 == 0:
            return False
        if vars == 0:
            if (val := p.value1) not in self.manager.numbers:
                self.manager.numbers.append(val)
        return str(p.value0) + " > " + str(p.value1)

    @_('value LT value')
    def condition(self, p):
        vars = are_variables(p.value0, p.value1)
        if vars == -1:
            return p.value0 < p.value1
        if vars == 0 and p.value1 == 0:
            return False
        if vars == 1:
            if (val := p.value0) not in self.manager.numbers:
                self.manager.numbers.append(val)
        return str(p.value0) + " < " + str(p.value1)

    @_('value GE value')
    def condition(self, p):
        vars = are_variables(p.value0, p.value1)
        if vars == -1:
            return p.value0 >= p.value1
        if vars == 0 and p.value1 == 0:
            return True
        if vars == 1:
            if (val := p.value0) not in self.manager.numbers:
                self.manager.numbers.append(val)
        return str(p.value0) + " >= " + str(p.value1)

    @_('value LE value')
    def condition(self, p):
        vars = are_variables(p.value0, p.value1)
        if vars == -1:
            return p.value0 <= p.value1
        if vars == 1 and p.value0 == 0:
            return True
        if vars == 0:
            if (val := p.value1) not in self.manager.numbers:
                self.manager.numbers.append(val)
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
    