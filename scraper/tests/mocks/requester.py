import sys
sys.path.append('..')

from aiess import Event, Beatmapset, User, Discussion
from aiess.timestamp import from_string

beatmapset = Beatmapset(4, "artist", "title", creator=User(1, "someone"), modes=["osu"])
discussion = Discussion(5, beatmapset=beatmapset, user=User(2, "sometwo"), content="hi")
discussion_dq = Discussion(6, beatmapset=beatmapset, user=User(2, "sometwo"), content="no wait")

# Note that all events are yielded from newest to oldest.

def get_discussion_events(page: int=1, limit: int=50):
    if page == 1:
        yield Event("problem", from_string("2020-01-01 03:00:00"), beatmapset, discussion_dq, user=User(2, "sometwo"), content="no wait")
        yield Event("hype", from_string("2020-01-01 02:30:00"), beatmapset, user=User(2, "sometwo"), content="hype")
        yield Event("praise", from_string("2020-01-01 02:00:00"), beatmapset, user=User(2, "sometwo"), content="amazing")
    if page == 2:
        yield Event("issue_resolve", from_string("2020-01-01 01:00:00"), beatmapset, discussion, user=User(1, "someone"))
        yield Event("praise", from_string("2020-01-01 00:00:00"), beatmapset, user=User(2, "sometwo"), content="wow")

def get_reply_events(page: int=1, limit: int=50):
    if page == 1:
        yield Event("reply", from_string("2020-01-01 01:04:00"), beatmapset, user=User(2, "sometwo"), content="thanks")
        yield Event("reply", from_string("2020-01-01 01:00:00"), beatmapset, user=User(1, "someone"), content="hi")
        yield Event("reply", from_string("2020-01-01 00:31:00"), beatmapset, discussion, user=User(2, "sometwo"), content="say hi back")
    if page == 2:
        yield Event("reply", from_string("2020-01-01 00:30:00"), beatmapset, discussion, user=User(1, "someone"), content="yes?")
        yield Event("reply", from_string("2020-01-01 00:00:00"), beatmapset, discussion, user=User(2, "sometwo"), content="please reply")

def get_beatmapset_events(page: int=1, limit: int=50):
    if page == 1:
        yield Event("disqualify", from_string("2020-01-01 03:00:00"), beatmapset, discussion_dq, user=User(2, "sometwo"))
        yield Event("qualify", from_string("2020-01-01 02:31:00"), beatmapset)
        yield Event("nominate", from_string("2020-01-01 02:31:00"), beatmapset, user=User(2, "sometwo"))
    if page == 2:
        yield Event("nominate", from_string("2020-01-01 02:30:30"), beatmapset, user=User(1, "someone"))