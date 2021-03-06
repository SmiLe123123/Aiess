import sys
sys.path.append('..')

from bot.objects import Subscription
from bot.objects import Prefix
from bot.objects import CommandPermission

def test_sub_init_str_ids():
    sub = Subscription(guild_id="1", channel_id="3", _filter="type:nominate")
    assert sub.guild_id == 1
    assert sub.channel_id == 3

def test_sub_str():
    sub = Subscription(guild_id=1, channel_id=3, _filter="type:nominate")
    assert "\"type:nominate\"" in str(sub)
    assert "1" in str(sub)
    assert "3" in str(sub)

def test_sub_eq():
    sub1 = Subscription(guild_id=1, channel_id=3, _filter="type:nominate")
    sub2 = Subscription(guild_id=1, channel_id=3, _filter="type:nominate")
    sub3 = Subscription(guild_id=1, channel_id=4, _filter="type:nominate")
    assert sub1 == sub2
    assert sub1 != sub3

def test_sub_eq_type_mismatch():
    sub = Subscription(guild_id=1, channel_id=3, _filter="type:nominate")
    assert sub != "not a sub"

def test_sub_hash():
    sub = Subscription(guild_id=1, channel_id=3, _filter="type:nominate")
    assert sub.__hash__()



def test_prefix_init_str_id():
    prefix = Prefix(guild_id="1", prefix="&")
    assert prefix.guild_id == 1

def test_prefix_eq():
    prefix1 = Prefix(guild_id=1, prefix="&")
    prefix2 = Prefix(guild_id=1, prefix="&")
    prefix3 = Prefix(guild_id=3, prefix="&")
    assert prefix1 == prefix2
    assert prefix1 != prefix3

def test_prefix_eq_type_mismatch():
    prefix = Prefix(guild_id=1, prefix="&")
    assert prefix != "not a sub"

def test_prefix_hash():
    prefix = Prefix(guild_id=1, prefix="&")
    assert prefix.__hash__()



def test_permission_init_str_id():
    permission = CommandPermission(guild_id="1", command_name="test", permission_filter="filter")
    assert permission.guild_id == 1

def test_permission_eq():
    permission1 = CommandPermission(guild_id=1, command_name="test", permission_filter="filter")
    permission2 = CommandPermission(guild_id=1, command_name="test", permission_filter="filter")
    permission3 = CommandPermission(guild_id=3, command_name="test", permission_filter="filter")
    assert permission1 == permission2
    assert permission1 != permission3

def test_permission_eq_type_mismatch():
    permission = CommandPermission(guild_id=1, command_name="test", permission_filter="filter")
    assert permission != "not a sub"

def test_permission_hash():
    permission = CommandPermission(guild_id=1, command_name="test", permission_filter="filter")
    assert permission.__hash__()