from CompExceptions import VariableNotFoundException
from CompUtils import *


class CompManager:

    optimization : bool = True

    def __init__(self) -> None:
        self.act_val_memory_address = 1
        self.variables = []
        self.static_vars = {}
        self.procedures = []
        self.__clear_p0()

    def add_declaration(self, name, is_reference = False):
        new_var = Variable(name, self.act_val_memory_address, is_reference)
        self.variables.append(new_var)
        self.act_val_memory_address += 1
    

    def read(self, name):
        var : Variable = self.__get_variable(name)
        self.__var_changed(var)
        if var.is_reference:
            self.__clear_p0()
            cmds = [Command(f"GET 0")]
            cmds.extend(self.store_i_address(var.memory_address))
            return cmds
        return [Command(f"GET {var.memory_address}")]

    def write_value(self, val):
        res = self.set(val)
        res.append(Command("PUT 0"))
        return res

    def write(self, name):
        var : Variable = self.__get_variable(name)
        if var.is_reference:
            cmds = self.load_i_address(var.memory_address)
            cmds.append(Command("PUT 0"))
            return cmds
        return [Command(f"PUT {var.memory_address}")]


    def set(self, val):
        self.p0 = [Value(val)]
        return [Command(f"SET {val}")]

    def load(self, name):
        var : Variable = self.__get_variable(name)
        if var.is_reference:
            self.p0 = [IAddress(var.memory_address)]
            return [Command(f"LOADI {var.memory_address}")]
        obj = Address(var.memory_address)
        if CompManager.optimization and self.__is_in_p0(obj):
            return []
        self.p0 = [obj]
        return [Command(f"LOAD {var.memory_address}")]


    def load_i_address(self, address):
        self.p0 = [IAddress(address)]
        return [Command(f"LOADI {address}")]

    def load_address(self, address):
        self.p0 = [Address(address)]
        return [Command(f"LOAD {address}")]
    
    def store(self, name):
        var = self.__get_variable(name)
        self.__var_changed(var)
        if var.is_reference:
            self.p0.append(IAddress(var.memory_address))
            return [Command(f"STOREI {var.memory_address}")]
        self.p0.append(Address(var.memory_address))
        return [Command(f"STORE {var.memory_address}")]

    def store_act(self) -> int:
        act = self.act_val_memory_address
        self.act_val_memory_address += 1
        self.p0.append(Address(act))
        return act, [Command(f"STORE {act}")]

    def store_address(self, address):
        self.p0.append(Address(address))
        return [Command(f"STORE {address}")]

    def store_i_address(self, address):
        self.p0.append(IAddress(address))
        return [Command(f"STOREI {address}")]
    

    def create_procedure(self, proc_name, start_index):
        act = self.act_val_memory_address
        self.act_val_memory_address += 1
        proc = Procedure(proc_name, self.variables.copy(), start_index, act)
        self.procedures.append(proc)
        self.variables.clear()
        return self.jump_i_address(act)

    def call_procedure(self, proc_name, declarations):
        cmds = []
        proc : Procedure = self.__get_procedure(proc_name)
        i = 0
        self.__clear_p0()
        for variable in proc.arguments:
            if variable.is_reference:
                dec = self.__get_variable(declarations[i])
                cmds.extend(self.set(dec.memory_address))
                cmds.extend(self.store_address(variable.memory_address))
                self.__var_changed(variable)
                i += 1
        call_cmds = []
        call_cmds.extend(self.store_address(proc.return_memory_adress))
        call_cmds.extend(self.jump_address(proc.start_index))
        cmds.append(Command("SET", len(call_cmds) + 1))
        cmds.extend(call_cmds)
        self.__clear_p0()
        return cmds


    def add(self, v1, v2):
        vars = are_variables(v1, v2)
        if vars == -1:
            commands = self.set(v1 + v2)
        elif vars == 0:
            operation = Operation(str(v1) + " + " + str(v2))
            if CompManager.optimization and self.__is_in_p0(operation):
                return []
            commands = self.add_var_to_val(v1, v2)
            self.__clear_p0()
            self.p0.extend([operation, Operation(str(v2) + " + " + str(v1))])
        elif vars == 1:
            operation = Operation(str(v1) + " + " + str(v2))
            if CompManager.optimization and self.__is_in_p0(operation):
                return []
            commands = self.add_var_to_val(v2, v1)
            self.__clear_p0()
            self.p0.extend([operation, Operation(str(v2) + " + " + str(v1))])
        else:
            operation = Operation(str(v1) + " + " + str(v2))
            if CompManager.optimization and self.__is_in_p0(operation):
                return []
            commands = self.add_var_to_var(v1, v2)
            self.__clear_p0()
            self.p0.extend([operation, Operation(str(v2) + " + " + str(v1))])
        return commands

    def add_var_to_val(self, var_name, val):
        var = self.__get_variable(var_name)
        res = self.set(val)
        if var.is_reference:
            res.extend(self.__add_i_var(var))
        else:
            res.extend(self.__add_var(var))
        return res

    def add_var_to_var(self, var_name0, var_name1):
        var1 = self.__get_variable(var_name1)
        res = self.load(var_name0)
        if var1.is_reference:
            res.extend(self.__add_i_var(var1))
        else:
            res.extend(self.__add_var(var1))
        return res
    
    def __add_var(self, var: Variable):
        self.__clear_p0()
        return [Command(f"ADD {var.memory_address}")]
    
    def __add_i_var(self, var: Variable):
        self.__clear_p0()
        return [Command(f"ADDI {var.memory_address}")]

    def __add_address(self, address):
        self.__clear_p0()
        return [Command(f"ADD {address}")]


    def substract(self, v1, v2):
        vars = are_variables(v1, v2)
        if vars == -1:
            commands = self.set(max(v1 - v2, 0))
        elif vars == 0:
            operation = Operation(str(v1) + " - " + str(v2))
            if CompManager.optimization and self.__is_in_p0(operation):
                return []
            commands = self.sub_var_val(v1, v2)
            self.__clear_p0()
            self.p0.append(operation)
        elif vars == 1:
            operation = Operation(str(v1) + " - " + str(v2))
            if CompManager.optimization and self.__is_in_p0(operation):
                return []
            commands = self.sub_val_var(v1, v2)
            self.__clear_p0()
            self.p0.append(operation)
        else:
            operation = Operation(str(v1) + " - " + str(v2))
            if CompManager.optimization and self.__is_in_p0(operation):
                return []
            commands = self.sub_var_var(v1, v2)
            self.__clear_p0()
            self.p0.append(operation)
        return commands
    
    def sub_var_val(self, var_name, val):
        if val == 0:
            return self.load(var_name)
        res = self.set(val)
        mem_address, cmds = self.store_act()
        res.extend(cmds)
        res.extend(self.load(var_name))
        res.extend(self.__sub_address(mem_address))
        return res

    def sub_val_var(self, val, var_name):
        if val == 0:
            return self.set(0)
        var = self.__get_variable(var_name)
        res = self.set(val)
        res.extend(self.__sub(var))
        return res
    
    def sub_var_var(self, var_name0, var_name1):
        if var_name0 == var_name1:
            return self.set(0)
        var1 = self.__get_variable(var_name1)
        res = self.load(var_name0)
        res.extend(self.__sub(var1))
        return res

    def __sub(self, var: Variable):
        if var.is_reference:
            return [Command(f"SUBI {var.memory_address}")]
        return [Command(f"SUB {var.memory_address}")]

    def __sub_address(self, memory_address):
        return [Command(f"SUB {memory_address}")]

    
    def multiply(self, v1, v2):
        vars = are_variables(v1, v2)
        if vars == -1:
            commands = self.set(v1 * v2)
        elif vars == 0:
            operation = Operation(str(v1) + " * " + str(v2))
            if CompManager.optimization and self.__is_in_p0(operation):
                return []
            commands = self.multiply_var_val(v1, v2)
            self.__clear_p0()
            self.p0.extend([operation, Operation(str(v2) + " * " + str(v1))])
        elif vars == 1:
            operation = Operation(str(v1) + " * " + str(v2))
            if CompManager.optimization and self.__is_in_p0(operation):
                return []
            commands = self.multiply_var_val(v2, v1)
            self.__clear_p0()
            self.p0.extend([operation, Operation(str(v2) + " * " + str(v1))])
        else:
            operation = Operation(str(v1) + " * " + str(v2))
            if CompManager.optimization and self.__is_in_p0(operation):
                return []
            commands = self.multiply_var_var(v1, v2)
            self.__clear_p0()
            self.p0.extend([operation, Operation(str(v2) + " * " + str(v1))])
        return commands
    
    def multiply_var_val(self, var_name, val):
        if val == 0:
            return self.set(0)
        is_power, power = isPowerOfTwo(val)
        if is_power:
            res_cmds = self.load(var_name)
            for i in range(power):
                res_cmds.extend(self.__add_address(0))
                self.__clear_p0()
            return res_cmds
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
                self.__clear_p0()
                res_store_cmds = self.store_address(res_mem_address)
                act_load_cmds = self.load_address(act_mem_address)

                res_cmds.extend(store_cmds)
                res_cmds.extend(load_cmds)
                res_cmds.extend(add_cmds)
                res_cmds.extend(res_store_cmds)
                res_cmds.extend(act_load_cmds)
            
            multiply_cmds = self.__add_address(0)
            self.__clear_p0()
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
        
        res_cmds.extend(self.substract(var_name0, var_name1))
        self.__clear_p0()

        swap_cmds = []
        # this is by default multiplied by 2
        swap_cmds.extend(self.load(var_name0))
        act_mem_address0, store_cmds0 = self.store_act()
        swap_cmds.extend(store_cmds0)

        # this is by default divided by 2
        swap_cmds.extend(self.load(var_name1))
        act_mem_address1, store_cmds1 = self.store_act()
        swap_cmds.extend(store_cmds1)


        swap_cmds.extend(self.jump(5)) # skip this jump, load + store, load + store
        self.__clear_p0()

        res_cmds.extend(self.jump_zero(len(swap_cmds) + 1))
        res_cmds.extend(swap_cmds)

        # change var0 with var1 (because it will be faster to divide smaller number)
        self.act_val_memory_address -= 2
        res_cmds.extend(self.load(var_name1))
        act_mem_address0, store_cmds0 = self.store_act()
        res_cmds.extend(store_cmds0)
        self.__clear_p0()

        res_cmds.extend(self.load(var_name0))
        act_mem_address1, store_cmds1 = self.store_act()
        res_cmds.extend(store_cmds1)

        # take b, add 1, divide by 2, multiply by 2 and subtract b,
        # check if res is 0, if yes then b % 2 == 0, else b % 2 == 1 
        mul_cmds = []
        mul_cmds.extend(self.__add_address(self.static_vars[1]))
        mul_cmds.extend(self.half())
        mul_cmds.extend(self.__add_address(0))
        mul_cmds.extend(self.__sub_address(act_mem_address1))
        self.__clear_p0()

        add_to_res_cmds = []
        add_to_res_cmds.extend(self.load_address(res_mem_address))
        add_to_res_cmds.extend(self.__add_address(act_mem_address0))
        add_to_res_cmds.extend(self.store_address(res_mem_address))
        self.__clear_p0()

        # jump for amount of add to result commands (it will be placed before these commands)
        mod_jump_cmds = self.jump_zero(len(add_to_res_cmds) + 1)

        mul_cmds.extend(mod_jump_cmds)
        mul_cmds.extend(add_to_res_cmds)

        mul_cmds.extend(self.load_address(act_mem_address0))
        mul_cmds.extend(self.__add_address(act_mem_address0))
        mul_cmds.extend(self.store_address(act_mem_address0))
        self.__clear_p0()

        mul_cmds.extend(self.load_address(act_mem_address1))
        mul_cmds.extend(self.half())

        # REMEMBER TO CHANGE VALUE 3 IF store_address OR jump CHANGE AMOUNT OF LINES
        mul_cmds.extend(self.jump_zero(3))

        mul_cmds.extend(self.store_address(act_mem_address1))
        mul_cmds.extend(self.jump(-len(mul_cmds)))
        self.__clear_p0()
        
        # skip multiplication if b was equal to 0
        res_cmds.extend(self.jump_zero(len(mul_cmds)+1))

        res_cmds.extend(mul_cmds)
        res_cmds.extend(self.load_address(res_mem_address))

        self.p0.append(Value(0))

        return res_cmds
 
    def half(self):
        self.__clear_p0()
        return [Command("HALF")]


    def divide(self, v1, v2):
        vars = are_variables(v1, v2)
        if vars == -1:
            commands = self.set(v1 // v2)
        elif vars == 0:
            operation = Operation(str(v1) + " / " + str(v2))
            if CompManager.optimization and self.__is_in_p0(operation):
                return []
            commands = self.divide_var_val(v1, v2)
            self.__clear_p0()
            self.p0.append(operation)
        elif vars == 1:
            operation = Operation(str(v1) + " / " + str(v2))
            if CompManager.optimization and self.__is_in_p0(operation):
                return []
            commands = self.divide_val_var(v1, v2)
            self.__clear_p0()
            self.p0.append(operation)
        else:
            operation = Operation(str(v1) + " / " + str(v2))
            if CompManager.optimization and self.__is_in_p0(operation):
                return []
            commands = self.divide_var_var(v1, v2)
            self.__clear_p0()
            self.p0.append(operation)
        return commands
    
    def divide_var_val(self, var_name, val):
        if val == 0:
            return self.set(0)
        is_power, power = isPowerOfTwo(val)
        if is_power:
            res_cmds = self.load(var_name)
            for i in range(power):
                res_cmds.extend(self.half())
            return res_cmds
        var = self.__get_variable(var_name)
        res_cmds = self.__init_static_var(val)
        res_cmds.extend(self.__divide_var_var(var.memory_address, self.static_vars[val], var.is_reference, False))
        return res_cmds
    
    def divide_val_var(self, val, var_name):
        if val == 0:
            return self.set(0)
        var = self.__get_variable(var_name)
        res_cmds = self.__init_static_var(val)
        res_cmds.extend(self.__divide_var_var(self.static_vars[val], var.memory_address, False, var.is_reference))
        return res_cmds
    
    def divide_var_var(self, var_name0, var_name1):
        var0 = self.__get_variable(var_name0)
        var1 = self.__get_variable(var_name1)
        return self.__divide_var_var(var0.memory_address, var1.memory_address, var0.is_reference, var1.is_reference)

    def __divide_var_var(self, mem_address0, mem_address1, is_ref0 = False, is_ref1 = False):
        # TODO check if value in mem_adress1 is 0 or 1 or 2
        init_cmds1 = self.__init_static_var(1)

        init_cmds1.extend(self.set(0))
        res_mem_address, cmds = self.store_act()
        init_cmds1.extend(cmds)

        if is_ref1:
            init_cmds1.extend(self.load_i_address(mem_address1))
        else:
            init_cmds1.extend(self.load_address(mem_address1))

        init_cmds0 = []

        act_mem_address1, store_cmds1 = self.store_act()
        init_cmds0.extend(store_cmds1)

        if is_ref0:
            init_cmds0.extend(self.load_i_address(mem_address0))
        else:
            init_cmds0.extend(self.load_address(mem_address0))

        tmp_res_cmds = []

        act_mem_address0, store_cmds0 = self.store_act()
        tmp_res_cmds.extend(store_cmds0)

        tmp_res_cmds.extend(self.set(1))
        act_mem_address2, store_cmds2 = self.store_act()
        tmp_res_cmds.extend(store_cmds2)

        inc_cmds = []

        inc_cmds.extend(self.load_address(act_mem_address2))
        inc_cmds.extend(self.__add_address(act_mem_address2))
        inc_cmds.extend(self.store_address(act_mem_address2))
        self.__clear_p0()

        inc_cmds.extend(self.load_address(act_mem_address1))
        inc_cmds.extend(self.__add_address(act_mem_address1))
        inc_cmds.extend(self.store_address(act_mem_address1))
        inc_cmds.extend(self.__sub_address(act_mem_address0))
        self.__clear_p0()

        tmp_res_cmds.extend(inc_cmds)
        tmp_res_cmds.extend(self.jump_zero(-len(inc_cmds)))

        div_cmds = []
        div_cmds.extend(self.load_address(act_mem_address1))
        div_cmds.extend(self.__sub_address(act_mem_address0))
        self.__clear_p0()

        div_cmds2 = []
        div_cmds2.extend(self.load_address(act_mem_address0))
        div_cmds2.extend(self.__sub_address(act_mem_address1))
        div_cmds2.extend(self.store_address(act_mem_address0))
        self.__clear_p0()

        div_cmds2.extend(self.load_address(res_mem_address))
        div_cmds2.extend(self.__add_address(act_mem_address2))
        div_cmds2.extend(self.store_address(res_mem_address))

        div_cmds.extend(self.jump_pos(len(div_cmds2) + 1))
        div_cmds.extend(div_cmds2)
        self.__clear_p0()

        div_cmds3 = []
        div_cmds3.extend(self.load_address(act_mem_address2))
        div_cmds3.extend(self.half())
        div_cmds3.extend(self.store_address(act_mem_address2))
        self.__clear_p0()


        div_cmds_cont = []
        div_cmds_cont.extend(self.load_address(act_mem_address1))
        div_cmds_cont.extend(self.half())
        div_cmds_cont.extend(self.store_address(act_mem_address1))
        # Change 1 to another value if jump_zero will not be in 1 line
        div_cmds_cont.extend(self.jump(-len(div_cmds) - len(div_cmds3) - len(div_cmds_cont) - 1))
        self.__clear_p0()

        div_cmds3.extend(self.jump_zero(len(div_cmds_cont) + 1))

        div_cmds.extend(div_cmds3)
        div_cmds.extend(div_cmds_cont)

        tmp_res_cmds.extend(div_cmds)
        tmp_res_cmds.extend(self.load_address(res_mem_address))
        self.__clear_p0()

        # check if values of var0 and var1 are 0, 1, 2 (if yes then jump to the end)
        res_cmds = []

        res_cmds.extend(init_cmds1)
        # add 1 this jump, add 1 load, 
        res_cmds.extend(self.jump_zero(len(tmp_res_cmds) + len(init_cmds0) + 1 + 1))

        if is_ref1:
            res_cmds.extend(self.load_i_address(mem_address1))
        else:
            res_cmds.extend(self.load_address(mem_address1))
        self.__clear_p0()

        res_cmds.extend(init_cmds0)
        res_cmds.extend(tmp_res_cmds)


        return res_cmds


    def modulo(self, v1, v2):
        vars = are_variables(v1, v2)
        if vars == -1:
            commands = self.set(v1 % v2)
        elif vars == 0:
            operation = Operation(str(v1) + " % " + str(v2))
            if CompManager.optimization and self.__is_in_p0(operation):
                return []
            commands = self.modulo_var_val(v1, v2)
            self.__clear_p0()
            self.p0.append(operation)
        elif vars == 1:
            operation = Operation(str(v1) + " % " + str(v2))
            if CompManager.optimization and self.__is_in_p0(operation):
                return []
            commands = self.modulo_val_var(v1, v2)
            self.__clear_p0()
            self.p0.append(operation)
        else:
            operation = Operation(str(v1) + " % " + str(v2))
            if CompManager.optimization and self.__is_in_p0(operation):
                return []
            commands = self.modulo_var_var(v1, v2)
            self.__clear_p0()
            self.p0.append(operation)
        return commands
    
    def modulo_var_val(self, var_name, val):
        if val == 0 or val == 1:
            return self.set(0)
        if val == 2:
            res_cmds = self.__init_static_var(1)
            res_cmds.extend(self.load(var_name))
            res_cmds.extend(self.__add_address(self.static_vars[1]))
            res_cmds.extend(self.half())
            res_cmds.extend(self.__add_address(0))
            var = self.__get_variable(var_name)
            res_cmds.extend(self.__sub(var))
            return res_cmds
        var = self.__get_variable(var_name)
        res_cmds = self.__init_static_var(val)
        res_cmds.extend(self.__modulo_var_var(var.memory_address, self.static_vars[val], var.is_reference, False))
        return res_cmds
    
    def modulo_val_var(self, val, var_name):
        if val == 0:
            return self.set(0)
        var = self.__get_variable(var_name)
        res_cmds = self.__init_static_var(val)
        res_cmds.extend(self.__modulo_var_var(self.static_vars[val], var.memory_address, False, var.is_reference))
        return res_cmds
    
    def modulo_var_var(self, var_name0, var_name1):
        var0 = self.__get_variable(var_name0)
        var1 = self.__get_variable(var_name1)
        return self.__modulo_var_var(var0.memory_address, var1.memory_address, var0.is_reference, var1.is_reference)

    def __modulo_var_var(self, mem_address0, mem_address1, is_ref0 = False, is_ref1 = False):
        # TODO check if value in mem_adress1 is 0 or 1 or 2
        init_cmds1 = self.__init_static_var(1)

        init_cmds1.extend(self.set(0))
        res_mem_address, cmds = self.store_act()
        init_cmds1.extend(cmds)

        if is_ref1:
            init_cmds1.extend(self.load_i_address(mem_address1))
        else:
            init_cmds1.extend(self.load_address(mem_address1))

        init_cmds0 = []

        act_mem_address1, store_cmds1 = self.store_act()
        init_cmds0.extend(store_cmds1)

        if is_ref0:
            init_cmds0.extend(self.load_i_address(mem_address0))
        else:
            init_cmds0.extend(self.load_address(mem_address0))

        tmp_res_cmds = []

        act_mem_address0, store_cmds0 = self.store_act()
        tmp_res_cmds.extend(store_cmds0)

        tmp_res_cmds.extend(self.set(1))
        act_mem_address2, store_cmds2 = self.store_act()
        tmp_res_cmds.extend(store_cmds2)

        inc_cmds = []

        inc_cmds.extend(self.load_address(act_mem_address2))
        inc_cmds.extend(self.__add_address(act_mem_address2))
        inc_cmds.extend(self.store_address(act_mem_address2))
        self.__clear_p0()

        inc_cmds.extend(self.load_address(act_mem_address1))
        inc_cmds.extend(self.__add_address(act_mem_address1))
        inc_cmds.extend(self.store_address(act_mem_address1))
        inc_cmds.extend(self.__sub_address(act_mem_address0))
        self.__clear_p0()

        tmp_res_cmds.extend(inc_cmds)
        tmp_res_cmds.extend(self.jump_zero(-len(inc_cmds)))

        div_cmds = []
        div_cmds.extend(self.load_address(act_mem_address1))
        div_cmds.extend(self.__sub_address(act_mem_address0))
        self.__clear_p0()

        div_cmds2 = []
        div_cmds2.extend(self.load_address(act_mem_address0))
        div_cmds2.extend(self.__sub_address(act_mem_address1))
        div_cmds2.extend(self.store_address(act_mem_address0))
        self.__clear_p0()

        div_cmds2.extend(self.load_address(res_mem_address))
        div_cmds2.extend(self.__add_address(act_mem_address2))
        div_cmds2.extend(self.store_address(res_mem_address))

        div_cmds.extend(self.jump_pos(len(div_cmds2) + 1))
        div_cmds.extend(div_cmds2)
        self.__clear_p0()

        div_cmds3 = []
        div_cmds3.extend(self.load_address(act_mem_address2))
        div_cmds3.extend(self.half())
        div_cmds3.extend(self.store_address(act_mem_address2))
        self.__clear_p0()


        div_cmds_cont = []
        div_cmds_cont.extend(self.load_address(act_mem_address1))
        div_cmds_cont.extend(self.half())
        div_cmds_cont.extend(self.store_address(act_mem_address1))
        # Change 1 to another value if jump_zero will not be in 1 line
        div_cmds_cont.extend(self.jump(-len(div_cmds) - len(div_cmds3) - len(div_cmds_cont) - 1))
        self.__clear_p0()

        div_cmds3.extend(self.jump_zero(len(div_cmds_cont) + 1))

        div_cmds.extend(div_cmds3)
        div_cmds.extend(div_cmds_cont)

        tmp_res_cmds.extend(div_cmds)
        tmp_res_cmds.extend(self.load_address(act_mem_address0))
        self.__clear_p0()

        res_cmds = []

        res_cmds.extend(init_cmds1)
        # add 1 this jump, add 1 load, 
        res_cmds.extend(self.jump_zero(len(tmp_res_cmds) + len(init_cmds0) + 1 + 1))

        if is_ref1:
            res_cmds.extend(self.load_i_address(mem_address1))
        else:
            res_cmds.extend(self.load_address(mem_address1))
        self.__clear_p0()

        res_cmds.extend(init_cmds0)
        res_cmds.extend(tmp_res_cmds)

        return res_cmds

    def jump(self, add_index):
        return [Command("JUMP", add_index)]

    def jump_address(self, address):
        return [Command(f"JUMP {address}")]

    def jump_zero(self, add_index):
        return [Command("JZERO", add_index)]

    def jump_pos(self, add_index):
        return [Command("JPOS", add_index)]

    def jump_i_address(self, address):
        return [Command(f"JUMPI {address}")]


    def equal(self, v0, v1, ret_val):
        vars = are_variables(v0, v1)
        if vars == 0 and v1 == 0:
            return ret_val, self.load(v0)
        if vars == 1 and v0 == 0:
            return ret_val, self.load(v1)
        cmds = self.substract(v0, v1)
        cmds2 = self.substract(v1, v0)
        cmds.extend(self.jump_pos(len(cmds2) + 1))
        cmds.extend(cmds2)
        return ret_val, cmds

    def greater_than(self, v0, v1, ret_val):
        vars = are_variables(v0, v1)
        if vars == 1 and v0 == 1:
            return self.equal(v1, 0, 1-ret_val)
        return ret_val, self.substract(v0, v1)

    def __init_static_var(self, val):
        if val in self.static_vars:
            return []
        cmds = self.set(val)
        mem_address, store_cmds = self.store_act()
        self.static_vars[val] = mem_address
        cmds.extend(store_cmds)
        return cmds

    def __clear_p0(self):
        self.p0 = []
    
    def __var_changed(self, var):
        if type(var) == str:
            var = self.__get_variable(var)
        new_p0 = []
        for el in self.p0:
            if type(el) == Operation:
                if el.contains(var):
                    continue
            new_p0.append(el)
        self.p0 = new_p0
    
    def __is_in_p0(self, val):
        for el in self.p0:
            if type(el) == type(val) and el == val:
                return True
        return False

    def __get_variable(self, name):
        for var in self.variables:
            if var.name == name:
                return var
        raise VariableNotFoundException(f"Variable with name {name} was not defined.")

    def __get_procedure(self, name):
        for proc in self.procedures:
            if proc.name == name:
                return proc
        raise VariableNotFoundException(f"Procedure with name {name} was not defined.")

