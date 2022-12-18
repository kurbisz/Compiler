def optimize_input(input: str):
    res = replace_vars_with_values(input)
    res = remove_unused_lines(res)
    return res

def replace_vars_with_values(input: str):
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
    
def remove_unused_lines(input: str):
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