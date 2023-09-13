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

class GeonodeModel(object):
    """ Geonode proxies service model """
    ip: str
    anonymityLevel: str
    protocols: list
    asn: str
    city: str
    country: str
    created_at: str
    google: bool
    isp: str
    lastChecked: int
    latency: float
    org: str
    port: str
    region: str | None
    responseTime: int
    speed: int
    updated_at: str
    workingPercent: float | None
    upTime: float
    upTimeSuccessCount: int
    upTimeTryCount: int
    proxy: dict = dict()
    is_valid: bool = False

    def __init__(self, console: Console) -> None:
        self.console = console

    def set_fields(self, data: dict) -> None:
        """ Set the values for the fields """
        for field in self.__annotations__:
            if field in ["proxy", "is_valid"]:
                continue

            setattr(self, str(field), data.get(field, None))

    def validate(self) -> bool:
        """ Validate the proxy """
        protocols = self.protocols
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

    def export_tuple(self) -> tuple:
        """ Export the fields into a tuple """
        return (
            self.ip,
            self.anonymityLevel,
            self.asn,
            self.city,
            self.country,
            self.created_at,
            self.google,
            self.isp,
            self.lastChecked,
            self.latency,
            self.org,
            self.port,
            self.protocols,
            self.region,
            self.responseTime,
            self.speed,
            self.updated_at,
            self.workingPercent,
            self.upTime,
            self.upTimeSuccessCount,
            self.upTimeTryCount
        )

    def export_dict(self) -> dict:
        """ Exports the fields into a dict """
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
        """ Exports the current proxies data into a `Proxies` table row """
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
