


from PostUtils import PostBlock, get_cmd_index


class PostManager:

    def optimize(self, cmds: list[str]):
        # list of indexes where we can jump
        start_jumps = []
        
        for i in range(len(cmds)):
            cmd = cmds[i]
            if "JUMP" in cmd:
                index = get_cmd_index(cmd)
                start_jumps.append(index)
            
            if "JZERO" in cmd or "JPOS" in cmd:
                index = get_cmd_index(cmd)
                start_jumps.append(index)
                start_jumps.append(i+1)
        
        start_jumps = list(set(start_jumps))
        start_jumps = sorted(start_jumps)
        
        blocks : dict[int, PostBlock] = {}
        blocks_list : list[PostBlock] = []

        last = 0

        for i in range(len(start_jumps)):
            index = start_jumps[i]
            if index == 0:
                continue
            block = PostBlock(last, index-1, cmds[last:index])
            blocks[last] = block
            blocks_list.append(block)
            last = index
        blocks[last] = PostBlock(last, len(cmds) - 1, cmds[last:])
        blocks_list.append(blocks[last])
        
        # for block in blocks_list:
        #     block.set_nexts(blocks)
        
        #TODO check if all stores/loads are essentials (program0.imp as example)

        am = 0
        new_inds : dict[int, int] = {}
        for block in blocks_list:
            block.remove_unused_stores()
            new_inds[block.start] = block.start - am
            am += block.removed_lines
        
        for block in blocks_list:
            block.move_up_cmds(new_inds)
        
        new_cmds = []
        for block in blocks_list:
            new_cmds.extend(block.cmds)


        return new_cmds

