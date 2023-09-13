"""
    Errors messages used through out proxycrawler
    to log out to the end-user
"""

FILE_EXTENSION_NOT_SUPPORTED = f"[bold red][ERROR] [bold white]The provided proxy file's extension is not supported. Please make sure it's a plain text file (.txt) and try again"

PROXY_FILE_DOESNT_EXIST = f"[bold red][ERROR] [bold white]The provided proxy file path doesn't seem to exists. Please verify it and try again"

UNVALID_OUTPUT_FILE_PATH = lambda output_file_path: f"[bold red][ERROR] [bold white]Unvalid output file path [bold red]'{output_file_path}'[bold white]. Please change it and try again (or you can leave it empty)"

FAILD_TO_REQUEST_GEONODE_API = lambda error: f"[bold red][ERROR] [bold white]Faild to request [bold green]geonode[bold white]'s API. Error: {error}"
FAILD_TO_REQUEST_FREE_PROXY_LIST = lambda error: f"[bold red][ERROR] [bold white]Faild to request [bold green]free-proxy-list.net[bold white]. Error: {error}"

UNVALID_COUNTRY_CODE = lambda country_code, supported_country_code: f"[bold red][ ! ] [bold white]Unvalid country code [bold red]'{country_code}'[bold white]. Supported country code: \n{supported_country_code}"

UNVALID_PROXY_FORMAT = f"[bold red][ERROR] [bold white]Unvalid proxies format. Format should be [bold green]<protocol>://ip:port[bold white]. Please fix it and try again"

UNVALID_PROXY_PROTOCOL = lambda protocol, protocols: f"[bold red][ERROR] [bold white]Unvalid proxy protocol [bold red]'{protocol}'. the supported protocols are [bold green]{protocols}[bold white] (you may keep --protocol null to test it on all protocols)"

NO_PROXIES_WHERE_GATHERED = lambda proxies: f"[bold red][ERROR] [bold white]No proxies where gathered. proxies:[bold red]{proxies}[bold white]"

NO_PROXIES_WHERE_FOUND_IN_THE_DATABASE = "[bold red][ERROR] [bold white]No proxies where found in the database"
