"""
    Info messages used through out proxycrawler
    to log out to the end-user
"""

NEW_UPDATE_FOUND = lambda latest_tag: f"[bold green][INFO] [bold white]New update found [bold yellow]`{latest_tag}`[bold white]"

NO_UPDATE_FOUND = "[bold green][INFO] [bold white]No new updates found"

USING_SERVICE = lambda service_name, service_url: f"[bold green][INFO] [bold white]Using service [bold green]'{service_name}'[bold white] with url:[bold red]'{service_url}'[bold white]"

REQUESTING_GEONODE_API = lambda api_url, payload: f"[bold green][INFO] [bold white]Requesting [bold green]Geonode[bold white]'s API at api_url:[bold green]'{api_url}'[bold white] with payload: {payload}"

REQUESTING_FREE_PROXY_LIST = lambda url: f"[bold green][INFO] [bold white]Scrapping [bold green]free-proxy-list[bold white] at url:[bold green]'{url}'[bold white]"

FOUND_A_VALID_PROXY = lambda proxy: f"[bold green][INFO] [bold white]Found a valid proxy: [bold green]{proxy.proxy}[bold white]"

PROXIES_SAVED_IN_PATHS = lambda output_file_paths: "[bold green][INFO] [bold white]Proxies saved in the following files:{}".format("".join([f"\n\t[bold green]->[bold white] {path}" for path in output_file_paths]))

FETCHING_AND_VALIDATING_PROXIES_FROM_DATABASE = f"[bold green][INFO] [bold white]Fetching and validating proxies from the database"

FETCHED_PROXIES_FROM_THE_DATABASE_VALIDATING = lambda count: f"[bold green][INFO] [bold white]Fetched [bold green]'{count}'[bold white] proxies from the database. Validating them..."

FETCHED_PROXIES_FROM_THE_DATABASE_WITHOUT_VALIDATING = lambda count: f"[bold green][INFO] [bold white]Fetched [bold green]'{count}'[bold white] proxies from the database"

VALIDATING_PROXIES_FROM_FILE = lambda proxies_count, proxy_file_path: f"[bold green][INFO] [bold white]Found [bold green]'{proxies_count}'[bold white] proxies from [bold green]'{proxy_file_path}'[bold white]. Validating them..."
