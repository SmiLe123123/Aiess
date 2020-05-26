import requests
from requests import Response
from socket import gaierror
from typing import Generator, Dict
from time import sleep
from datetime import datetime, timedelta
from collections import defaultdict

from aiess.logger import log_err

next_request_time: Dict[str, datetime] = defaultdict(lambda: datetime.utcnow())
failed_attempts: Dict[str, datetime] = defaultdict(int)

def request_with_rate_limit(request_url: str, rate_limit: float, rate_limit_id: str=None) -> Response:
    """Requests a response object at most once every rate_limit seconds for the same rate_limit_id (default None)."""
    global next_request_time
    
    response = None
    while not response:
        request_time = next_request_time[rate_limit_id]
        if request_time and request_time > datetime.now():
            sleep((request_time - datetime.now()).total_seconds())

        response = try_request(request_url)
        next_request_time[rate_limit_id] = datetime.now() + timedelta(seconds=rate_limit)

        # `try_request` will return None in case of ConnectionErrors or IUAM.
        # In these cases we back off and wait until it's over.
        if not response:
            back_off(rate_limit_id)

    if rate_limit_id in failed_attempts:
        failed_attempts[rate_limit_id] = 0

    return response

def try_request(request_url: str) -> Response:
    """Requests a response object and returns it if successful, otherwise None is returned.
    If the website is in cloudflare IUAM mode, we also return None."""
    response = None

    try:
        response = requests.get(request_url)
    except ConnectionError:
        log_err(f"WARNING | ConnectionError was raised on GET \"{request_url}\", retrying...")
        return None
    
    if "<title>Just a moment...</title>" in response.text:
        log_err("WARNING | CloudFlare IUAM is active")
        return None
    
    return response

def back_off(rate_limit_id: str=None) -> None:
    """Postpones the next request for 30 -> 60 -> 120 -> 240 seconds for 1, 2, 3, and 4+ tries respectively.
    This way we give the website some room to breathe if there are already many incoming connections causing this."""
    global failed_attempts
    if failed_attempts[rate_limit_id] < 4:
        failed_attempts[rate_limit_id] += 1

    next_request_time[rate_limit_id] += timedelta(seconds = 30 * 2**(failed_attempts[rate_limit_id] - 1))