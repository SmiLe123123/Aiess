from datetime import datetime
from typing import List

from aiess.web import api
from aiess.errors import DeletedContextError

class User:
    """Contains the user data either requested from the api or directly supplied (i.e. id, name)."""
    def __init__(self, _id: int=None, name: str=None):
        if _id is None and name is None:
            raise ValueError("Cannot create a User object with neither id nor name provided.")

        self.id = int(_id) if _id is not None else None
        self.name = str(name) if name is not None else None

        if name is None:
            user_json = api.request_user(_id)
            if user_json is not None:
                self.name = str(user_json["username"])
            else:
                # User doesn't exist, likely restricted.
                self.name = None
        
        if _id is None:
            user_json = api.request_user(name)
            if user_json is not None:
                self.id = int(user_json["user_id"])
            else:
                # User doesn't exist, either restricted or renamed a long time ago.
                self.id = None
    
    def __str__(self) -> str:
        return self.name if self.name is not None else str(self.id)
    
    def __key(self) -> tuple:
        return (
            self.id,
            self.name
        )
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, User):
            return False
        return self.__key() == other.__key()
    
    def __hash__(self) -> str:
        return hash(self.__key())

class Beatmapset:
    """Contains the beatmapset data requested from the api or supplied as a json object (e.g. artist, title, creator)."""
    def __init__(
            self, _id: int, artist: str=None, title: str=None, creator: User=None,
            modes: List[str]=None, genre: str=None, language: str=None, beatmapset_json: object=None):
        if _id is None:
            raise ValueError("Beatmapset id should not be None.")

        # No need to get the beatmap json if we already have all the data.
        if artist is None or title is None or creator is None or modes is None or language is None or genre is None:
            if not beatmapset_json:
                beatmapset_json = api.request_beatmapset(_id)
                if not beatmapset_json:
                    raise DeletedContextError(f"Could not retrieve any api response for a beatmapset with id {_id}.")
            if str(beatmapset_json) == "[]":
                raise DeletedContextError(f"No beatmapset with id {_id} exists.")
            beatmap_json = beatmapset_json[0]  # Assumes metadata is the same across the entire set.

        self.id = int(_id)
        self.artist = str(artist) if artist is not None else beatmap_json["artist"]
        self.title = str(title) if title is not None else beatmap_json["title"]
        self.creator = creator if creator is not None else User(
            beatmap_json["creator_id"],
            beatmap_json["creator"])
        
        self.modes = modes if modes is not None else self.__get_modes(beatmapset_json)
        self.genre = genre if genre is not None else self.__get_genre(beatmapset_json)
        self.language = language if language is not None else self.__get_language(beatmapset_json)
    
    def __str__(self) -> str:
        return f"{self.artist} - {self.title} (mapped by {self.creator}) {self.mode_str()}"

    def mode_str(self) -> str:
        string = ""
        for mode in self.modes:
            string += f"[{mode}]"
        return string

    def __get_modes(self, beatmapset_json: object) -> List[str]:
        """Returns a list of the game modes by name included in the given beatmapset json (e.g. ["osu", "taiko", "mania"])."""
        mode_names = []
        for beatmap_json in beatmapset_json:
            mode_id = beatmap_json["mode"]
            mode_name = api.MODES[mode_id]
            if mode_name not in mode_names:
                mode_names.append(mode_name)
        return mode_names
    
    def __get_genre(self, beatmapset_json: object) -> str:
        """Returns the genre by name included in the given beatmapset json (e.g. "Electronic")."""
        return api.GENRES[beatmapset_json[0]["genre_id"]]

    def __get_language(self, beatmapset_json: object) -> str:
        """Returns the language by name included in the given beatmapset json (e.g. "Instrumental")."""
        return api.LANGUAGES[beatmapset_json[0]["language_id"]]
    
    def __key(self) -> tuple:
        return (
            self.id,
            self.artist,
            self.title,
            self.creator,
            tuple(self.modes)  # Cannot hash mutable types; list is mutable, tuple is immutable.
        )
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Beatmapset):
            return False
        return self.__key() == other.__key()
    
    def __hash__(self) -> str:
        return hash(self.__key())

