import requests

from bs4 import BeautifulSoup
from rich.console import Console
from user_agent import generate_user_agent

from proxycrawler.messages import (
    info,
    errors
)

from proxycrawler.src.database.database_handler import  DatabaseHandler

# Models
from proxycrawler.src.models.free_proxy_list_model import FreeProxyListModel

class FreeProxyList:
    """
    This class is designed to scrape proxies from `free-proxy-list.net` using bs4

    Attributes:
        url (str): The official url for `free-proxy-list`.
        found_proxies (list[FreeProxyListModel]): A list of valid proxies represented in instances of the `FreeProxyListModel` class.
    """
    url                 :       str                         =   "https://free-proxy-list.net"
    found_proxies       :       list[FreeProxyListModel]    =   list()

    def __init__(self, database_handler: DatabaseHandler, console: Console, validate_proxies: bool | None = False):
        self.database_handler = database_handler
        self.console = console
        self.validate_proxies = validate_proxies

    def fetch_proxies(self) -> list[FreeProxyListModel]:
        """
        Fetches proxies from `free-proxy-list.com` by scrapping them.

        Args:
            None

        Returns:
            list[FreeProxyListModel]: Returns a list of valid proxies represented in instances of the `FreeProxyListModel` class.
        """
        headers = {
            "User-Agent": generate_user_agent()
        }
        self.console.log(
            info.REQUESTING_FREE_PROXY_LIST(
                url=self.url
            )
        )

        response = requests.get(
            self.url,
            headers=headers
        )

        if response.status_code != 200:
            self.console.log(
                errors.FAILD_TO_REQUEST_FREE_PROXY_LIST(
                    error=response.text
                )
            )

        soup = BeautifulSoup(
            response.content,
            "html.parser"
        )
        rows = soup.find_all("tr")

        for row in rows:
            proxy = FreeProxyListModel(
                console=self.console
            )
            parts = row.find_all("td")

            if len(parts) == 8:
                proxy.ip                  =   parts[0].text
                proxy.port                =   parts[1].text
                proxy.proxy_country_code  =   parts[2].text
                proxy.country             =   parts[3].text
                proxy.provider            =   parts[4].text
                proxy.google              =   parts[5].text
                proxy.https               =   parts[6].text
                proxy.last_checked        =   parts[7].text

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

        return self.found_proxies
