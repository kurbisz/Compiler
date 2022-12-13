class Variable:

    def __init__(self, name, memory_adress) -> None:
        self.name = name
        self.memory_adress = memory_adress

def is_int(var):
    return type(var) == int