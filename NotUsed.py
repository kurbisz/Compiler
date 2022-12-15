def multiplyVarVal(self, var_name, val):
    if val == 0:
        return self.set(0)
    res_cmds = self.set(0)
    res_mem_address, cmds = self.store_act()
    load_cmds = self.load(var_name)
    act_mem_address, store_cmds = self.store_act()
    res_cmds.extend(cmds)
    res_cmds.extend(load_cmds)
    res_cmds.extend(store_cmds)
    while val > 0:
        if val % 2 == 1:
            store_cmds = self.store_address(act_mem_address)
            load_cmds = self.load_address(res_mem_address)
            add_cmds = self.__add_address(act_mem_address)
            res_store_cmds = self.store_address(res_mem_address)
            act_load_cmds = self.load_address(act_mem_address)

            res_cmds.extend(store_cmds)
            res_cmds.extend(load_cmds)
            res_cmds.extend(add_cmds)
            res_cmds.extend(res_store_cmds)
            res_cmds.extend(act_load_cmds)
        
        multiply_cmds = self.__add_address(0)
        res_cmds.extend(multiply_cmds)
        val = val // 2

    load_cmds = self.load_address(res_mem_address)
    res_cmds.extend(load_cmds)
    return res_cmds 