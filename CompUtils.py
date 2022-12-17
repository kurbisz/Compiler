class Variable:

    def __init__(self, name, memory_address, is_reference = False) -> None:
        self.name = name
        self.memory_address = memory_address
        self.is_reference = is_reference

class Procedure:
    def __init__(self, name, arguments: list[Variable], start_index: int, return_memory_adress: int) -> None:
        self.name = name
        self.arguments = arguments
        self.start_index = start_index
        self.return_memory_adress = return_memory_adress

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

def isPowerOfTwo(n):
    i = 0
    while (n != 1):
        if (n % 2 != 0):
            return False, 0
        n = n // 2
        i += 1
    return True, i