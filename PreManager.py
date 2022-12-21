from CompExceptions import VariableNotFoundException
from CompUtils import *


class PreManager:

    def optimize_input(self, input: str, pre_store: PreStore):
        res = self.replace_vars_with_values(input)
        res = self.remove_unused_lines(res)
        res = self.move_operations_if_worth(res, pre_store)
        return res

    def replace_vars_with_values(self, input: str):
        l = input.split("\n")
        act = {}
        for i in range(len(l)):
            el = l[i]
            if "END" in el or "WHILE" in el or "ENDWHILE" in el or "REPEAT" in el or "UNTIL" in el or "(" in el:
                act = {}
                continue
            s = el.split(" ")
            if s[0] == "READ":
                if s[1] in act:
                    del act[spl[0]]
            if "IF" in el:
                for repl in act.keys():
                    l[i] = el.replace(" " + repl + " ", " " + str(act[repl]) + " ")
            if ":=" in el:
                for repl in act.keys():
                    l[i] = el.replace(" " + repl + " ", " " + str(act[repl]) + " ")
                spl = l[i].replace(" ", "").replace(";", "").split(":=")
                values = spl[1]
                try:
                    if "+" in values:
                        values = values.split("+")
                        res = int(values[0]) + int(values[1])
                    elif "-" in values:
                        values = values.split("-")
                        res = max(int(values[0]) - int(values[1]), 0)
                    elif "*" in values:
                        values = values.split("*")
                        res = int(values[0]) * int(values[1])
                    elif "/" in values:
                        values = values.split("/")
                        res = int(values[0]) // int(values[1])
                    elif "%" in values:
                        values = values.split("%")
                        res = int(values[0]) % int(values[1])
                    else:
                        res = int(values)
                except ValueError:
                    if spl[0] in act:
                        del act[spl[0]]
                    continue
                act[spl[0]] = res
        return "\n".join(l)
    
    def remove_unused_lines(self, input: str):
        l = input.split("\n")
        act = {}
        remove_lines = []
        for i in range(len(l)-1):
            el = l[i]
            if "END" in el or "WHILE" in el or "ENDWHILE" in el or "REPEAT" in el or "UNTIL" in el or "(" in el:
                act = {}
                continue
            s = el.split(" ")
            if s[0] == "READ":
                if s[1] in act:
                    del act[spl[0]]
            if ":=" in el:
                spl = l[i].replace(" ", "").replace(";", "").split(":=")
                values = spl[1]
                try:
                    if "+" in values:
                        values = values.split("+")
                        res = int(values[0]) + int(values[1])
                    elif "-" in values:
                        values = values.split("-")
                        res = max(int(values[0]) - int(values[1]), 0)
                    elif "*" in values:
                        values = values.split("*")
                        res = int(values[0]) * int(values[1])
                    elif "/" in values:
                        values = values.split("/")
                        res = int(values[0]) // int(values[1])
                    elif "%" in values:
                        values = values.split("%")
                        res = int(values[0]) % int(values[1])
                    else:
                        res = int(values)
                except ValueError:
                    if spl[0] in act:
                        del act[spl[0]]
                    continue
                if spl[0] in act:
                    remove_lines.append(act[spl[0]])
                act[spl[0]] = i
        for key in act.keys():
            remove_lines.append(act[key])
        remove_lines = sorted(remove_lines, reverse=True)
        for line_index in remove_lines:
            del l[line_index]
        return "\n".join(l)


    def move_operations_if_worth(self, s: str, pre_store: PreStore) -> str:
        res_str = []
        operations = {}
        if pre_store.mul_am >= PreStore.min_am:
            c = "*"
            proc_name = self.__proc_name("multiplication", pre_store.proc_names)
            operations[c] = proc_name
            res_str.append(self.__create_procedure(c, proc_name))
        if pre_store.div_am >= PreStore.min_am:
            c = "/"
            proc_name = self.__proc_name("division", pre_store.proc_names)
            operations[c] = proc_name
            res_str.append(self.__create_procedure(c, proc_name))
        if pre_store.mod_am >= PreStore.min_am:
            c = "%"
            proc_name = self.__proc_name("modulo", pre_store.proc_names)
            operations[c] = proc_name
            res_str.append(self.__create_procedure(c, proc_name))
        for line in s.split("\n"):
            end = False
            for operation in operations.keys():
                if operation in line:
                    spl = line.split(" ")
                    result = spl[0]
                    first = spl[2]
                    second = spl[4]
                    if move_to_procedure(operation, first, second):
                        res_str.append(line)
                    else:
                        res_str.append(operations[operation] + "(" + first + ", " + second + ", " + result + ") ;")
                    end = True
                    break
            if not end:
                res_str.append(line)
        return "\n".join(res_str)
    
    def __create_procedure(self, c, proc_name):
        proc = "PROCEDURE " + proc_name + "(a, b, c) IS\n"
        proc += "BEGIN\n"
        proc += "c := a " + c + " b ;\n"
        proc += "END\n"
        return proc
    
    def __proc_name(self, proc_name, proc_names):
        res_proc_name = proc_name
        while res_proc_name in proc_names:
            res_proc_name += "a"
        return res_proc_name
