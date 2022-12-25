


from PostUtils import PostBlock, get_cmd_index


class PostManager:

    def optimize(self, cmds: list[str]):

        blocks_list : list[PostBlock] = []

        def apply_to_blocks(new_inds : dict[int, int]):
            for block in blocks_list:
                block.move_up_cmds(new_inds)
                block.removed_lines = 0


        def init_blocks_list(cmds: list[str]):
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
            blocks_list.clear()

            last = 0


            # Initialize dict and list

            for i in range(len(start_jumps)):
                index = start_jumps[i]
                if index == 0:
                    continue
                block = PostBlock(i, last, index-1, cmds[last:index])
                blocks[last] = block
                blocks_list.append(block)
                last = index
            blocks[last] = PostBlock(len(start_jumps), last, len(cmds) - 1, cmds[last:])
            blocks_list.append(blocks[last])
            
            for block in blocks_list:
                block.set_nexts(blocks)

        init_blocks_list(cmds)


        # Remove unnecessary STOREs

        def remove_stores():
            am = 0
            new_inds : dict[int, int] = {}
            for block in blocks_list:
                block.remove_unused_stores()
                new_inds[block.start] = block.start - am
                block.start -= am
                am += block.removed_lines

            apply_to_blocks(new_inds)
        
        remove_stores()


        # Init previous blocks

        for block in blocks_list:
            block.init_previous_for_nexts()

        for block in blocks_list:
            block.set_start_val_for_nexts()


        # Remove SET at the beggining of the block if it had only 1 previous block with certain result
        
        am = 0
        new_inds = {}
        for block in blocks_list:
            block.replace_start_sets()
            new_inds[block.start] = block.start - am
            block.start -= am
            am += block.removed_lines
        

        apply_to_blocks(new_inds)


        # Remove blocks which are duplicates

        replace_blocks : dict[int, PostBlock] = {}

        for block in blocks_list:
            if block.next1 is not None and block.next2 is not None:
                if block.next1.id in replace_blocks.keys() or \
                     block.next2.id in replace_blocks.keys():
                    continue
                if block.next1.has_same_cmds(block.next2):
                    block.next2.to_remove = True
                    replace_blocks[block.next2.id] = block.next1

        for block in blocks_list:
            while block.next1 is not None and block.next1.id in replace_blocks.keys():
                block.replace_jump1(replace_blocks[block.next1.id])

            while block.next2 is not None and block.next2.id in replace_blocks.keys():
                block.replace_jump2(replace_blocks[block.next2.id])

        am = 0
        new_inds = {}
        for block in blocks_list:
            if block.to_remove:
                am += len(block.cmds)
            else:
                new_inds[block.start] = block.start - am
                block.start -= am
                am += block.removed_lines

        
        apply_to_blocks(new_inds)
        

        # Remove unnecessary jumps

        am = 0
        new_inds : dict[int, int] = {}
        for block in blocks_list:
            if not block.to_remove:
                block.remove_unused_jumps()
                new_inds[block.start] = block.start - am
                block.start -= am
                am += block.removed_lines

        
        apply_to_blocks(new_inds)
        

        # Create list of new commands

        new_cmds = []
        
        def create_new_cmds():
            new_cmds.clear()
            for block in blocks_list:
                if not block.to_remove:
                    new_cmds.extend(block.cmds)

        create_new_cmds()

        init_blocks_list(new_cmds)

        remove_stores()


        # Remove commands which are before SET (after removing IF ELSE)

        am = 0
        new_inds : dict[int, int] = {}
        for block in blocks_list:
            if not block.to_remove:
                block.remove_unused_cmds_before_set()
                new_inds[block.start] = block.start - am
                block.start -= am
                am += block.removed_lines

        apply_to_blocks(new_inds)

        create_new_cmds()
            

        # Replace SETI with appropriate SET

        for i in range(len(new_cmds)):
            if new_cmds[i] == "SETI":
                new_cmds[i] = f"SET {i+3}"

        return new_cmds

