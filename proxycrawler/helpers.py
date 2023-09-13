import uuid
import string
import random
import hashlib
import datetime

from rich import print

from proxycrawler import constants

def banner() -> None:
    """
    Display the proxycrawler's banner.

    Args:
        None

    Returns:
        None: This function doesn't return anything
    """
    print(constants.BANNER)

def date() -> datetime:
    """
    Returns the current date

    Args:
        None

    Returns:
        datetime.datetime: An instance of the `datetime` class representing the current date and time.
    """
    return datetime.datetime.now()

def generate_uid(data: str) -> str:
    """
    Generates a UID based on the given data.

    Args:
        data (str): Data to use to create a UID based off it.

    Returns:
        str: Returns the generated UID
    """
    data = f"{data}{''.join([char for char in random.choices(string.ascii_letters)])}"

    hashed_data_salt = hashlib.md5(data.encode()).hexdigest()
    generated_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, hashed_data_salt)

    return str(generated_uuid)
