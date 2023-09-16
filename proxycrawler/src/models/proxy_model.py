import json
import time
import requests

from rich.console import Console
from user_agent import generate_user_agent

from proxycrawler import helpers
from proxycrawler import constants
from proxycrawler.messages import (
    info,
    debug,
    errors
)
from proxycrawler.src.database.tables import Proxies

class ProxyModel(object):
    """
    Represents a proxy model for handling proxy information for proxies that where fetched from a file.

    Attributes:
        proxy (dict): A dictionary containing proxy details for different protocols.
        country (str): The country associated with the proxy (default: "Null").
        is_valid (bool): Indicates whether the proxy is valid or not (default: False).

    Methods:
        __init__(self, ip: str, port: int, protocols: list[str], console: Console): Initializes the ProxyModel instance with the provided parameters.
        validate(self) -> bool: Validates the proxy's compatibility with various protocols.
        export_dict(self) -> dict: Exports the class attributes as a dictionary.
        export_table_row(self) -> Proxies: Exports the proxy data as a `Proxies` table row.

    """
    proxy       :   dict    =   dict()
    country     :   str     =   "Null"
    is_valid    :   bool    =   False

    def __init__(self, ip: str, port: int, protocols: list[str], console: Console | None = None) -> None:
        """
        Initializes a ProxyModel instance with the provided parameters.

        Args:
            ip (str): The IP address of the proxy.
            port (int): The port number of the proxy.
            protocols (list[str]): A list of supported protocols by the proxy.
            console (Console): An instance of the `rich.console.Console` for logging.

        """
        self.ip = ip
        self.port = port
        self.protocols = protocols
        self.console = console

    def validate(self) -> bool:
        """
        Validate proxy

        Args:
            None

        Returns:
            bool: True if the proxy is valid, otherwise False is returned
        """
        proxy = {

        }
        delay_time = 3

        for protocol in self.protocols:
            try:
                headers = {
                    "User-Agent": generate_user_agent()
                }
                proxies = {
                    protocol: f"{protocol}://{self.ip}:{self.port}"
                }
                status_codes = []

                for _ in range(3):
                    time.sleep(delay_time)
                    response = requests.get(
                        "https://google.com",
                        headers=headers,
                        proxies=proxies
                    )
                    status_codes.append(response.status_code)

                if status_codes.count(200) >= 2:
                    proxy[protocol] = proxies[protocol]
            except requests.exceptions.ProxyError as error:
                if constants.DEBUG:
                    self.console.log(
                        debug.EXCEPTION_RAISED_WHEN_VALIDATING_PROXY(
                            proxy=proxies,
                            error=error
                        )
                    )
            except Exception as error:
                if constants.DEBUG:
                    self.console.log(
                        debug.EXCEPTION_RAISED_WHEN_VALIDATING_PROXY(
                            proxy=proxies,
                            error=error
                        )
                    )

        if len(proxy) != 0:
            self.is_valid = True

        self.proxy = proxy

        protocols = []
        for protocol in self.proxy:
            protocols.append(protocol)

        self.protocols = protocols

        return self.is_valid

    def export_dict(self) -> dict:
        """
        Exports class attributes into a dict format.

        Args:
            None

        Returns:
            dict: Provides the class attributes in dictionary format.
        """
        return {
            "ip"                  :     self.ip,
            "port"                :     self.port,
            "country"             :     self.country,
            "proxy"               :     self.proxy,
            "protocols"           :     self.protocols,
            "is_valid"            :     self.is_valid
        }

    def export_table_row(self) -> Proxies:
        """
        Exports the current proxy data as a `Proxies` table row.

        Args:
            None

        Returns:
            Proxies: The `Proxies` table row containing the current proxy data.
        """
        proxy_id = helpers.generate_uid(
            data=json.dumps(
                self.export_dict()
            )
        )

        proxy = Proxies(
            proxy_id=proxy_id,
            ip=self.ip,
            port=self.port,
            proxy=json.dumps(self.proxy),
            protocols=str(self.protocols),
            country=self.country,
            is_valid=self.is_valid
        )

        return proxy
