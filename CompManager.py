from CompExceptions import VariableNotFoundException
from CompUtils import *


class CompManager:

    def __init__(self) -> None:
        self.act_val_memory_address = 1
        self.variables = []
        self.static_vars = {}

    def add_declaration(self, name):
        new_var = Variable(name, self.act_val_memory_address)
        self.variables.append(new_var)
        self.act_val_memory_address += 1
    

    def read(self, name):
        var = self.__get_variable(name)
        return [Command(f"GET {var.memory_address}")]

    def write_value(self, val):
        res = self.set(val)
        res.append(Command("PUT 0"))
        return res

    def write(self, name):
        var = self.__get_variable(name)
        return [Command(f"PUT {var.memory_address}")]


    def set(self, val):
        return [Command(f"SET {val}")]

    def load(self, name):
        var = self.__get_variable(name)
        return [Command(f"LOAD {var.memory_address}")]

    def load_address(self, address):
        return [Command(f"LOAD {address}")]
    
    def store(self, name):
        var = self.__get_variable(name)
        return [Command(f"STORE {var.memory_address}")]

    def store_act(self) -> int:
        act = self.act_val_memory_address
        self.act_val_memory_address += 1
        return act, [Command(f"STORE {act}")]

    def store_address(self, address):
        return [Command(f"STORE {address}")]
    


    def add(self, v1, v2):
        vars = are_variables(v1, v2)
        if vars == -1:
            commands = self.set(v1 + v2)
        elif vars == 0:
            commands = self.add_var_to_val(v1, v2)
        elif vars == 1:
            commands = self.add_var_to_val(v2, v1)
        else:
            commands = self.add_var_to_var(v1, v2)
        return commands

    def add_var_to_val(self, var_name, val):
        var = self.__get_variable(var_name)
        res = self.set(val)
        res.extend(self.__addVar(var))
        return res

    def add_var_to_var(self, var_name0, var_name1):
        var1 = self.__get_variable(var_name1)
        res = self.load(var_name0)
        res.extend(self.__addVar(var1))
        return res
    
    def __addVar(self, var: Variable):
        return [Command(f"ADD {var.memory_address}")]

    def __add_address(self, address):
        return [Command(f"ADD {address}")]


    def substract(self, v1, v2):
        vars = are_variables(v1, v2)
        if vars == -1:
            commands = self.set(max(v1 - v2, 0))
        elif vars == 0:
            commands = self.sub_var_val(v1, v2)
        elif vars == 1:
            commands = self.sub_val_var(v1, v2)
        else:
            commands = self.sub_var_var(v1, v2)
        return commands
    
    def sub_var_val(self, var_name, val):
        res = self.set(val)
        mem_address, cmds = self.store_act()
        res.extend(cmds)
        res.extend(self.load(var_name))
        res.extend(self.__sub_address(mem_address))
        return res

    def sub_val_var(self, val, var_name):
        var = self.__get_variable(var_name)
        res = self.set(val)
        res.extend(self.__sub_address(var.memory_address))
        return res
    
    def sub_var_var(self, var_name0, var_name1):
        var1 = self.__get_variable(var_name1)
        res = self.load(var_name0)
        res.extend(self.__sub_address(var1.memory_address))
        return res

    def __sub_address(self, memory_address):
        return [Command(f"SUB {memory_address}")]

    
    def multiply(self, v1, v2):
        vars = are_variables(v1, v2)
        if vars == -1:
            commands = self.set(v1 * v2)
        elif vars == 0:
            commands = self.multiply_var_val(v1, v2)
        elif vars == 1:
            commands = self.multiply_var_val(v2, v1)
        else:
            commands = self.multiply_var_var(v1, v2)
        return commands
    
    def multiply_var_val(self, var_name, val):
        if val == 0:
            return self.set(0)
        res_cmds = self.set(0)
        res_mem_address, cmds = self.store_act()
        load_cmds = self.load(var_name)
        act_mem_address, store_cmds = self.store_act()
        res_cmds.extend(cmds)
        res_cmds.extend(load_cmds)
        res_cmds.extend(store_cmds)
        while val > 0:
            if val % 2 == 1:
                store_cmds = self.store_address(act_mem_address)
                load_cmds = self.load_address(res_mem_address)
                add_cmds = self.__add_address(act_mem_address)
                res_store_cmds = self.store_address(res_mem_address)
                act_load_cmds = self.load_address(act_mem_address)

                res_cmds.extend(store_cmds)
                res_cmds.extend(load_cmds)
                res_cmds.extend(add_cmds)
                res_cmds.extend(res_store_cmds)
                res_cmds.extend(act_load_cmds)
            
            multiply_cmds = self.__add_address(0)
            res_cmds.extend(multiply_cmds)
            val = val // 2

        load_cmds = self.load_address(res_mem_address)
        res_cmds.extend(load_cmds)
        return res_cmds        


    
    def multiply_var_var(self, var_name0, var_name1):
        # TODO check if var_name1 is 0 or 1 or 2
        res_cmds = self.__init_static_var(1)

        res_cmds.extend(self.set(0))
        res_mem_address, cmds = self.store_act()
        res_cmds.extend(cmds)
        res_cmds.extend(self.load(var_name0))
        act_mem_address0, store_cmds0 = self.store_act()
        res_cmds.extend(store_cmds0)
        res_cmds.extend(self.load(var_name1))
        act_mem_address1, store_cmds1 = self.store_act()
        res_cmds.extend(store_cmds1)

        # take b, add 1, divide by 2, multiply by 2 and subtract b,
        # check if res is 0, if yes then b % 2 == 0, else b % 2 == 1 
        mul_cmds = []
        mul_cmds.extend(self.__add_address(self.static_vars[1]))
        mul_cmds.extend(self.half())
        mul_cmds.extend(self.__add_address(0))
        mul_cmds.extend(self.__sub_address(act_mem_address1))

        add_to_res_cmds = []
        add_to_res_cmds.extend(self.load_address(res_mem_address))
        add_to_res_cmds.extend(self.__add_address(act_mem_address0))
        add_to_res_cmds.extend(self.store_address(res_mem_address))

        # jump for amount of add to result commands (it will be placed before these commands)
        mod_jump_cmds = self.jump_zero(len(add_to_res_cmds) + 1)

        mul_cmds.extend(mod_jump_cmds)
        mul_cmds.extend(add_to_res_cmds)

        mul_cmds.extend(self.load_address(act_mem_address0))
        mul_cmds.extend(self.__add_address(act_mem_address0))
        mul_cmds.extend(self.store_address(act_mem_address0))

        mul_cmds.extend(self.load_address(act_mem_address1))
        mul_cmds.extend(self.half())

        # REMEMBER TO CHANGE VALUE 3 IF store_address OR jump CHANGE AMOUNT OF LINES
        mul_cmds.extend(self.jump_zero(3))

        mul_cmds.extend(self.store_address(act_mem_address1))
        mul_cmds.extend(self.jump(-len(mul_cmds)))
        
        res_cmds.extend(mul_cmds)
        res_cmds.extend(self.load_address(res_mem_address))
        return res_cmds
 
    def half(self):
        return [Command("HALF")]


    def divide(self, v1, v2):
        vars = are_variables(v1, v2)
        if vars == -1:
            commands = self.set(v1 // v2)
        elif vars == 0:
            commands = self.divide_var_val(v1, v2)
        elif vars == 1:
            commands = self.divide_val_var(v1, v2)
        else:
            commands = self.divide_var_var(v1, v2)
        return commands
    
    def divide_var_val(self, var_name, val):
        var = self.__get_variable(var_name)
        res_cmds = self.__init_static_var(val)
        res_cmds.extend(self.__divide_var_var(var.memory_address, self.static_vars[val]))
        return res_cmds
    
    def divide_val_var(self, val, var_name):
        var = self.__get_variable(var_name)
        res_cmds = self.__init_static_var(val)
        res_cmds.extend(self.__divide_var_var(self.static_vars[val], var.memory_address))
        return res_cmds
    
    def divide_var_var(self, var_name0, var_name1):
        var0 = self.__get_variable(var_name0)
        var1 = self.__get_variable(var_name1)
        return self.__divide_var_var(var0.memory_address, var1.memory_address)

    def __divide_var_var(self, mem_address0, mem_address1):
        # TODO check if value in mem_adress1 is 0 or 1 or 2
        res_cmds = []

        res_cmds.extend(self.set(0))
        res_mem_address, cmds = self.store_act()
        res_cmds.extend(cmds)

        res_cmds.extend(self.load_address(mem_address0))
        act_mem_address0, store_cmds0 = self.store_act()
        res_cmds.extend(store_cmds0)

        res_cmds.extend(self.load_address(mem_address1))
        act_mem_address1, store_cmds1 = self.store_act()
        res_cmds.extend(store_cmds1)

        res_cmds.extend(self.set(1))
        act_mem_address2, store_cmds2 = self.store_act()
        res_cmds.extend(store_cmds2)

        inc_cmds = []

        inc_cmds.extend(self.load_address(act_mem_address2))
        inc_cmds.extend(self.__add_address(act_mem_address2))
        inc_cmds.extend(self.store_address(act_mem_address2))

        inc_cmds.extend(self.load_address(act_mem_address1))
        inc_cmds.extend(self.__add_address(act_mem_address1))
        inc_cmds.extend(self.store_address(act_mem_address1))
        inc_cmds.extend(self.__sub_address(act_mem_address0))

        res_cmds.extend(inc_cmds)
        res_cmds.extend(self.jump_zero(-len(inc_cmds)))

        # res_cmds.extend(self.load_address(act_mem_address2))
        # return res_cmds

        div_cmds = []
        div_cmds.extend(self.load_address(act_mem_address1))
        div_cmds.extend(self.__sub_address(act_mem_address0))

        div_cmds2 = []
        div_cmds2.extend(self.load_address(act_mem_address0))
        div_cmds2.extend(self.__sub_address(act_mem_address1))
        div_cmds2.extend(self.store_address(act_mem_address0))

        div_cmds2.extend(self.load_address(res_mem_address))
        div_cmds2.extend(self.__add_address(act_mem_address2))
        div_cmds2.extend(self.store_address(res_mem_address))

        div_cmds.extend(self.jump_pos(len(div_cmds2) + 1))
        div_cmds.extend(div_cmds2)

        div_cmds3 = []
        div_cmds3.extend(self.load_address(act_mem_address2))
        div_cmds3.extend(self.half())
        div_cmds3.extend(self.store_address(act_mem_address2))


        div_cmds_cont = []
        div_cmds_cont.extend(self.load_address(act_mem_address1))
        div_cmds_cont.extend(self.half())
        div_cmds_cont.extend(self.store_address(act_mem_address1))
        # Change 1 to another value if jump_zero will not be in 1 line
        div_cmds_cont.extend(self.jump(-len(div_cmds) - len(div_cmds3) - len(div_cmds_cont) - 1))

        div_cmds3.extend(self.jump_zero(len(div_cmds_cont) + 1))

        div_cmds.extend(div_cmds3)
        div_cmds.extend(div_cmds_cont)

        res_cmds.extend(div_cmds)
        res_cmds.extend(self.load_address(res_mem_address))

        return res_cmds


    def modulo(self, v1, v2):
        vars = are_variables(v1, v2)
        if vars == -1:
            commands = self.set(v1 % v2)
        elif vars == 0:
            commands = self.modulo_var_val(v1, v2)
        elif vars == 1:
            commands = self.modulo_val_var(v1, v2)
        else:
            commands = self.modulo_var_var(v1, v2)
        return commands
    
    def modulo_var_val(self, var_name, val):
        var = self.__get_variable(var_name)
        res_cmds = self.__init_static_var(val)
        res_cmds.extend(self.__modulo_var_var(var.memory_address, self.static_vars[val]))
        return res_cmds
    
    def modulo_val_var(self, val, var_name):
        var = self.__get_variable(var_name)
        res_cmds = self.__init_static_var(val)
        res_cmds.extend(self.__modulo_var_var(self.static_vars[val], var.memory_address))
        return res_cmds
    
    def modulo_var_var(self, var_name0, var_name1):
        var0 = self.__get_variable(var_name0)
        var1 = self.__get_variable(var_name1)
        return self.__modulo_var_var(var0.memory_address, var1.memory_address)

    def __modulo_var_var(self, mem_address0, mem_address1):
        # TODO check if value in mem_adress1 is 0 or 1 or 2
        res_cmds = []

        res_cmds.extend(self.set(0))
        res_mem_address, cmds = self.store_act()
        res_cmds.extend(cmds)

        res_cmds.extend(self.load_address(mem_address0))
        act_mem_address0, store_cmds0 = self.store_act()
        res_cmds.extend(store_cmds0)

        res_cmds.extend(self.load_address(mem_address1))
        act_mem_address1, store_cmds1 = self.store_act()
        res_cmds.extend(store_cmds1)

        res_cmds.extend(self.set(1))
        act_mem_address2, store_cmds2 = self.store_act()
        res_cmds.extend(store_cmds2)

        inc_cmds = []

        inc_cmds.extend(self.load_address(act_mem_address2))
        inc_cmds.extend(self.__add_address(act_mem_address2))
        inc_cmds.extend(self.store_address(act_mem_address2))

        inc_cmds.extend(self.load_address(act_mem_address1))
        inc_cmds.extend(self.__add_address(act_mem_address1))
        inc_cmds.extend(self.store_address(act_mem_address1))
        inc_cmds.extend(self.__sub_address(act_mem_address0))

        res_cmds.extend(inc_cmds)
        res_cmds.extend(self.jump_zero(-len(inc_cmds)))

        # res_cmds.extend(self.load_address(act_mem_address2))
        # return res_cmds

        div_cmds = []
        div_cmds.extend(self.load_address(act_mem_address1))
        div_cmds.extend(self.__sub_address(act_mem_address0))

        div_cmds2 = []
        div_cmds2.extend(self.load_address(act_mem_address0))
        div_cmds2.extend(self.__sub_address(act_mem_address1))
        div_cmds2.extend(self.store_address(act_mem_address0))

        div_cmds2.extend(self.load_address(res_mem_address))
        div_cmds2.extend(self.__add_address(act_mem_address2))
        div_cmds2.extend(self.store_address(res_mem_address))

        div_cmds.extend(self.jump_pos(len(div_cmds2) + 1))
        div_cmds.extend(div_cmds2)

        div_cmds3 = []
        div_cmds3.extend(self.load_address(act_mem_address2))
        div_cmds3.extend(self.half())
        div_cmds3.extend(self.store_address(act_mem_address2))


        div_cmds_cont = []
        div_cmds_cont.extend(self.load_address(act_mem_address1))
        div_cmds_cont.extend(self.half())
        div_cmds_cont.extend(self.store_address(act_mem_address1))
        # Change 1 to another value if jump_zero will not be in 1 line
        div_cmds_cont.extend(self.jump(-len(div_cmds) - len(div_cmds3) - len(div_cmds_cont) - 1))

        div_cmds3.extend(self.jump_zero(len(div_cmds_cont) + 1))

        div_cmds.extend(div_cmds3)
        div_cmds.extend(div_cmds_cont)

        res_cmds.extend(div_cmds)
        res_cmds.extend(self.load_address(act_mem_address0))

        return res_cmds

    def jump(self, add_index):
        return [Command("JUMP", add_index)]

    def jump_zero(self, add_index):
        return [Command("JZERO", add_index)]

    def jump_pos(self, add_index):
        return [Command("JPOS", add_index)]


    def __init_static_var(self, val):
        if val in self.static_vars:
            return []
        cmds = self.set(val)
        mem_address, store_cmds = self.store_act()
        self.static_vars[val] = mem_address
        cmds.extend(store_cmds)
        return cmds

    def __get_variable(self, name):
        for var in self.variables:
            if var.name == name:
                return var
        raise VariableNotFoundException(f"Variable with name {name} was not defined.")
