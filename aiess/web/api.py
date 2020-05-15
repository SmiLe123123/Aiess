import json
from collections import defaultdict

from aiess.web.ratelimiter import request_with_rate_limit
from aiess.settings import API_KEY, API_RATE_LIMIT

def request_api(request_type: str, query: str) -> object:
    """Requests a json object from the v1 osu!api, where the api key is supplied."""
    request = f"https://osu.ppy.sh/api/{request_type}?{query}&k={API_KEY}"
    response = request_with_rate_limit(request, API_RATE_LIMIT, "api")
    try:
        json_response = json.loads(response.text)
        if "error" in json_response:
            # e.g. "Please provide a valid API key." if it's incorrect.
            error_str = json_response["error"]
            raise ValueError(f"The osu! api responded with an error \"{error_str}\"")

        return json_response
    except json.decoder.JSONDecodeError:
        # This happens whenever the response text is empty (e.g. "[]").
        return None

requested_beatmapsets = defaultdict()
def request_beatmapset(beatmapset_id: str) -> object:
    """Requests a json object of the given beatmapset id.
    Caches any response gotten until cleared manually."""
    if beatmapset_id in requested_beatmapsets and requested_beatmapsets[beatmapset_id]:
        return requested_beatmapsets[beatmapset_id]
    
    beatmapset_json = request_api("get_beatmaps", f"s={beatmapset_id}")
    requested_beatmapsets[beatmapset_id] = beatmapset_json
    return beatmapset_json

requested_users = defaultdict()
def request_user(user_id: str) -> object:
    """Requests a json object of the given user id.
    Caches any response gotten until cleared manually."""
    if user_id in requested_users and requested_users[user_id]:
        return requested_users[user_id]
    
    user_json = request_api("get_user", f"u={user_id}")
    if len(user_json) > 0:
        requested_users[user_id] = user_json[0]
        return user_json[0]
    
    # For when the user does not exist (e.g. restricted).
    # Do not cache, in case they get unrestricted soon.
    return None

def clear_response_cache() -> None:
    global requested_beatmapsets
    global requested_users
    requested_beatmapsets = defaultdict()
    requested_users = defaultdict()