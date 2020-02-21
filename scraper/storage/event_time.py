from datetime import datetime
import os

PATH_PREFIX = "../time/"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
FILE_NAME_PREFIX = "last_datetime-"
FILE_NAME_POSTFIX = ".txt"

def get_last(id: str=None) -> datetime:
    """Returns the last datetime we're done with for this id. If the file doesn't exist, one will be created
    with the current time in UTC as datetime."""
    # Only in cases where the file does not already exist do we want to create and initialize one.
    # In any other case we should throw an exception if data is missing (e.g. corruption due to power loss),
    # to prevent silent failure.
    path = get_path(id)
    if not exists(id):
        with open(path, "w") as _file:
            _file.write(format_time(datetime.utcnow()))

    with open(path, "r") as _file:
        last_datetime_text = _file.read()
        if not last_datetime_text:
            raise ValueError(f"{path} has no contents.")
        
        # Will only raise an exception if the file already exists, but has an invalid datetime format (e.g. empty).
        last_datetime = datetime.strptime(last_datetime_text, TIME_FORMAT)
        return last_datetime

def set_last(new_datetime: datetime, id: str=None) -> None:
    """Sets the last datetime we're done with for this id. Creates the respective file if it does not exist."""
    with open(get_path(id), "w") as _file:
        _file.write(format_time(new_datetime))

def exists(id: str=None) -> bool:
    """Returns whether a datetime file for this id exists."""
    return os.path.exists(get_path(id))

def get_path(id: str=None) -> str:
    """Returns the path to the event time file with the given identifier."""
    global PATH_PREFIX, FILE_NAME_PREFIX, FILE_NAME_POSTFIX
    return f"{PATH_PREFIX}{FILE_NAME_PREFIX}{id}{FILE_NAME_POSTFIX}"

def format_time(_datetime: datetime) -> str:
    """Returns the year-month-day hour:minute:second format of the given datetime."""
    return _datetime.strftime(TIME_FORMAT)