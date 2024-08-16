from mcpq import Entity, Event, MCPQError, Minecraft, Player, Vec3, World


def test_mc_creation():
    mc = Minecraft()
    assert mc.host == "localhost"
    name = "AnyPlayer"
    p = mc.getOfflinePlayer(name)
    assert p
    assert p.name == p.id == name


def test_annotate_imports():
    # to mark imports as used
    mc = Minecraft
    e = Entity
    ev = Event
    exc = MCPQError
    p = Player
    v = Vec3
    w = World
