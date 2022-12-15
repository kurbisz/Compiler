from CompExceptions import VariableNotFoundException
from CompUtils import *


class CompManager:

    def __init__(self) -> None:
        self.act_val_memory_adress = 1
        self.variables = []

    def add_declaration(self, name):
        new_var = Variable(name, self.act_val_memory_adress)
        self.variables.append(new_var)
        self.act_val_memory_adress += 1
    

    def read(self, name):
        var = self.__get_variable(name)
        return [Command(f"GET {var.memory_adress}")]

    def write_value(self, val):
        res = self.set(val)
        res.append(Command("PUT 0"))
        return res

    def write(self, name):
        var = self.__get_variable(name)
        return [Command(f"PUT {var.memory_adress}")]


    def set(self, val):
        return [Command(f"SET {val}")]

    def load(self, name):
        var = self.__get_variable(name)
        return [Command(f"LOAD {var.memory_adress}")]
    
    def store(self, name):
        var = self.__get_variable(name)
        return [Command(f"STORE {var.memory_adress}")]

    def store_act(self) -> int:
        act = self.act_val_memory_adress
        self.act_val_memory_adress += 1
        return act, [Command(f"STORE {act}")]


    def addVarToVal(self, var_name, val):
        var = self.__get_variable(var_name)
        res = self.set(val)
        res.extend(self.__addVar(var))
        return res

    def addVarToVar(self, var_name0, var_name1):
        var1 = self.__get_variable(var_name1)
        res = self.load(var_name0)
        res.extend(self.__addVar(var1))
        return res
    
    def __addVar(self, var: Variable):
        return [Command(f"ADD {var.memory_adress}")]

    
    def subVarVal(self, var_name, val):
        res = self.set(val)
        mem_adress, cmds = self.store_act()
        res.extend(cmds)
        res.extend(self.load(var_name))
        res.extend(self.__subVar(mem_adress))
        return res

    def subValVar(self, val, var_name):
        var = self.__get_variable(var_name)
        res = self.set(val)
        res.extend(self.__subVar(var.memory_adress))
        return res
    
    def subVarVar(self, var_name0, var_name1):
        var1 = self.__get_variable(var_name1)
        res = self.load(var_name0)
        res.extend(self.__subVar(var1.memory_adress))
        return res

    def __subVar(self, memory_adress):
        return [Command(f"SUB {memory_adress}")]


    def __get_variable(self, name):
        for var in self.variables:
            if var.name == name:
                return var
        raise VariableNotFoundException(f"Variable with name {name} was not defined.")
