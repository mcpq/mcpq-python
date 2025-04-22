from mcpq import NBT, Block, Entity, Event, MCPQError, Minecraft, Player, Vec3, World


def test_annotate_imports():
    # to mark imports as used
    (Entity, Event, MCPQError, Minecraft, Player, Vec3, World, NBT, Block)


def test_mc_creation():
    mc = Minecraft()
    assert mc.host == "localhost"
    name = "AnyPlayer"
    p = mc.getOfflinePlayer(name)
    assert p
    assert p.name == p.id == name
