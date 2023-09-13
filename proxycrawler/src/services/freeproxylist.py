import requests

from rich.console import Console
from bs4 import BeautifulSoup
from user_agent import generate_user_agent

from proxycrawler.messages import (
    info,
    errors
)
from proxycrawler.src.models.free_proxy_list_model import FreeProxyListModel

class FreeProxyList(object):
    """ free-proxy-list.net """
    url: str = "https://free-proxy-list.net"
    valid_proxies: list[FreeProxyListModel] = list()

    def __init__(self, console: Console):
        self.console = console

    def fetch_proxies(self) -> list[FreeProxyListModel]:
        """ Fetches proxies with filter `country_code` """
        headers = {
            "User-Agent": generate_user_agent()
        }
        self.console.log(info.REQUESTING_FREE_PROXY_LIST(url=self.url))

        response = requests.get(
            self.url,
            headers=headers
        )

        if response.status_code != 200:
            self.console.log(errors.FAILD_TO_REQUEST_FREE_PROXY_LIST(error=response.text))

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

                if proxy.https == "yes":
                    # Check if the proxy already exists and validate the proxy
                    if proxy.validate():
                        self.valid_proxies.append(proxy)

                        self.console.log(info.FOUND_A_VALID_PROXY(proxy=proxy))
