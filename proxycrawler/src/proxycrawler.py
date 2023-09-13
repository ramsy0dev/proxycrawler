import re
import ast
import sys
import json
import time
import requests

from user_agent import generate_user_agent
from rich.console import Console

from proxycrawler import constants
from proxycrawler.messages import (
    info,
    debug,
    errors
)
from proxycrawler.src.database.database_handler import DatabaseHandler
from proxycrawler.src.database.tables import Proxies

# Services
from proxycrawler.src.services.geonode import Geonode
from proxycrawler.src.services.freeproxylist import FreeProxyList

# Models
from proxycrawler.src.models.proxy_model import ProxyModel

class ProxyCrawler:
    """ ProxyCrawler """
    free_proxy_list: list = list()
    geonode_proxies_list: list = list()

    output_save_paths: list = list()

    def __init__(
            self, database_handler: DatabaseHandler, console: Console | None = Console()) -> None:
        self.database_handler = database_handler
        self.console = console

    def crawl_proxies(
            self,
            enable_save_on_run: bool,
            group_by_protocol: bool,
            output_file_path: str
        ) -> None:
        """ Starts crawling proxies from all the known services """
        geonode = Geonode(
            console=self.console,

        )
        free_proxy_list = FreeProxyList(
            console=self.console
        )

        services = {
            "free_proxy_list": free_proxy_list,
            "geonode": geonode
        }

        for service in services:
            service_name    =   service
            service         =   services[service]
            service_url     =   service.url

            self.console.log(
                info.USING_SERVICE(
                    service_name=service_name,
                    service_url=service_url
                )
            )

            # Fetching and validating proxies from `service_name`
            service.fetch_proxies()

            # Saving the proxies to the database
            proxies = service.valid_proxies

            for proxy in proxies:
                proxy = proxy.export_table_row()

                self.database_handler.save_proxy(
                    proxy=proxy
                )

            # Save to the output file on the run in case
            # `self.enable_save_on_run` was enabled
            if not enable_save_on_run:
                continue

            self.output_save_paths = self.save_to_file(
                proxies=proxies,
                group_by_protocol=group_by_protocol,
                output_file_path=output_file_path
            )

        if not enable_save_on_run:
            for service in services:
                proxies = services[service].valid_proxies

                self.output_save_paths = self.save_to_file(
                    proxies=proxies,
                    group_by_protocol=group_by_protocol,
                    output_file_path=output_file_path
                )

        self.console.log(
            info.PROXIES_SAVED_IN_PATHS(
                output_file_paths=self.output_save_paths
            )
        )

    def export_database_proxies(
            self,
            proxies_count: int,
            group_by_protocol: bool | None = False,
            validate_proxies: bool | None = True,
            output_file_path: str | None = None
        ) -> None:
        """ Export the proxies from the database and validate them """
        saved_database_proxies = self.database_handler.fetch_proxies(
            proxies_count=proxies_count
        )
        valid_proxies = []

        if len(saved_database_proxies) == 0:
            self.console.log(
                errors.NO_PROXIES_WHERE_FOUND_IN_THE_DATABASE
            )
            sys.exit(1)

        self.console.log(
            info.FETCHED_PROXIES_FROM_THE_DATABASE(
                count=len(saved_database_proxies)
            )
        )

        for proxy in saved_database_proxies:
            proxy = proxy[0]

            if validate_proxies:
                if self.validate_db_proxies(proxy=proxy):
                    valid_proxies.append(proxy)

                    self.database_handler.update_proxy_valid_value(
                        proxy=proxy
                    )

                    self.console.log(
                        info.FOUND_A_VALID_PROXY(
                            proxy=proxy
                        )
                    )

                else:
                    proxy.is_valid = False

                    self.database_handler.update_proxy_valid_value(
                        proxy=proxy
                    )

        if len(valid_proxies) == 0 and not validate_proxies:
            self.output_save_paths = self.save_to_file(
                proxies=saved_database_proxies,
                group_by_protocol=group_by_protocol,
                output_file_path=output_file_path
            )
        else:
            self.output_save_paths = self.save_to_file(
                proxies=valid_proxies,
                group_by_protocol=group_by_protocol,
                output_file_path=output_file_path
            )

        self.console.log(
                info.PROXIES_SAVED_IN_PATHS(
                    output_file_paths=self.output_save_paths
                )
            )

    def validate_db_proxies(self, proxy: Proxies) -> bool:
        """ Validate proxies """
        if type(proxy.proxy) == str:
            proxy.proxy = json.loads(proxy.proxy)

        delay_time = 7
        status_codes = []
        headers = {
            "User-Agent": generate_user_agent()
        }

        for _ in range(3):
            time.sleep(delay_time)
            try:
                response = requests.get(
                        "https://google.com",
                        headers=headers,
                        proxies=proxy.proxy
                    )
                status_codes.append(response.status_code)
            except requests.exceptions.ProxyError as error:
                if constants.DEBUG:
                    self.console.log(
                        debug.EXCEPTION_RAISED_WHEN_VALIDATING_PROXY(
                            proxy=proxy.proxy,
                            error=error
                        )
                    )
            except Exception as error:
                if constants.DEBUG:
                    self.console.log(
                        debug.EXCEPTION_RAISED_WHEN_VALIDATING_PROXY(
                            proxy=proxy.proxy,
                            error=error
                        )
                    )

        if status_codes.count(200) >= 2:
            proxy.is_valid == True

        return proxy.is_valid

    def validate_proxies(self, proxies: list[str], protocol: str | None = None, test_all_protocols: bool | None = False, group_by_protocol: bool | None = False, proxy_file_path: str | None = None,output_file_path: str | None = None) -> None:
        """ Validates proxies """
        protocols = [
            "http",
            "https",
            "socks4",
            "socks5"
        ]
        valid_proxies = []

        # In case of a protocol was specified to test the proxies
        # on or in case the user chose to test all the protocols
        # on the proxies, we need to make sure we are revalidating
        # the same proxy because the list may contain the same proxy
        # but with different procotols, wich is why we keep track of
        # them here in the `processed_proxies`
        processed_proxies = []

        for proxy in proxies:
            if proxy == "":
                continue

            ip = proxy.split("/")[2].split(":")[0]
            port= proxy.split(":")[-1]
            proxy_protocols = None

            # Determining wich protocols to use
            if not test_all_protocols:
                if protocol is None:
                    proxy_protocols = [proxy.split("/")[0].replace(":", "")]
                else:
                    # Skip the proxy if already processed
                    if proxy.split("/")[2] in processed_proxies:
                        continue

                    proxy_protocols = [protocol]
            else:
                # Skip the proxy if already processed
                if proxy.split("/")[2] in processed_proxies:
                    continue

                proxy_protocols = protocols

            proxy = ProxyModel(
                ip=ip,
                port=port,
                protocols=proxy_protocols,
                console=self.console
            )

            if proxy.validate():
                valid_proxies.append(proxy)

                self.console.log(
                    info.FOUND_A_VALID_PROXY(
                        proxy=proxy
                    )
                )

                # Save proxy to the database
                self.database_handler.save_proxy(
                    proxy=proxy.export_table_row()
                )

            processed_proxies.append(f"{proxy.ip}:{proxy.port}")

        if output_file_path is None:
            output_file_path = f"{proxy_file_path.split('/')[-1].replace('.txt', '')}-valid.txt"

        self.output_save_paths = self.save_to_file(
            proxies=valid_proxies,
            group_by_protocol=group_by_protocol,
            output_file_path=output_file_path
        )

        self.console.log(
            info.PROXIES_SAVED_IN_PATHS(
                output_file_paths=self.output_save_paths
            )
        )

    def check_proxy_fromat(self, proxy: str) -> bool:
        """ Checks the format of the proxy """
        regex =  r"^(https?|socks[45])://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+"

        return re.match(regex, proxy)

    def save_to_file(
            self,
            proxies: list,
            group_by_protocol: bool,
            output_file_path: str | None
        ) -> list[str]:
        """ Saves proxies to the output file path """
        output_save_paths = []

        if output_file_path is None:
            output_file_path = f"./proxycrawler-proxies.txt"

        if not group_by_protocol:
            with open(output_file_path, "a") as save_proxies:
                data = []

                for proxy_data in proxies:
                    if type(proxy_data.proxy) == str:
                        proxy_data.proxy = json.loads(proxy_data.proxy) # Reattache to a session

                    for proxy in proxy_data.proxy:
                        data.append(f"{proxy_data.proxy[proxy]}\n")

                save_proxies.write(''.join(data))

            output_save_paths.append(output_file_path)

            return output_save_paths

        protocols = {
            "http": {
                "output_file_path": f"{'/'.join(output_file_path.split('/')[:-1])}/proxies-http.txt",
                "proxies": set()
            },
            "https": {
                "output_file_path": f"{'/'.join(output_file_path.split('/')[:-1])}/proxies-https.txt",
                "proxies": set()
            },
            "socks4": {
                "output_file_path": f"{'/'.join(output_file_path.split('/')[:-1])}/proxies-socks4.txt",
                "proxies": set()
            },
            "socks5": {
                "output_file_path": f"{'/'.join(output_file_path.split('/')[:-1])}/proxies-socks5.txt",
                "proxies": set()
            }
        }

        for proxy in proxies:
            if type(proxy.proxy) == str:
                proxy.proxy = json.loads(proxy.proxy)

            if type(proxy.protocols) == str:
                proxy.protocols = ast.literal_eval(proxy.protocols)

            for protocol in proxy.protocols:
                protocols[protocol]["proxies"].add(f"{proxy.proxy[protocol]}\n")

        for protocol in protocols:
            # Don't save in case no proxies have this `protocol`
            if not len(protocols[protocol]["proxies"]) > 0:
                continue

            with open(protocols[protocol]["output_file_path"], "a") as save_proxies:
                save_proxies.write(''.join(protocols[protocol]["proxies"]))

            output_save_paths.append(protocols[protocol]["output_file_path"])

        self.console.log(output_save_paths)

        return output_save_paths
