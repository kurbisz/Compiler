from CompExceptions import VariableNotFoundException
from CompUtils import *


class CompManager:

    def __init__(self) -> None:
        self.__output_codes = []
        self.act_val_memory_adress = 1
        self.variables = []

    def add_declaration(self, name):
        new_var = Variable(name, self.act_val_memory_adress)
        self.variables.append(new_var)
        self.act_val_memory_adress += 1
    
    def read(self, name):
        var = self.__get_variable(name)
        self.__output_codes.append(f"GET {var.memory_adress}")

    def set(self, val):
        self.__output_codes.append(f"SET {val}")

    def load(self, name):
        var = self.__get_variable(name)
        self.__output_codes.append(f"LOAD {var.memory_adress}")
    
    def store(self, name):
        var = self.__get_variable(name)
        self.__output_codes.append(f"STORE {var.memory_adress}")

    def write_value(self, val):
        self.set(val)
        self.__output_codes.append("PUT 0")

    def write(self, name):
        var = self.__get_variable(name)
        self.__output_codes.append(f"PUT {var.memory_adress}")

    def addVarToVal(self, var_name, val):
        var = self.__get_variable(var_name)
        self.set(val)
        self.__addVar(var)
    
    def addVarToVar(self, var_name0, var_name1):
        var0 = self.__get_variable(var_name0)
        var1 = self.__get_variable(var_name1)
        self.load(var_name0)
        self.__addVar(var1)
    
    def __addVar(self, var: Variable):
        self.__output_codes.append(f"ADD {var.memory_adress}")


    def get_output_codes(self):
        return self.__output_codes

    def __get_variable(self, name):
        for var in self.variables:
            if var.name == name:
                return var
        raise VariableNotFoundException(f"Variable with name {name} was not defined.")
