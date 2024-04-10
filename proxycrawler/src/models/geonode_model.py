import json
import time
import requests

from rich.console import Console
from user_agent import generate_user_agent

from proxycrawler import helpers
from proxycrawler import constants
from proxycrawler.messages import debug
from proxycrawler.src.database.tables import Proxies

class GeonodeModel(object):
    """
    Represents a proxy model for the `Geonode.com` proxies service.

    Attributes:
        ip (str): The IP address of the proxy.
        anonymityLevel (str): The level of anonymity of the proxy.
        protocols (list): A list of supported protocols by the proxy.
        asn (str): The Autonomous System Number (ASN) of the proxy.
        city (str): The city where the proxy is located.
        country (str): The country where the proxy is located.
        created_at (str): The timestamp when the proxy was created.
        google (bool): Indicates Google compatibility.
        isp (str): The Internet Service Provider (ISP) associated with the proxy.
        lastChecked (int): Timestamp for when the proxy was last checked.
        latency (float): The latency of the proxy.
        org (str): The organization or entity behind the proxy.
        port (str): The port number of the proxy.
        region (str | None): The region where the proxy is located (or None if not available).
        responseTime (int): The response time of the proxy.
        speed (int): The speed of the proxy.
        updated_at (str): The timestamp when the proxy was last updated.
        workingPercent (float | None): The percentage of time the proxy is working (or None if not available).
        upTime (float): The uptime of the proxy.
        upTimeSuccessCount (int): The count of successful uptime checks.
        upTimeTryCount (int): The total count of uptime check attempts.
        proxy (dict): A dictionary containing proxy details for different protocols.
        is_valid (bool): Indicates whether the proxy is valid or not.

    Methods:
        set_fields(data: dict): Sets the values for class attributes based on provided data.
        validate(): Validates the proxy's compatibility with various protocols.
        export_dict(): Exports the class attributes as a dictionary.
        export_table_row(): Exports the proxy data as a `Proxies` table row.

    """
    ip                      :       str
    anonymityLevel          :       str
    protocols               :       list
    asn                     :       str
    city                    :       str
    country                 :       str
    created_at              :       str
    google                  :       bool
    isp                     :       str
    lastChecked             :       int
    latency                 :       float
    org                     :       str
    port                    :       str
    region                  :       str | None
    responseTime            :       int
    speed                   :       int
    updated_at              :       str
    workingPercent          :       float | None
    upTime                  :       float
    upTimeSuccessCount      :       int
    upTimeTryCount          :       int
    proxy                   :       dict    =   dict()
    is_valid                :       bool    =   False

    def __init__(self, console: Console) -> None:
        self.console = console

    def set_fields(self, data: dict) -> None:
        """
        Set the values for the class attributes

        Args:
            data (dict): The json response from the `Geonode.com`'s API

        Returns:
            None: This methods doesn't return anything
        """
        for field in self.__annotations__:
            if field in ["proxy", "is_valid"]:
                continue

            setattr(self, str(field), data.get(field, None))

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
            "ip": self.ip,
            "anonymityLevel": self.anonymityLevel,
            "asn": self.asn,
            "city": self.city,
            "country": self.country,
            "created_at": self.created_at,
            "google": self.google,
            "isp": self.isp,
            "lastChecked": self.lastChecked,
            "latency": self.latency,
            "org": self.org,
            "port": self.port,
            "protocols": self.protocols,
            "region": self.region,
            "responseTime": self.responseTime,
            "speed": self.speed,
            "updated_at": self.updated_at,
            "workingPercent": self.workingPercent,
            "upTime": self.upTime,
            "upTimeSuccessCount": self.upTimeSuccessCount,
            "upTimeTryCount": self.upTimeTryCount
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
