class PostBlock:

    def __init__(self, id: int, start: int, end: int, cmds: list[str]) -> None:
        self.id : int = id
        self.start : int = start
        self.end : int = end
        self.cmds : list[str] = cmds
        self.next1 : PostBlock = None
        self.next2 : PostBlock = None
        self.last = False
        self.removed_lines = 0
        self.to_remove = False

    def set_nexts(self, blocks : list["PostBlock"]):
        last_cmd = self.cmds[len(self.cmds) - 1]
        if "JUMP" in last_cmd and "JUMPI" not in last_cmd:
            self.next1 = blocks[get_cmd_index(last_cmd)]
        elif "JZERO" in last_cmd:
            self.next1 = blocks[get_cmd_index(last_cmd)]
            self.next2 = blocks[self.end + 1]
        elif "JPOS" in last_cmd:
            self.next2 = blocks[get_cmd_index(last_cmd)]
            self.next1 = blocks[self.end + 1]
        elif "HALT" in last_cmd:
            self.last = True
        elif "JUMPI" not in last_cmd:
            self.next1 = blocks[self.end + 1]

    def remove_unused_stores(self):
        i = 0
        act_index = -1
        last_index = -1
        while i < len(self.cmds):
            cmd = self.cmds[i]

            if "GET" in cmd:
                ind = get_cmd_index(cmd)
                if ind == act_index:
                    del self.cmds[last_index]
                    self.removed_lines += 1
                    act_index = -1
                    last_index = -1
                    continue
            
            if "LOAD" in cmd or "ADD" in cmd or "SUB" in cmd:
                ind = get_cmd_index(cmd)
                if ind == act_index:
                    act_index = -1
                    i += 1
                    continue
            
            if "LOADI" in cmd or "STOREI" in cmd or "ADDI" in cmd or "SUBI" in cmd:
                act_index = -1
                i += 1
                continue
                
            if "STORE" in cmd:
                index = get_cmd_index(cmd)
                if index == act_index:
                    del self.cmds[last_index]
                    self.removed_lines += 1
                    last_index = i - 1
                    continue
                else:
                    act_index = index
                    last_index = i
            
            
            i += 1

    def move_up_cmds(self, index_map: dict[int, int]):
        last = len(self.cmds) - 1
        last_cmd = self.cmds[last]
        if "JUMPI" in last_cmd:
            return
        for l in ["JUMP", "JZERO", "JPOS"]:
            if l in last_cmd:
                index = get_cmd_index(last_cmd)
                index = index_map[index]
                self.cmds[last] = f"{l} {index}" 
                break

    def has_same_cmds(self, obj: "PostBlock"):
        if not (self.next1 == obj.next1 and self.next2 == obj.next2):
            return False
        if (n1 := len(self.cmds)) == (n2 := len(obj.cmds)):
            compare_cmds(self.cmds, obj.cmds)
        elif n1 == n2 + 1:
            for l in ["JUMP", "JZERO", "JPOS"]:
                if l in self.cmds[n1 - 1]:
                    return compare_cmds(self.cmds[:-1], obj.cmds)
        elif n1 == n2 - 1:
            for l in ["JUMP", "JZERO", "JPOS"]:
                if l in obj.cmds[n2 - 1]:
                    return compare_cmds(self.cmds, obj.cmds[:-1])
        return False
    
    def replace_jump1(self, obj: "PostBlock"):
        last = len(self.cmds) - 1
        self.next1 = obj
        if self.next1 == self.next2:
            self.cmds[last] = f"JUMP {obj.start}"
            return
        last_cmd = self.cmds[last]
        if "JUMP" in last_cmd:
            self.cmds[last] = f"JUMP {obj.start}"
        elif "JZERO" in last_cmd:
            self.cmds[last] = f"JZERO {obj.start}"
        else:
            self.cmds.append(f"JUMP {obj.start}")
            self.removed_lines -= 1
    
    def replace_jump2(self, obj: "PostBlock"):
        last = len(self.cmds) - 1
        self.next2 = obj
        if self.next1 == self.next2:
            self.cmds[last] = f"JUMP {obj.start}"
            return
        last_cmd = self.cmds[last]
        if "JUMP" in last_cmd:
            self.cmds[last] = f"JUMP {obj.start}"
        elif "JPOS" in last_cmd:
            self.cmds[last] = f"JPOS {obj.start}"
        else:
            self.cmds.append(f"JUMP {obj.start}")
            self.removed_lines -= 1

    def remove_unused_jumps(self):
        last_cmd = self.cmds[len(self.cmds) - 1]
        if "JUMP" in last_cmd and "JUMPI" not in last_cmd:
            index = get_cmd_index(last_cmd)
            if index == self.start + len(self.cmds):
                del self.cmds[len(self.cmds) - 1]
                self.removed_lines += 1
    
    def remove_unused_cmds_before_set(self):
        i = len(self.cmds) - 1
        index_to_remove = []
        while i >= 0:
            if "SET" in self.cmds[i] or "LOAD" in self.cmds[i] or "LOADI" in self.cmds[i]:
                j = i - 1
                while j >= 0:
                    if "SET" in self.cmds[j] or "ADD" in self.cmds[j] or "SUB" in self.cmds[j] \
                        or "HALF" in self.cmds[0]:
                        index_to_remove.append(j)
                    if "STORE" in self.cmds[j] or "STOREI" in self.cmds[0]:
                        break
                    j -= 1
            i -= 1
        index_to_remove = list(set(index_to_remove))
        self.removed_lines += len(index_to_remove)
        for i in reversed(sorted(index_to_remove)):
            del self.cmds[i]

    def __eq__(self, __o: object) -> bool:
        return __o is not None and self.id == __o.id

def get_cmd_index(cmd):
    return int(cmd.split(" ")[1])

def compare_cmds(cmds1: list[str], cmds2: list[str]):
    # asserts that len of cmds1 and cmds2 are the same
    for i in range(len(cmds1)):
        if cmds1[i] != cmds2[i]:
            return False
    return True
