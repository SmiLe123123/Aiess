from bs4 import BeautifulSoup
from typing import Generator
from bs4.element import Tag
import json

from aiess.objects import Event, Beatmapset, User, Discussion
from aiess.errors import ParsingError, DeletedContextError
from aiess import timestamp
from aiess.logger import log_err

from parsers.event_parser import EventParser

class DiscussionEventParser(EventParser):

    def parse(self, events: BeautifulSoup) -> Generator[Event, None, None]:
        """Returns a generator of BeatmapsetEvents, from the given /beatmapset-discussions BeautifulSoup response, parsed top-down."""
        event_tags = events.findAll("div", {"class": "beatmapset-activities__discussion-post"})
        if event_tags:
            for event_tag in event_tags:
                event = self.parse_event(event_tag)
                if event:
                    yield event
        else:
            # In case the page uses a json format script to fill out the page.
            # Currently /beatmap-discussions does this, but not /beatmap-discussion-posts.
            json_discussions = events.find("script", {"id": "json-discussions"})
            json_users = events.find("script", {"id": "json-users"})

            event_jsons = json.loads(json_discussions.text)
            user_jsons = json.loads(json_users.text)

            for event_json in event_jsons:
                event = self.parse_event_json(event_json, user_jsons)
                if event:
                    yield event
    
    def parse_event(self, event: Tag) -> Event:
        """Returns a BeatmapsetEvent reflecting the given event html Tag object.
        Ignores any event with an incomplete context (e.g. deleted beatmaps)."""
        try:
            # Scrape object data
            _type = self.parse_event_type(event)
            time = self.parse_event_time(event)

            link = self.parse_event_link(event)
            beatmapset_id = self.parse_id_from_beatmapset_link(link)
            discussion_id = self.parse_id_from_discussion_link(link)

            user_id = self.parse_event_author_id(event)
            user_name = self.parse_event_author_name(event)

            content = self.parse_discussion_message(event)

            # Reconstruct objects
            beatmapset = Beatmapset(beatmapset_id)
            user = User(user_id, user_name) if user_id != None else None
            if _type == "reply":
                # Replies should look up the discussion they are posted on.
                discussion = Discussion(discussion_id, beatmapset) if discussion_id != None else None
            else:
                discussion = Discussion(discussion_id, beatmapset, user, content) if discussion_id != None else None
        except DeletedContextError as err:
            log_err(err)
        else:
            return Event(
                _type = _type,
                time = time,
                beatmapset = beatmapset,
                discussion = discussion,
                user = user,
                content = content)
    
    def parse_event_json(self, event_json: object, user_jsons: object=None) -> Event:
        """Returns a BeatmapsetEvent reflecting the given event json object.
        Ignores any event with an incomplete context (e.g. deleted beatmaps).

        Requests user names from the api unless supplied with the corresponding user json from the discussion page."""
        try:
            # Scrape object data
            _type = event_json["message_type"]
            time = timestamp.from_string(event_json["created_at"])

            beatmapset_id = event_json["beatmapset_id"]
            discussion_id = event_json["starting_post"]["beatmap_discussion_id"]

            user_id = event_json["user_id"]
            # The user name is either provided by a user json from the discussion page, or queried through the api.
            user_json = self.__lookup_user_json(user_id, user_jsons)
            user_name = user_json["username"] if user_json else None
            
            content = event_json["starting_post"]["message"]

            # Reconstruct objects
            beatmapset = Beatmapset(beatmapset_id)
            user = User(user_id, user_name) if user_id != None else None
            # TODO: This portion is missing handling for replies, see the other method.
            # Still unclear which message_type replies use; will need to find out if/when replies get json formats.
            discussion = Discussion(discussion_id, beatmapset, user, content) if discussion_id != None else None
        except DeletedContextError as err:
            log_err(err)
        else:
            return Event(
                _type = _type,
                time = time,
                beatmapset = beatmapset,
                discussion = discussion,
                user = user,
                content = content)
    
    def __lookup_user_json(self, user_id: str, user_jsons: object):
        if not user_jsons:
            return None

        for user_json in user_jsons:
            if user_json["id"] == user_id:
                return user_json
        
        return None

    def parse_event_type(self, event: Tag) -> str:
        """Returns the type of the given event (e.g. "suggestion", "problem", "hype")."""
        event_class = "beatmap-discussion-message-type"
        class_prefix = "beatmap-discussion-message-type--"
        try:
            return super().parse_event_type(event,
                event_class=event_class,
                class_prefix=class_prefix)
        except ParsingError:
            if event:
                is_discussion_message = event.find(attrs={"class": event_class})
                has_type = event.find(attrs={"class": class_prefix})
                # Replies have no explicit type.
                if is_discussion_message and not has_type:
                    return "reply"
            raise
    
    def parse_event_author_id(self, event: Tag) -> str:
        """Returns the user id associated with the given event, if applicable (e.g. the user starting a discussion, "1314547")."""
        return super().parse_event_author_id(event,
            href_class="beatmap-discussion-user-card__user-link",
            must_find=True)
    
    def parse_event_author_name(self, event: Tag) -> str:
        """Returns the user name associated the given event, if applicable (e.g. the user starting a discussion, 5129592)."""
        return super().parse_event_author_name(event,
            name_class="beatmap-discussion-user-card__user-text",
            must_find=True)

    def parse_discussion_message(self, event: Tag) -> str:
        """Parses the raw message content of a discussion post."""
        message_class = "beatmap-discussion-post__message"
        return event.find("div", {"class": message_class}).contents[0]

# Only need one instance since it's always the same.
discussion_event_parser = DiscussionEventParser()