import sys
sys.path.append('..')

from bs4 import BeautifulSoup
from datetime import datetime
from time import sleep

from aiess import timestamp, logger
from aiess.logger import log
from aiess.database import Database, SCRAPER_DB_NAME

from scraper.crawler import get_all_events_between

init_time_str = datetime.utcnow().strftime("%Y%m%d-%H%M%S")

def loop() -> None:
    """Iterates over new events since the last time, inserts them into the database, and then updates the last time."""
    current_time = datetime.utcnow().replace(microsecond=0)
    last_time = timestamp.get_last("events")

    push_events(get_all_events_between, current_time, last_time)

    last_updated(current_time)

def push_events(generator_func, current_time, last_time) -> None:
    """Parses and inserts events generated by the given function over the timeframe."""
    events = []
    parse_events(events, generator_func, current_time, last_time)
    insert_db(events)

def parse_events(event_list, generator_func, current_time, last_time) -> None:
    """Parses events generated by the given function over the timeframe and appends them to the event list."""
    log(f"--- Parsing Events from {last_time} to {current_time} ---")
    for event in generator_func(current_time, last_time):
        log(event)
        event_list.append(event)

def insert_db(events) -> None:
    """Inserts the given event list into the database in reversed order."""
    if not events:
        return
    
    events.sort(key=lambda event: event.time)

    log(f"--- Inserting {len(events)} Events into the Database ---")
    for event in events:
        log(".", newline=False)
        database.insert_event(event)
    log()

def last_updated(current_time) -> None:
    """Updates the last updated file to reflect the given time."""
    log(f"--- Last Updated {current_time} ---")
    timestamp.set_last(current_time, "events")

logger.init(init_time_str)
database = Database(SCRAPER_DB_NAME)
while(True):
    loop()
    sleep(60)