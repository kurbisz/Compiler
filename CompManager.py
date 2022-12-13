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
    
    def write_value(self, val):
        self.__output_codes.append(f"SET {val}")
        self.__output_codes.append("PUT 0")

    def write(self, name):
        var = self.__get_variable(name)
        self.__output_codes.append(f"PUT {var.memory_adress}")

    def get_output_codes(self):
        return self.__output_codes

    def __get_variable(self, name):
        for var in self.variables:
            if var.name == name:
                return var
        raise VariableNotFoundException(f"Variable with name {name} was not defined.")
