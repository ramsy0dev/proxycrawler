import uuid
import string
import random
import hashlib
import datetime

from rich import print

from proxycrawler import constants

def banner() -> None:
    """ proxycrawler's banner """
    print(constants.BANNER)

# def log_json(json_data: str, console) -> None:
#     """ Logs out the json data in a beautified way """
#     splited_json_data = json_data.split("\n")

#     for log_line in splited_json_data:
#         console.log(log_line)

def date() -> datetime:
    """ Returns the current date """
    return datetime.datetime.now()

def generate_uid(data: str) -> str:
    """ Generates a UID based on the given data """
    data = f"{data}{''.join([char for char in random.choices(string.ascii_letters)])}"

    hashed_data_salt = hashlib.md5(data.encode()).hexdigest()
    generated_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, hashed_data_salt)

    return str(generated_uuid)
