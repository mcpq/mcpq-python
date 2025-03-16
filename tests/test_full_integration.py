"""This module contains integration tests.
They connect to a real server (use a test server) and expect a player online.
The intent is to test most available functions and try them in some specified way.
These tests are not exhaustive about the possible applications but should cover
most of the available functions at least once.

With the package `pytest-integration` run pytest with `pytest --without-integration` to skip integration tests.
"""

from time import sleep

import grpc._channel
import pytest

from mcpq import (
    Entity,
    Event,
    MCPQError,
    Minecraft,
    Player,
    PlayerNotFound,
    Vec3,
    World,
    WorldNotFound,
)


@pytest.fixture
def mc():
    client = Minecraft()
    try:
        assert client.getMinecraftVersion()
    except grpc.RpcError:
        raise ConnectionError("Connection to server is required for integration tests")
    yield client
    client.events.stopEventPollingAndClearCallbacks()


@pytest.mark.integration_test
def test_player(mc):
    ps = mc.getPlayers()
    assert len(ps), "No players on Server, cannot run player test"
    mc.events.player_death.poll(None)  # activate
    # mc.events.player_leave.poll(None)  # activate

    p = mc.getPlayer()
    assert p
    assert p in ps
    assert p.type == "player"
    assert p.online
    assert p.name == p.id
    assert mc.getPlayer(p.name) is p
    assert mc.getOfflinePlayer(p.name) is p
    with pytest.raises(PlayerNotFound):
        mc.getPlayer("thisplayerdoesnotexistontheserver")
    with pytest.raises(PlayerNotFound):
        mc.getPlayers([p.name, "thisplayerdoesnotexistontheserver"])
    assert mc.getOfflinePlayer("thisplayerdoesnotexistontheserver")
    assert p.name in mc.getPlayerNames()
    orig_pos = p.pos
    assert p.pos != Vec3()
    p.pos = Vec3()
    assert p.pos == Vec3()
    orig_world = p.world
    assert p.world in mc.worlds
    other_world = next(w for w in mc.worlds if w != orig_world)
    p.world = other_world
    assert p.world is other_world
    orig_facing = p.facing
    p.facing = Vec3().east().south(12).norm()
    assert p.facing != orig_facing
    p.teleport(pos=orig_pos, world=orig_world, facing=orig_facing)
    assert p.pos == orig_pos
    assert p.world == orig_world
    with pytest.raises(Exception):
        p.remove()
    with pytest.raises(Exception):
        assert p.loaded
    # assert p.facing == orig_facing
    e = mc.spawnEntity("sheep", p.pos.up(1))
    assert e in p.getEntitiesAround(50)

    # not testable for the the moment
    p.gamemode("creative")
    p.adventure()
    p.survival()
    p.spectator()
    p.creative()
    p.op()

    p.giveItems("snowball", 64)
    p.giveEffect("glowing", 5)
    p.runCommand("clear")
    p.runCommandBlocking("clear")
    # and more...

    # testable events
    mc.runCommandBlocking("gamerule doImmediateRespawn true")
    mc.events.player_death.poll(None)  # clear
    p.kill()
    res = mc.events.player_death.get(1)
    assert res
    assert res.player == p

    # mc.events.player_leave.poll(None)  # clear
    # p.kick()
    # res = mc.events.player_leave.get(1)
    # assert res
    # assert res.player == p


@pytest.mark.integration_test
def test_world(mc):
    origin = Vec3()

    ow = mc.overworld
    assert mc.overworld in mc.worlds
    assert mc.nether in mc.worlds
    assert mc.end in mc.worlds
    with pytest.raises(WorldNotFound):
        mc.getWorldByKey("minecraft:not_this_world_here")
    with pytest.raises(WorldNotFound):
        mc.getWorldByName("not_this_world_here_folder_name")
    assert mc.getWorldByKey("minecraft:overworld") == mc.overworld
    assert mc.getWorldByKey("overworld") == mc.overworld
    assert mc.getWorldByName(ow.name) == ow
    assert mc.getWorldByKey(ow.key) == ow

    orig_block = mc.getBlock(origin)
    new_block = "birch_stairs" if orig_block == "spruce_stairs" else "spruce_stairs"
    assert orig_block != new_block
    mc.setBlock(new_block, origin)
    sleep(0.05)  # setBlock nonblocking
    assert (new_block_ret := mc.getBlock(origin)) == new_block
    assert ow.getBlock(origin) == new_block, "Default world should almost always be overworld"
    assert mc.nether.getBlock(origin) != new_block

    assert hasattr(new_block_ret, "id")
    assert not new_block_ret.getData()
    assert (
        new_block_ret_data := mc.getBlockWithData(origin)
    ) != new_block, "expected block to have data/components"
    assert new_block_ret_data.getData()

    # world.pvp = False  # disable pvp only in this world
    # ground_pos = world.getHeighestPos(0, 0)  # get position of heighest ground at origin
    # block = world.getBlock(ground_pos)  # get the block type there
    # world.setBlock("diamond_block", ground_pos)  # replace that block at location with diamond
    # # set every second block in a line along the x axis to emerald
    # world.setBlockList("emerald_block", [ground_pos.up(2).east(i) for i in range(0,20,2)])
    # # set a 10 x 10 x 10 oak plank block 50 blocks above ground
    # world.setBlockCube("oak_planks", ground_pos.up(50), ground_pos.up(50) + 9)
    # sheep = world.spawnEntity("sheep", ground_pos.up(1))  # spawn a sheep on that block
    # entities = world.getEntities()  # get all (loaded) entities
    # # get all  (loaded) entities around origin highest block in 20 block radius
    # entities = world.getEntitiesAround(ground_pos, 20)
    # world.removeEntities("sheep")  # remove all (loaded) sheep
    # # copy all blocks between those two points (inclusive)
    # blocks = world.copyBlockCube(Vec3(0,0,0), Vec3(5,5,5))
    # # paste back the copied blocks 20 blocks above origin ground
    # world.pasteBlockCube(blocks, ground_pos.up(20))
    # world.setBed(ground_pos.up(1))  # place a bed on top of diamond block

    mc.setBlock(orig_block, origin)
