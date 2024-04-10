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
from proxycrawler.src.database.tables import Proxies
from proxycrawler.src.database.database_handler import DatabaseHandler

# Services
from proxycrawler.src.services.geonode import Geonode
from proxycrawler.src.services.freeproxylist import FreeProxyList

# Models
from proxycrawler.src.models.proxy_model import ProxyModel
from proxycrawler.src.models.geonode_model import GeonodeModel
from proxycrawler.src.models.free_proxy_list_model import FreeProxyListModel

class ProxyCrawler:
    """
    A class representing the proxycrawler module, which provides functionality for crawling, validating,
    and managing proxy data from various services.

    Attributes:
        free_proxy_list (list): A list that will be used to store the valid proxies scrapped from the service `https://free-proxy-list.com`
        geonnode_proxies_paths (list): A list that will be used to store the valid proxies scrapped from the service `https://geonode.net`
        output_save_paths (list): A list that will store the paths to the files where the proxies where saved. There can be multipule files if the flag `--group-by-protocol` was used wich will seperate the proxies into different files based off their supported protocol

    """
    free_proxy_list         :   list    = list()
    geonode_proxies_list    :   list    = list()
    output_save_paths       :   list    = list()

    def __init__(self, database_handler: DatabaseHandler, console: Console | None = None) -> None:
        self.database_handler = database_handler
        self.console = console

    def crawl_proxies(
            self,
            enable_save_on_run: bool | None = True,
            group_by_protocol: bool | None = False,
            validate_proxies: bool | None = False,
            output_file_path: str | None = None
        ) -> None:
        """
        Starts crawling proxies from all the known services

        This method initiates the process of gathering proxy information from various services. It takes several parameters, including options to enable saving the crawled proxies on the run to a file and group them by protocol. Additionally, you can specify a custom output file path for saving the results.

        Args:
            enable_save_on_run (bool, optional, default: True): Save the validated proxies of a service after finishing scrapping it.
            group_by_protocol: (bool, optional, default: False): Save the proxies into seperate files depending on the supported protocol type.
            validate_proxies (bool, optional, default: False): Is to validate each proxy that was found (enabling this will make the scrapping process run more slower).
            output_file_path: (str, optional, default: None): A custom output file path to save the proxies to.

        Returns:
            None: this method doesn't return anything.

        NOTE:
            If the `group_by_protocol` option is turned on, the proxies will be stored in the same directory as the custom file.
        """
        geonode = Geonode(
            console=self.console,
            database_handler=self.database_handler,
            save_proxies_to_file=self.save_proxies_to_file,
            enable_save_on_run=enable_save_on_run,
            group_by_protocol=group_by_protocol,
            validate_proxies=validate_proxies,
            output_file_path=output_file_path
        )
        free_proxy_list = FreeProxyList(
            database_handler=self.database_handler,
            validate_proxies=validate_proxies,
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

            proxies = service.found_proxies

            # Save to the output file on the run in case
            # `self.enable_save_on_run` was enabled
            if not enable_save_on_run:
                # Saving the proxies to the database
                for proxy in proxies:
                    proxy = proxy.export_table_row()

                    self.database_handler.save_proxy(
                        proxy=proxy
                    )
                
                continue

            self.output_save_paths = self.save_proxies_to_file(
                proxies=proxies,
                group_by_protocol=group_by_protocol,
                output_file_path=output_file_path
            )

        if not enable_save_on_run:
            for service in services:
                proxies = services[service].valid_proxies

                self.output_save_paths = self.save_proxies_to_file(
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
        """
        Export a number of proxies from the database and validate them

        Args:
            proxies_count (int): The number of proxies to export and validate from the database.
            enable_save_on_run (bool, optional, default: True): Save the validated proxies of a service after finishing scrapping it.
            group_by_protocol: (bool, optional, default: False): Save the proxies into seperate files depending on the supported protocol type.
            output_file_path: (str, optional, default: None): A custom output file path to save the proxies to.

        Returns:
            None: This method doesn't return anything.

        NOTE:
            If the `group_by_protocol` option is turned on, the proxies will be stored in the same directory as the custom file.
        """
        saved_database_proxies = self.database_handler.fetch_proxies(
            proxies_count=proxies_count
        )
        valid_proxies = []

        if len(saved_database_proxies) == 0:
            self.console.log(
                errors.NO_PROXIES_WHERE_FOUND_IN_THE_DATABASE
            )
            sys.exit(1)

        if valid_proxies:
            self.console.log(
                info.FETCHED_PROXIES_FROM_THE_DATABASE_VALIDATING(
                    count=len(saved_database_proxies)
                )
            )
        else:
            self.console.log(
                info.FETCHED_PROXIES_FROM_THE_DATABASE_WITHOUT_VALIDATING(
                    count=len(saved_database_proxies)
                )
            )
        
        for proxy in saved_database_proxies:
            proxy = proxy[0]

            if not validate_proxies:
                valid_proxies.append(proxy)
                continue

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
            self.output_save_paths = self.save_proxies_to_file(
                proxies=saved_database_proxies,
                group_by_protocol=group_by_protocol,
                output_file_path=output_file_path
            )
        else:
            self.output_save_paths = self.save_proxies_to_file(
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
        """
        Validate proxies from the database

        Args:
            proxy (Proxies): A proxy record representing a row in the 'Proxies' table.

        Returns:
            bool: True if the proxy is valid, otherwise False is returned.
        """
        if isinstance(proxy.proxy, str):
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
            proxy.is_valid = True

        return proxy.is_valid

    def validate_proxies(
            self,
            proxies: list[str],
            proxy_file_path: str,
            protocol: str | None = None,
            test_all_protocols: bool | None = False,
            group_by_protocol: bool | None = False,
            output_file_path: str | None = None
        ) -> None:
        """
        Validates proxies from a proxy list file

        Args:
            proxies (list[str]): A list of proxies in plain text in the format <protocol>://<ip>:<port>.
            protocol (str, optional): The protocol to test the proxies on.
            test_all_protocols (bool, optional, default: False): Evaluate the proxies against all available protocols.
            group_by_protocol: (bool, optional, default: False): Save the proxies into seperate files depending on the supported protocol type.
            output_file_path: (str, optional, default: None): A custom output file path to save the proxies to.

        Returns:
            None: This method doesn't return anything.

        NOTE:
            If the `group_by_protocol` option is turned on, the proxies will be stored in the same directory as the custom file.
        """
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

        self.output_save_paths = self.save_proxies_to_file(
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
        """
        Checks the format of the proxy.
        The supported format is <protocol>://<ip>:<port>.

        Args:
            proxy (str): The proxy info in plain text.

        Returns:
            bool: True if the proxy's format is valid, otherwise False is returned.
        """
        regex =  r"^(https?|socks[45])://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+"

        return re.match(regex, proxy)

    def save_proxies_to_file(
            self,
            proxies: list[FreeProxyListModel | GeonodeModel | ProxyModel],
            group_by_protocol: bool | None = False,
            output_file_path: str | None = None
        ) -> list[str]:
        """
        Saves proxies to the output file path.
        In case no `output_file_path` was given the proxies will be saved based on if `group_by_protocol` is turned on.

        Args:
            proxies (list): List of instance of models `FreeProxyListMode`, `GeonodeModel` and `ProxyModel`.
            group_by_protocol: (bool, optional, default: False): Save the proxies into seperate files depending on the supported protocol type.
                output_file_path: (str, optional, default: None): A custom output file path to save the proxies to.

        Returns:
            list[str]: Returns a list paths `self.output_save_paths` where the proxies where saved. `

        NOTE:
            If the `group_by_protocol` option is turned on, the proxies will be stored in the same directory as the custom file.
        """
        output_save_paths = []

        if output_file_path is None:
            output_file_path = "./proxycrawler-proxies.txt"

        if not group_by_protocol:
            with open(output_file_path, "a") as save_proxies:
                data = []

                for proxy_data in proxies:
                    if isinstance(proxy_data.proxy, str):
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

        # Load the proxies into the "proxies" key in
        # protocols based on the supported protocol
        for proxy in proxies:
            if isinstance(proxy.proxy, str):
                proxy.proxy = json.loads(proxy.proxy)

            if isinstance(proxy.protocols, str):
                proxy.protocols = ast.literal_eval(proxy.protocols)

            for protocol in proxy.protocols:
                protocols[protocol]["proxies"].add(f"{proxy.proxy[protocol]}\n")

        # Save the proxies into the corresponding "output_file_path" key's value
        for protocol in protocols:
            # Don't save in case no proxies supports this `protocol`
            if not len(protocols[protocol]["proxies"]) > 0:
                continue

            with open(protocols[protocol]["output_file_path"], "a") as save_proxies:
                save_proxies.write(''.join(protocols[protocol]["proxies"]))

            output_save_paths.append(protocols[protocol]["output_file_path"])

        return output_save_paths
