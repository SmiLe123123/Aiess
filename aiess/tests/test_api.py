from datetime import datetime

from aiess.web import api

def test_cache():
    api.cache.clear()
    assert not api.cache

    beatmapset_response = api.request_beatmapset(1)
    user_response       = api.request_user(2)
    assert beatmapset_response
    assert user_response

    assert api.cache
    assert api.cache["/get_beatmaps?s=1"]
    assert api.cache["/get_user?u=2"]

def test_cache_timing():
    api.cache.clear()

    # Not cached, needs to be retrieved with API rate limit.
    time = datetime.utcnow()
    api.request_beatmapset(1)
    api.request_user(2)
    delta_time = datetime.utcnow() - time

    assert delta_time.total_seconds() > 1

    # Cached, can simply be read from a dictionary, should be pretty much instant.
    time = datetime.utcnow()
    api.request_beatmapset(1)
    api.request_user(2)
    delta_time = datetime.utcnow() - time

    assert delta_time.total_seconds() < 0.01

def test_request_beatmapset():
    beatmapset_response = api.request_beatmapset(1)

    assert beatmapset_response[0]["title"] == "DISCO PRINCE"
    assert beatmapset_response[0]["artist"] == "Kenji Ninuma"

def test_request_user():
    user_response = api.request_user(2)

    assert user_response["username"] == "peppy"

def test_request_user_escaped_name():
    user_response = api.request_user("-Mo- &amp; Ephemeral")

    assert user_response is None