"""This module contains integration tests.
They connect to a real server (use a test server) and expect a player online.
The intent is to test most available functions and try them in some specified way.
These tests are not exhaustive about the possible applications but should cover
most of the available functions at least once.

With the package `pytest-integration` run pytest with `pytest --without-integration` to skip integration tests.
"""

from time import sleep

import grpc
import pytest

import mcpq
from mcpq import NBT, Minecraft, PlayerNotFound, Vec3, WorldNotFound


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
    ps = mc.getPlayerList()
    if len(ps) == 0:
        pytest.skip("No players on Server, cannot run player test")
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
        mc.getPlayerList([p.name, "thisplayerdoesnotexistontheserver"])
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
    sleep(0.2)  # setBlock nonblocking
    assert (new_block_ret := mc.getBlock(origin)) == new_block
    assert ow.getBlock(origin) == new_block, "Default world should almost always be overworld"
    assert mc.nether.getBlock(origin) != new_block

    assert hasattr(new_block_ret, "id")
    assert not new_block_ret.getData()
    assert (
        new_block_ret_data := mc.getBlockWithData(origin)
    ) == new_block, "equals check should still succeed even with data"
    assert new_block_ret_data.getData(), "expected block to have data/components"

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


@pytest.mark.integration_test
def test_entity(mc):
    mcversion = mc.getMinecraftVersionTuple()
    etype = "cow"  # hostile behaves differently
    mc.removeEntities(etype)
    spawn = Vec3().up(1000)
    mc.getBlock(spawn)
    mc.runCommandBlocking("setworldspawn 0 0 0 150")  # to load chunks there
    e = mc.spawnEntity(etype, spawn)
    e.giveEffect("slow_falling", 9999, 5)
    assert e.type == etype, f"Not a {etype}, but {e}"
    if not e.loaded and mcversion == (1, 20, 5):
        pytest.skip("Entity cannot be loaded in empty world in 1.20.5")
    assert e.loaded, f"{etype} was not loaded"
    assert (
        last_dist := e.pos.distance(spawn)
    ) < 300, f"{etype} was at {e.pos}, far away from spawn at {spawn}"
    sleep(mcpq.entity.CACHE_ENTITY_TIME + 0.3)
    new_dist = e.pos.distance(spawn)
    if new_dist == last_dist and (1, 20) < mcversion <= (1, 21):
        # It seems like (on paper) versions 1.21 and older the entity
        # does not (always) fall ...
        print("Skipping over non falling entity position checks")
    else:
        assert new_dist > last_dist, f"{etype} did not fall at all {new_dist=} !> {last_dist=}"
        assert (
            last_dist + 50 > new_dist
        ), f"{etype} moved very far with slow falling {last_dist=} + 50 !> {new_dist=}"

    def check_execute(cmd: str):
        block_pos = Vec3().floor()
        initial_block = last_block = mc.getBlock(block_pos)
        new_block = "diamond_block" if last_block == "emerald_block" else "emerald_block"
        if cmd and (not cmd.startswith("execute") or not cmd.endswith("run")):
            raise ValueError(cmd)

        e.runCommandBlocking(
            (f"{cmd} " if cmd else "")
            + f"setblock {block_pos.x} {block_pos.y} {block_pos.z} {new_block}"
        )
        last_block = mc.getBlock(block_pos)
        mc.runCommandBlocking(
            f"setblock {block_pos.x} {block_pos.y} {block_pos.z} {initial_block}"
        )
        assert last_block == new_block, f"{cmd} failed or {e} did not exist"

    def getNbtData(entity) -> NBT:
        res: str = entity.runCommandBlocking("data get entity @s")
        if res:
            # supports vanilla return!
            # looks like: "type" has the following entity data: {...}
            # or like: no entity was found
            if "{" in res and "}" in res:
                nbt_string = res[res.index("{") : res.rindex("}")]
                return NBT.parse(nbt_string)
            print("No entity (nbt data) found")
            return NBT()
        print("runCommandBlocking not impl. for vanilla commands")
        return NBT()

    # check if entity is even there
    check_execute("")
    # check type of entity via command
    check_execute(f"execute as @e[type={e.type},limit=1,sort=nearest] run")
    nbt1 = NBT({"NoAI": "1b"})
    assert str(nbt1) == "{NoAI:1b}"
    nbt0 = NBT({"NoAI": "0b"})
    # check if "NoAI" is not set either way
    check_execute(f"execute as @s[nbt=!{nbt0}] run")
    check_execute(f"execute as @s[nbt=!{nbt1}] run")
    # set nbt data
    e.runCommandBlocking(f"data merge entity @s {nbt1}")
    # then check if set correctly
    check_execute(f"execute as @s[nbt=!{nbt0}] run")
    check_execute(f"execute as @s[nbt={nbt1}] run")

    e_nbt = getNbtData(e)
    if not e_nbt:
        print("runCommandBlocking not impl. for vanilla commands!")
    else:
        assert e_nbt.get("NoAI", None) is None
        effects = e_nbt["active_effects"]
        assert effects and any(
            ef["id"] == "minecraft:slow_falling" for ef in effects
        ), f"{effects=}"
        armor = e_nbt["ArmorItems"]
        assert len(armor) == 4, f"{armor=}"
        assert all(a == {} for a in armor), f"{armor=}"
        e.replaceHelmet(
            unbreakable=False, binding=False, vanishing=False, color=False
        )  # TODO: test enchants and color
        sleep(0.05)
        e_nbt = getNbtData()
        assert e_nbt
        armor = e_nbt["ArmorItems"]
        assert len(armor) == 4, f"{armor=}"
        assert not all(a == {} for a in armor), f"{armor=}"

    old_pos = e.pos
    assert len((es := mc.getEntitiesAround(old_pos, 5, etype))) == 1, f"{es}"
    e.pos = spawn = spawn.up(20)
    sleep(0.05)
    assert len((es := mc.getEntitiesAround(old_pos, 5, etype))) == 0, f"{es}"
    assert len((es := mc.getEntitiesAround(spawn, 5, etype))) == 1, f"{es}"

    e.remove()
    # e.runCommandBlocking("kill")
    # sleep(1)
    # e._update()
    # assert not e.loaded, f"{e} still exists"
