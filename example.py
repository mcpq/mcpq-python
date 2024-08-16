from mcpq import Minecraft, Vec3

mc = Minecraft()  # connect to server on localhost

mc.postToChat("Hello Minecraft!")
pos = Vec3(0, 0, 0)  # origin of world, coordinates x, y and z = 0
block = mc.getBlock(pos)  # get block at origin
mc.setBlock("obsidian", pos)  # replace block with obsidian
mc.postToChat("Replaced", block, "with obsidian at", pos)
