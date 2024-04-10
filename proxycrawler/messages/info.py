"""
    Info messages used through out proxycrawler
    to log out to the end-user
"""

def NEW_UPDATE_FOUND(latest_tag) -> str:
    return f"[bold green][INFO][reset] New update found [bold yellow]`{latest_tag}`[bold white]"

NO_UPDATE_FOUND = "[bold green][INFO][reset] No new updates found"

def USING_SERVICE(service_name, service_url) -> str:
    return f"[bold green][INFO][reset] Using service [bold green]'{service_name}'[bold white] with url:[bold red]'{service_url}'[bold white]"

def REQUESTING_GEONODE_API(api_url, payload) -> str:
    return f"[bold green][INFO][reset] Requesting [bold green]Geonode[bold white]'s API at api_url:[bold green]'{api_url}'[bold white] with payload: {payload}"

def REQUESTING_FREE_PROXY_LIST(url) -> str:
    return f"[bold green][INFO][reset] Scrapping [bold green]free-proxy-list[bold white] at url:[bold green]'{url}'[bold white]"

def FOUND_A_VALID_PROXY(proxy) -> str:
    return f"[bold green][INFO][reset] Found a valid proxy: [bold green]{proxy.proxy}[bold white]"

def PROXIES_SAVED_IN_PATHS(output_file_paths) -> str:
    return "[bold green][INFO][reset] Proxies saved in the following files:{}".format("".join([f"\n\t[bold green]->[bold white] {path}" for path in output_file_paths]))

FETCHING_AND_VALIDATING_PROXIES_FROM_DATABASE = "[bold green][INFO][reset] Fetching and validating proxies from the database"

def FETCHED_PROXIES_FROM_THE_DATABASE_VALIDATING(count) -> str:
    return f"[bold green][INFO][reset] Fetched [bold green]'{count}'[bold white] proxies from the database. Validating them..."

def FETCHED_PROXIES_FROM_THE_DATABASE_WITHOUT_VALIDATING(count) -> str:
    return f"[bold green][INFO][reset] Fetched [bold green]'{count}'[bold white] proxies from the database"

def VALIDATING_PROXIES_FROM_FILE(proxies_count, proxy_file_path) -> str:
    return f"[bold green][INFO][reset] Found [bold green]'{proxies_count}'[bold white] proxies from [bold green]'{proxy_file_path}'[bold white]. Validating them..."
