class Variable:

    def __init__(self, name, memory_adress) -> None:
        self.name = name
        self.memory_adress = memory_adress

class Command:
    def __init__(self, cmd, add_index = None) -> None:
        self.cmd = cmd
        self.add_index = add_index
    
    def get_value(self, act_index):
        if self.add_index is not None:
            return f"{self.cmd} {act_index + self.add_index}"
        return self.cmd
        

def is_int(var):
    return type(var) == int

def are_variables(val0, val1):
    if is_int(val0) and is_int(val1):
        return -1
    if not is_int(val0) and is_int(val1):
        return 0
    if is_int(val0) and not is_int(val1):
        return 1
    return 2