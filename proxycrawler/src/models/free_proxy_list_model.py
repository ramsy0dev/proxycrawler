import json
import time
import requests

from rich.console import Console
from user_agent import generate_user_agent

from proxycrawler import helpers
from proxycrawler import constants
from proxycrawler.messages import debug
from proxycrawler.src.database.tables import Proxies

class FreeProxyListModel(object):
    """
    Represents a proxy model for storing and validating proxy data from the `free-proxy-list.net` service.

    Attributes:
        ip (str): The IP address of the proxy.
        port (str): The port number of the proxy.
        proxy_country_code (str): The country code associated with the proxy.
        country (str): The country name associated with the proxy.
        provider (str): The provider or source of the proxy.
        google (str): Information about Google compatibility.
        https (str): Information about HTTPS support.
        last_checked (str): Timestamp for when the proxy was last checked.
        proxy (dict): A dictionary containing proxy details for different protocols.
        is_valid (bool): Indicates whether the proxy is valid or not.

    Methods:
        validate(): Validates the proxy's compatibility with various protocols.
        export_dict(): Exports the class attributes as a dictionary.
        export_table_row(): Exports the proxy data as a `Proxies` table row.
    """
    ip                      :       str
    port                    :       str
    proxy_country_code      :       str
    country                 :       str
    provider                :       str
    google                  :       str
    https                   :       str
    last_checked            :       str
    proxy                   :       dict    =   dict()
    is_valid                :       bool    =   False

    def __init__(self, console: Console | None = None) -> None:
        self.protocols = list() # supported protocols
        self.console = console

    def validate(self) -> bool:
        """
        Validate proxy

        Args:
            None

        Returns:
            bool: True if the proxy is valid, otherwise False is returned
        """
        protocols = ["http", "https", "socks4", "socks5"]
        proxy = {

        }
        delay_time = 3

        for protocol in protocols:
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
                    self.protocols.append(protocol)
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
            "ip"                  : self.ip,
            "port"                : self.port,
            "proxy_country_code"  : self.proxy_country_code,
            "country"             : self.country,
            "provider"            : self.provider,
            "google"              : self.google,
            "https"               : self.https,
            "last_checked"        : self.last_checked,
            "proxy"               : self.proxy,
            "is_valid"            : self.is_valid
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
