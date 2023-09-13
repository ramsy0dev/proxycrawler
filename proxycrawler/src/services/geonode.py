import requests

from user_agent import generate_user_agent
from rich.console import Console

from proxycrawler.messages import (
    info,
    errors
)
from proxycrawler.src.models.geonode_model import GeonodeModel

class Geonode(object):
    """
    This class is designed to interface with the Geonode.com API to retrieve proxy data. Geonode.net offers up to 5000 proxies, and this class accomplishes this by sending HTTP requests with specified parameters such as 'limit,' 'page,' 'sort_by,' and 'sort_type.' Of particular importance is the 'page' parameter, which has a limit of 100. This means that in order to obtain all 5000 proxies, we need to send about 100 requests to the API. Each request yields a JSON response containing a 'data' key, which holds a list of dictionaries containing proxy information. It's important to note that each response is limited to approximately 500 proxies.

    Attributes:
        url (str): The official url for `Geonode.com`.
        api_url (str): The URL of the API used for communication to retrieve proxies from Geonode.com.
        params (dict): A dictionary containing the parameters accepted by the API for fetching proxies.
        valid_proxies (list[GeonodeModel]): A list of valid proxies represented as instances of the `GeonodeModel` class.
    """
    url: str = "https://geonode.com/free-proxy-list"
    api_url: str = "https://proxylist.geonode.com/api/proxy-list"
    params: dict = {
        "limit": 500,
        "page": 1, # NOTE: page limit is 100
        "sort_by": "lastChecked",
        "sort_type": "desc"
    }
    valid_proxies: list[GeonodeModel] = list()

    def __init__(self, console: Console | None = None) -> None:
        self.console = console

    def fetch_proxies(self) -> list[GeonodeModel]:
        """
        Fetchs the proxies from Geonode's API

        Args:
            None

        Returns:
            list[GeonodeModel]: Returns a list of valid proxies represented as instances of the `GeonodeModel` class
        """
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
