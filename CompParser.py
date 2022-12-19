import sly
from sly.lex import *
from sly.yacc import *

from CompLexer import CompLexer
from CompManager import CompManager
from CompUtils import *


class CompParser(sly.Parser):

    tokens = CompLexer.tokens

    def __init__(self) -> None:
        super().__init__()
        self.manager = CompManager()


    @_('procedures main')
    def program_all(self, p):
        _, cmds = p.procedures
        if cmds:
            new_cmds = self.manager.jump(len(cmds) + 1)
            new_cmds.extend(cmds)
            cmds = new_cmds
        cmds.extend(p.main)
        res: list[str] = []
        index = 0
        for command in cmds:
            res.append(command.get_value(index))
            index += 1
        return res
    

    
    @_('procedures PROCEDURE proc_head_decl IS VAR declarations BEGIN commands END')
    def procedures(self, p):
        index, cmds = p.procedures
        proc_name = p.proc_head_decl
        cmds.extend(p.commands)
        cmds.extend(self.manager.create_procedure(proc_name, index))
        return index + len(cmds), cmds
        
    
    @_('procedures PROCEDURE proc_head_decl IS BEGIN commands END')
    def procedures(self, p):
        index, cmds = p.procedures
        proc_name = p.proc_head_decl
        cmds.extend(p.commands)
        cmds.extend(self.manager.create_procedure(proc_name, index))
        return index + len(cmds), cmds

    @_('')
    def procedures(self, p):
        # start index is 1 because we have to put jump at the beginning
        return 1, []


    @_('PROGRAM IS VAR declarations BEGIN commands END')
    def main(self, p):
        return p.commands

    @_('PROGRAM IS BEGIN commands END')
    def main(self, p):
        return p.commands


    @_('commands command')
    def commands(self, p):
        commands = p.commands
        commands.extend(p.command)
        return commands

    @_('command')
    def commands(self, p):
        return p.command

    @_('CLEAR')
    def command(self, p):
        self.manager.clear_cache()
        return []


    @_('IDENTIFIER ASSIGN expression SEMICOLON')
    def command(self, p):
        commands = p.expression
        commands.extend(self.manager.store(p.IDENTIFIER))
        return commands

    @_('IF condition THEN commands ELSE commands ENDIF')
    def command(self, p):
        cond_code, cond_commands = p.condition
        commands = p.commands0
        else_commands = p.commands1
        res = cond_commands

        commands.extend(self.manager.jump(len(else_commands) + 1))
        
        if cond_code == 0:
            res.extend(self.manager.jump_zero(len(commands) + 1))
        else:
            res.extend(self.manager.jump_pos(len(commands) + 1))
        
        res.extend(commands)
        res.extend(else_commands)

        return res

    @_('IF condition THEN commands ENDIF')
    def command(self, p):
        cond_code, cond_commands = p.condition
        commands = p.commands
        res = cond_commands
        
        if cond_code == 0:
            res.extend(self.manager.jump_zero(len(commands) + 1))
        else:
            res.extend(self.manager.jump_pos(len(commands) + 1))
        
        res.extend(commands)
        return res


    @_('WHILE condition DO commands ENDWHILE')
    def command(self, p):
        commands = p.commands
        cond_code, cond_commands = p.condition

        res_cmds = self.manager.jump(len(commands) + 1)
        res_cmds.extend(commands)
        res_cmds.extend(cond_commands)

        if cond_code == 1:
            res_cmds.extend(self.manager.jump_zero(-len(commands) - len(cond_commands)))
        else:
            res_cmds.extend(self.manager.jump_pos(-len(commands) - len(cond_commands)))

        return res_cmds


    @_('REPEAT commands UNTIL condition SEMICOLON')
    def command(self, p):
        commands = p.commands
        cond_code, cond_commands = p.condition

        res_cmds = []
        res_cmds.extend(commands)
        res_cmds.extend(cond_commands)

        if cond_code == 0:
            res_cmds.extend(self.manager.jump_zero(-len(commands) - len(cond_commands)))
        else:
            res_cmds.extend(self.manager.jump_pos(-len(commands) - len(cond_commands)))
        return res_cmds

    @_('proc_head SEMICOLON')
    def command(self, p):
        return p.proc_head

    @_('READ IDENTIFIER SEMICOLON')
    def command(self, p):
        return self.manager.read(p.IDENTIFIER)

    @_('WRITE value SEMICOLON')
    def command(self, p):
        if is_int(p.value):
            commands = self.manager.write_value(p.value)
        else:
            commands = self.manager.write(p.value)
        return commands


    @_('IDENTIFIER L_BRACKET call_declarations R_BRACKET')
    def proc_head(self, p):
        return self.manager.call_procedure(p.IDENTIFIER, p.call_declarations)


    @_('IDENTIFIER L_BRACKET proc_declarations R_BRACKET')
    def proc_head_decl(self, p):
        return p.IDENTIFIER


    @_('proc_declarations COMMA IDENTIFIER')
    def proc_declarations(self, p):
        self.manager.add_declaration(p.IDENTIFIER, True)

    @_('IDENTIFIER')
    def proc_declarations(self, p):
        self.manager.add_declaration(p.IDENTIFIER, True)


    @_('call_declarations COMMA IDENTIFIER')
    def call_declarations(self, p):
        p.call_declarations.append(p.IDENTIFIER)
        return p.call_declarations

    @_('IDENTIFIER')
    def call_declarations(self, p):
        return [p.IDENTIFIER]


    @_('declarations COMMA IDENTIFIER')
    def declarations(self, p):
        self.manager.add_declaration(p.IDENTIFIER)

    @_('IDENTIFIER')
    def declarations(self, p):
        self.manager.add_declaration(p.IDENTIFIER)


    @_('value')
    def expression(self, p):
        if is_int(p.value):
            commands = self.manager.set(p.value)
        else:
            commands = self.manager.load(p.value)
        return commands

    @_('value ADD value')
    def expression(self, p):
        return self.manager.add(p.value0, p.value1)

    @_('value SUB value')
    def expression(self, p):
        return self.manager.substract(p.value0, p.value1)

    @_('value MUL value')
    def expression(self, p):
        return self.manager.multiply(p.value0, p.value1)

    @_('value DIV value')
    def expression(self, p):
        return self.manager.divide(p.value0, p.value1)

    @_('value MOD value')
    def expression(self, p):
        return self.manager.modulo(p.value0, p.value1)

    # 0 means JZERO, 1 means JPOS (in IF statements)
    @_('value EQ value')
    def condition(self, p):
        print("TEST0")
        return self.manager.equal(p.value0, p.value1, 1)

    @_('value NE value')
    def condition(self, p):
        return self.manager.equal(p.value0, p.value1, 0)

    @_('value GT value')
    def condition(self, p):
        return self.manager.greater_than(p.value0, p.value1, 0)

    @_('value LT value')
    def condition(self, p):
        return self.manager.greater_than(p.value1, p.value0, 0)

    @_('value GE value')
    def condition(self, p):
        return self.manager.greater_than(p.value1, p.value0, 1)

    @_('value LE value')
    def condition(self, p):
        return self.manager.greater_than(p.value0, p.value1, 1)

    
    @_('NUM')
    def value(self, p):
        return p.NUM

    @_('IDENTIFIER')
    def value(self, p):
        return p.IDENTIFIER


    def error(self, token):
        print(f"Blad {(token if token else '')}")
        return None
    