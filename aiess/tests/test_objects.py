import pytest

from aiess.objects import User, Beatmapset, Discussion, Usergroup
from aiess.errors import ParsingError, DeletedContextError

from aiess.tests.mocks.api import beatmap as mock_beatmap
from aiess.tests.mocks.api import old_beatmap as mock_old_beatmap

def test_user():
    user = User(101, "Generic Name")

    assert user.id == "101"
    assert user.name == "Generic Name"
    assert user.__str__() == "Generic Name"

def test_user_no_name():
    user = User(2)

    assert user.id == "2"
    assert user.name == "peppy"
    assert user.__str__() == "peppy"

def test_user_restricted():
    user = User(1)

    assert user.id == "1"
    assert user.name == None
    assert user.__str__() == "1"

def test_beatmapset():
    beatmapset = Beatmapset(41823, beatmapset_json=mock_old_beatmap.JSON)

    assert beatmapset.id == "41823"
    assert beatmapset.artist == "The Quick Brown Fox"
    assert beatmapset.title == "The Big Black"
    assert beatmapset.creator.id == "19048"
    assert beatmapset.creator.name == "Blue Dragon"
    assert beatmapset.modes == ["osu", "taiko"]

    assert beatmapset.mode_str() == "[osu][taiko]"
    assert beatmapset.__str__() == "The Quick Brown Fox - The Big Black (mapped by Blue Dragon) [osu][taiko]"

def test_beatmapset_non_existent():
    with pytest.raises(DeletedContextError):
        Beatmapset(2, beatmapset_json="[]")

def test_old_discussion():
    beatmapset = Beatmapset(41823, beatmapset_json=mock_old_beatmap.JSON)
    discussion = Discussion(1234956, beatmapset)

    # No such discussion exists, but this should still work.
    assert discussion.id == "1234956"
    assert discussion.beatmapset == beatmapset

def test_discussion():
    beatmapset = Beatmapset(1001546, beatmapset_json=mock_beatmap.JSON)
    discussion = Discussion(1234956, beatmapset)

    assert discussion.id == "1234956"
    assert discussion.beatmapset == beatmapset

def test_usergroup():
    usergroup = Usergroup("4")

    assert usergroup.id == "4"
    assert usergroup.name == "Global Moderation Team"
