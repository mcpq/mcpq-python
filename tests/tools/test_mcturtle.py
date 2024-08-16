from unittest.mock import MagicMock, PropertyMock

import pytest
from pytest_mock import MockerFixture

from mcpq import Minecraft, Vec3, World
from mcpq.tools import Turtle

# see https://docs.python.org/3/library/unittest.mock.html#unittest.mock.PropertyMock


def test_init_wrong_mc():
    with pytest.raises(TypeError):
        Turtle(object())


def test_init_wrong_pos():
    mc = MagicMock(spec=Minecraft)
    assert isinstance(mc, Minecraft)

    with pytest.raises(TypeError):
        Turtle(mc, object())


def test_init_wrong_world():
    mc = MagicMock(spec=Minecraft)
    assert isinstance(mc, Minecraft)

    with pytest.raises(TypeError):
        Turtle(mc, Vec3(1, -2, 3), object())


@pytest.mark.skip(reason="should be adjusted after Turtle update")
def test_init_correct_all_provided():
    mc = MagicMock(spec=Minecraft)
    assert isinstance(mc, Minecraft)
    pos = Vec3(1, -2, 3)
    world = World(mc, mc, "minecraft:test", "my_test_world")

    # execute
    t = Turtle(mc, pos, world)

    # check
    assert t._mc is mc
    assert t._pos is pos
    assert t._world is world
    assert len(mc.mock_calls) == 2  # no mc.getPlayer() and one setBlock call
    assert not mc.getPlayer.called
    assert mc.setBlock.called or mc.setBlockIn.called


@pytest.mark.skip(reason="should be adjusted after Turtle update")
def test_init_create_new_instance_of_mc_get_pos_and_world_if_not_provided(
    mocker: MockerFixture,
):
    # setup
    mocked_mcclass = mocker.patch("mcpq.tools.mcturtle.Minecraft", spec=True)
    mc = MagicMock(spec=Minecraft)
    mocked_mcclass.return_value = mc
    assert isinstance(mc, Minecraft)
    mocked_player = MagicMock()
    mc.getPlayer.return_value = mocked_player
    pos = Vec3(1, -2, 3)
    mocked_pos = PropertyMock(return_value=pos)
    type(mocked_player).pos = mocked_pos
    world = "my_test_world"
    mocked_world = PropertyMock(return_value=world)
    type(mocked_player).world = mocked_world

    # execute
    t = Turtle()

    # check
    assert t._mc is mc
    assert t._pos == pos
    assert t._world == world
    mocked_mcclass.assert_called_once()
    mc.getPlayer.assert_called_once()
    assert mocked_pos.call_count == 1
    assert mocked_world.call_count == 1
    assert len(mc.mock_calls) == 2  # one mc.getPlayer() and one mc.setBlock call
    assert mc.getPlayer.called
    assert mc.setBlock.called or mc.setBlockIn.called
