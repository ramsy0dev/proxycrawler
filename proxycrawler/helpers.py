import uuid
import string
import random
import hashlib
import datetime
import subprocess

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

def check_for_update() -> (bool, str | None):
    """
    Check for any new updates.
    
    Args:
        None.
    
    Returns:
        (bool, str | None): True if there is an update with the new version tag, otherwise False is returned and None.
    """
    command = f"git ls-remote --tags {constants.GITHUB}"
    output = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    git_output = output.stdout.decode()
    latest_tag = None

    if git_output.split("\n")[-1] == "":
        latest_tag = git_output.split("\n")[-2][-6]
    else:
        latest_tag = git_output.split("\n")[-1][-6]
    
    return (result:=(constants.TAG == latest_tag), latest_tag if result else None)

def self_update() -> str | None:
    """
    Updates proxycrawler
    
    Args:
        None.
    
    Returns:
        str | None: In case of an error message was raised it will be returned.
    """
    command = f"pip install git+{constants.GITHUB}"
    output = subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    error = output.stderr

    return error.decode() if error.decode() != "" else None
