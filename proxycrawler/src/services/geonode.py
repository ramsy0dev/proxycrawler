import requests

from user_agent import generate_user_agent
from rich.console import Console

from proxycrawler.messages import (
    info,
    errors
)
from proxycrawler.src.models.geonode_model import GeonodeModel

class Geonode(object):
    """ Geonode """
    url: str = "https://geonode.com/free-proxy-list"
    api_url: str = "https://proxylist.geonode.com/api/proxy-list"
    params: dict = {
        "limit": 500,
        "page": 1, # NOTE: page limit is 100
        "sort_by": "lastChecked",
        "sort_type": "desc"
    }
    valid_proxies: list[GeonodeModel] = list()

    def __init__(self, console: Console) -> None:
        self.console = console

    def fetch_proxies(self) -> list[GeonodeModel]:
        """ Fetchs the proxies from Geonode """
        page_limit = 100

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
                if proxy.validate():
                    self.valid_proxies.append(proxy)

                    self.console.log(
                        info.FOUND_A_VALID_PROXY(
                            proxy=proxy
                        )
                    )

        return self.valid_proxies