class Discussion:
    """Contains the discussion data either supplied or further scraped (latter in case of e.g. disqualify or nomination_reset events)."""
    def __init__(self, _id: int, beatmapset: Beatmapset, user: User=None, content: str=None, tab: str=None, difficulty: str=None):
        self.id = int(_id)
        self.beatmapset = beatmapset
        self.user = user if user is not None else None
        self.content = str(content) if content is not None else None
        self.tab = str(tab) if tab is not None else None
        self.difficulty = str(difficulty) if difficulty is not None else None
    
    def __key(self) -> tuple:
        return (
            self.id,
            self.beatmapset,
            self.user,
            self.content,
            self.tab,
            self.difficulty
        )
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Discussion):
            return False
        return self.__key() == other.__key()
    
    def __hash__(self) -> str:
        return hash(self.__key())

class Usergroup:
    """Contains the usergroup data (i.e id, name). Name is implied from id if not supplied."""
    GROUP_NAMES = {
        4: "Global Moderation Team",
        7: "Nomination Assessment Team",
        11: "Development Team",
        16: "Alumni",
        22: "Support Team",
        28: "Beatmap Nominators",
        32: "Beatmap Nominators (Probationary)"
    }

    def __init__(self, _id: int, name: str=None, mode: str=None):
        self.id = int(_id)
        self.name = str(name) if name is not None else self.__get_name(int(_id))
        self.mode = mode

    def __get_name(self, _id: int) -> str:
        """Returns the name of the given group id, or None if unrecognized."""
        return self.GROUP_NAMES[_id] if _id in self.GROUP_NAMES else None
    
    def __key(self) -> tuple:
        return (
            self.id,
            self.name,
            self.mode
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, Usergroup):
            return False
        return self.__key() == other.__key()
    
    def __hash__(self) -> str:
        return hash(self.__key())
    
    def __str__(self) -> str:
        if self.name:
            return self.name
        return "group " + self.id

class NewsPost:
    """Contains news post data (e.g. title, preview, author, and image url)."""
    def __init__(self, _id: int, title: str, preview: str, author: User, slug: str, image_url: str):
        self.id = int(_id)
        self.title = str(title)
        self.preview = str(preview)
        self.author = author
        self.slug = str(slug)
        self.image_url = str(image_url)

    def __key(self) -> tuple:
        return (
            self.id,
            self.title,
            self.preview,
            self.author,
            self.slug,
            self.image_url
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, NewsPost):
            return False
        return self.__key() == other.__key()
    
    def __hash__(self) -> str:
        return hash(self.__key())
    
    def __str__(self) -> str:
        return self.title

class Event:
    """Contains the event data (i.e. type, time, mapset, discussion, user, group, content).
    Some of these properties will be None depending on type."""
    def __init__(
            self, _type: str, time: datetime, beatmapset: Beatmapset=None, discussion: Discussion=None,
            user: User=None, group: Usergroup=None, newspost: NewsPost=None, content: str=None):
        self.type = _type
        self.time = time.replace(microsecond=0)  # Simplify precision to database-level
        self.beatmapset = beatmapset
        self.discussion = discussion
        self.user = user
        self.group = group
        self.newspost = newspost
        self.content = str(content) if content is not None else None

        # Occurs in cases where the event should not be logged.
        # e.g. discussion deleted but we don't have the discussion cached (no relevant information).
        self.marked_for_deletion = False
    
    def __str__(self) -> str:
        string = f"{self.time} | {self.type}"
        string += f" ({self.user})" if self.user else ""
        string += f" on {self.beatmapset}" if self.beatmapset else ""
        string += f" to/from {self.group}" if self.group else ""
        string += f" posted {self.newspost}" if self.newspost else ""
        string += f" \"{self.content}\"" if self.content else ""
        
        return string
    
    def __key(self) -> tuple:
        return (
            self.type,
            self.time,
            self.beatmapset,
            self.discussion,
            self.user,
            self.group,
            self.content
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, Event):
            return False
        return self.__key() == other.__key()
    
    def __hash__(self) -> str:
        return hash(self.__key())