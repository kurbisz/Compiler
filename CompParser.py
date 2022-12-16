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
        commands = p.main
        res: list[str] = []
        index = 0
        for command in commands:
            res.append(command.get_value(index))
            index += 1
        return res
    

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
        pass

    @_('REPEAT commands UNTIL condition SEMICOLON')
    def command(self, p):
        pass

    @_('proc_head SEMICOLON')
    def command(self, p):
        pass

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
        pass

    # 0 means JZERO, 1 means JPOS
    @_('value EQ value')
    def condition(self, p):
        cmds = self.manager.substract(p.value0, p.value1)
        cmds2 = self.manager.substract(p.value1, p.value0)
        cmds.extend(self.manager.jump_pos(len(cmds2) + 1))
        cmds.extend(cmds2)
        return 1, cmds

    @_('value NE value')
    def condition(self, p):
        cmds = self.manager.substract(p.value0, p.value1)
        cmds2 = self.manager.substract(p.value1, p.value0)
        cmds.extend(self.manager.jump_pos(len(cmds2) + 1))
        cmds.extend(cmds2)
        return 0, cmds

    @_('value GT value')
    def condition(self, p):
        return 0, self.manager.substract(p.value0, p.value1)

    @_('value LT value')
    def condition(self, p):
        return 0, self.manager.substract(p.value1, p.value0)

    @_('value GE value')
    def condition(self, p):
        return 1, self.manager.substract(p.value1, p.value0)

    @_('value LE value')
    def condition(self, p):
        return 1, self.manager.substract(p.value0, p.value1)

    
    @_('NUM')
    def value(self, p):
        return p.NUM

    @_('IDENTIFIER')
    def value(self, p):
        return p.IDENTIFIER


    def error(self, token):
        print(f"Blad {(token if token else '')}")
        return None
    