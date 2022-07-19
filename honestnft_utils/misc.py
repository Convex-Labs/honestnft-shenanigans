import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def strtobool(val: str) -> bool:
    """Convert a string representation of truth to True or False.

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.

    :param val: string representation of truth
    :raises ValueError: if val can't be converted to a truthish value
    :return: True or False
    """
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return True
    elif val in ("n", "no", "f", "false", "off", "0"):
        return False
    else:
        raise ValueError("invalid truth value %r" % (val,))


def mount_session() -> requests.Session:
    """Create a requests.session() with optimised strategy for retrying and respecting errors

    :return: A requests session with retry and error handling
    """
    retry_strategy = Retry(
        total=5,
        respect_retry_after_header=True,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504, 520],
        allowed_methods=["GET"],
    )
    retry_strategy.DEFAULT_BACKOFF_MAX = 5  # type: ignore
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount(prefix="https://", adapter=adapter)
    session.mount(prefix="http://", adapter=adapter)

    return session
