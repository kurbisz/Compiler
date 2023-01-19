class Variable:

    def __init__(self, name, memory_address, is_reference = False) -> None:
        self.name = name
        self.memory_address = memory_address
        self.is_reference = is_reference
        self.defined = False
    
    def set_defined(self, defined: bool):
        self.defined = defined

    def __str__(self) -> str:
        return r"VAR\{" + self.name + r"\}"

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

class Address:
    def __init__(self, address: int) -> None:
        self.address = address
    def __eq__(self, __o: object) -> bool:
        return self.address == __o.address
class IAddress:
    def __init__(self, address: int) -> None:
        self.address = address
    def __eq__(self, __o: object) -> bool:
        return self.address == __o.address

class Value:
    def __init__(self, val: int) -> None:
        self.val = val
    def __eq__(self, __o: object) -> bool:
        return self.val == __o.val
class Operation:
    def __init__(self, operation: str) -> None:
        self.operation = " " + operation + " "

    def contains(self, var: Variable):
        if type(var) == Variable:
            return (" " + var.name + " ") in self.operation
        return (" " + var + " ") in self.operation

    def __eq__(self, __o: object) -> bool:
        return self.operation == __o.operation


class PreStore:

    min_am = 3

    def __init__(self) -> None:
        self.mul_am = 0
        self.div_am = 0
        self.mod_am = 0
        self.mul_cost = 0
        self.proc_names : dict[str, PreProcedure] = {}
        self.numbers : list[int] = []

class PreProcedure:

    def __init__(self, declarations: str) -> None:
        self.cmds : str = ""
        self.used_times = 0
        self.declarations = declarations.split(" , ")
        self.var_declarations = []


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

def move_to_procedure(c, a, b):
    if c == "*":
        if is_i(a) and is_i(b):
            return not int(a) * int(b) <= maxLongLong
        elif is_i(a) and not is_i(b):
            return not isPowerOfTwo(int(a))
        elif not is_i(a) and is_i(b):
            return not isPowerOfTwo(int(b))
        return True
    elif c == "/":
        if is_i(a) and is_i(b):
            return False
        elif is_i(a) and not is_i(b):
            return int(a) not in [0, 1]
        elif not is_i(a) and is_i(b):
            return not isPowerOfTwo(int(b))
        return True
    # elif c == "%"
    if is_i(a) and is_i(b):
        return False
    elif is_i(a) and not is_i(b):
        return int(a) not in [0, 1]
    elif not is_i(a) and is_i(b):
        return int(b) not in [0, 1, 2]
    return True

def sum_var_dicts(dict1, dict2):
    res = {key: value for key, value in dict2.items()}
    for key in dict1:
        if key in dict2:
            if dict1[key] == True or dict2[key] == True:
                res[key] = True
            else:
                res[key] = dict1[key] + dict2[key]
        else:
            res[key] = dict1[key]
    return res

def is_i(a):
    return (type(a) == int or a.isnumeric())


maxLongLong = 9223372036854775807