class PostBlock:

    def __init__(self, start: int, end: int, cmds: list[str]) -> None:
        self.start : int = start
        self.end : int = end
        self.cmds : list[str] = cmds
        self.next1 : PostBlock = None
        self.next2 : PostBlock = None
        self.last = False
        self.removed_lines = 0

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

def get_cmd_index(cmd):
    return int(cmd.split(" ")[1])