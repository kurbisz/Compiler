from CompExceptions import VariableNotFoundException
from CompUtils import *


class PreManager:

    def __init__(self) -> None:
        self.act_val_memory_address = 1
        self.variables = []
        self.static_vars = {}
        self.procedures = []

    def add_declaration(self, name, is_reference = False):
        new_var = Variable(name, self.act_val_memory_address, is_reference)
        self.variables.append(new_var)
        self.act_val_memory_address += 1
    