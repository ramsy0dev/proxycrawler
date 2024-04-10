import requests

from rich.console import Console
from user_agent import generate_user_agent

from proxycrawler.messages import (
    info,
    errors
)

from proxycrawler.src.database.database_handler import DatabaseHandler

# Models
from proxycrawler.src.models.geonode_model import GeonodeModel

class Geonode:
    """
    This class is designed to interface with the Geonode.com API to retrieve proxy data. Geonode.net offers up to 5000 proxies, and this class accomplishes this by sending HTTP requests with specified parameters such as 'limit,' 'page,' 'sort_by,' and 'sort_type.' Of particular importance is the 'page' parameter, which has a limit of 100. This means that in order to obtain all 5000 proxies, we need to send about 100 requests to the API. Each request yields a JSON response containing a 'data' key, which holds a list of dictionaries containing proxy information. It's important to note that each response is limited to approximately 500 proxies.

    Attributes:
        url (str): The official url for `Geonode.com`.
        api_url (str): The URL of the API used for communication to retrieve proxies from Geonode.com.
        params (dict): A dictionary containing the parameters accepted by the API for fetching proxies.
        valid_proxies (list[GeonodeModel]): A list of valid proxies represented as instances of the `GeonodeModel` class.
        saved_proxies (list[str]): A list of proxies that were saved to the output file.
    """
    url                 :       str                 =   "https://geonode.com/free-proxy-list"
    api_url             :       str                 =   "https://proxylist.geonode.com/api/proxy-list"
    params              :       dict                =   {
                "limit": 500,
                "page": 1, # NOTE: page limit is 10
                "sort_by": "lastChecked",
                "sort_type": "desc"
            }
    found_proxies       :       list[GeonodeModel]  =   list()
    saved_proxies       :       list[str]           =   list()

    def __init__(self, database_handler: DatabaseHandler, save_proxies_to_file, enable_save_on_run: bool | None = True, group_by_protocol: bool | None = False, output_file_path: str | None = None, validate_proxies: bool | None = False, console: Console | None = None) -> None:
        self.database_handler = database_handler
        self.save_proxies_to_file = save_proxies_to_file
        self.enable_save_on_run = enable_save_on_run
        self.group_by_protocol = group_by_protocol
        self.output_file_path = output_file_path
        self.validate_proxies = validate_proxies
        self.console = console

    def fetch_proxies(self) -> list[GeonodeModel]:
        """
        Fetchs the proxies from Geonode's API

        Args:
            None

        Returns:
            list[GeonodeModel]: Returns a list of valid proxies represented as instances of the `GeonodeModel` class
        """
        page_limit = 10

        for page_number in range(1, page_limit):
            payload = self.params
            payload["page"] = page_number
            headers = {
                "Host": "proxylist.geonode.com",
                "User-Agent": generate_user_agent(),
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate", # Remove 'br' from accepted encoding because the response content is not readable
                "Origin": "https://geonode.com",
                "Connection": "keep-alive",
                "Referer": "https://geonode.com/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-site"
            }

            proxies = None

            try:
                self.console.log(
                    info.REQUESTING_GEONODE_API(
                        api_url=self.api_url,
                        payload=payload
                    )
                )

                response = requests.get(
                    self.api_url,
                    params=payload,
                    headers=headers
                )
                
                if response.status_code != 200:
                    continue

                proxies = response.json()["data"]
            except Exception as error:
                self.console.log(
                    errors.FAILD_TO_REQUEST_GEONODE_API(
                        error=error
                        )
                    )

            # In case no proxies where retrieved just return `None`
            if proxies is None:
                continue

            # Validating proxies
            for proxy_info in proxies:
                proxy = GeonodeModel(
                    console=self.console
                )

                proxy.set_fields(
                    data=proxy_info
                )

                self.found_proxies.append(proxy)

                proxy_table = proxy.export_table_row()
                
                if self.validate_proxies:
                    if proxy.validate():
                        proxy_table.is_valid = True
                else:
                    # Since we don't know what protocols does the proxy support
                    # we will just set it to all.
                    proxy.proxy = {
                        "http": f"http://{proxy.ip}:{proxy.port}",
                        "socks4": f"socks4://{proxy.ip}:{proxy.port}",
                        "socks5": f"socks5://{proxy.ip}:{proxy.port}",
                    }
                    proxy.protocols = ["http", "socks4", "socks5"]
                
                # Save to database
                self.database_handler.save_proxy(proxy=proxy_table)

                self.console.log(
                    info.FOUND_A_VALID_PROXY(
                        proxy=proxy
                    )
                )

                if not self.enable_save_on_run:
                    continue

                # Save the proxy to the database in case `enable_save_on_run`
                self.database_handler.save_proxy(
                    proxy=proxy.export_table_row()
                )

            # Save to the output file in case `enable_save_on_run`
            if not self.enable_save_on_run:
                continue

            self.save_proxies_to_file(
                proxies=[proxy for proxy in self.found_proxies if proxy not in self.saved_proxies]
            )

            self.saved_proxies = [*self.saved_proxies, *self.found_proxies]

        return self.found_proxies
