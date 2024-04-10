"""
    Errors messages used through out proxycrawler
    to log out to the end-user
"""

def FAILD_TO_UPDATE(error) -> str:
    return f"[bold red][ERROR][reset] Faild to update, the following error was raised: {error}"

FILE_EXTENSION_NOT_SUPPORTED = "[bold red][ERROR][reset] The provided proxy file's extension is not supported. Please make sure it's a plain text file (.txt) and try again"

PROXY_FILE_DOESNT_EXIST = "[bold red][ERROR][reset] The provided proxy file path doesn't seem to exists. Please verify it and try again"

def UNVALID_OUTPUT_FILE_PATH(output_file_path) -> str:
    return f"[bold red][ERROR][reset] Unvalid output file path [bold red]'{output_file_path}'[reset]. Please change it and try again (or you can leave it empty)"

def FAILD_TO_REQUEST_GEONODE_API(error) -> str:
    return f"[bold red][ERROR][reset] Faild to request [bold green]geonode[reset]'s API. Error: {error}"

def FAILD_TO_REQUEST_FREE_PROXY_LIST(error) -> str:
    return f"[bold red][ERROR][reset] Faild to request [bold green]free-proxy-list.net[reset]. Error: {error}"

def UNVALID_COUNTRY_CODE(country_code, supported_country_code) -> str:
    return f"[bold red][ ! ] [reset]Unvalid country code [bold red]'{country_code}'[reset]. Supported country code: \n{supported_country_code}"

UNVALID_PROXY_FORMAT = "[bold red][ERROR][reset] Unvalid proxies format. Format should be [bold green]<protocol>://ip:port[reset]. Please fix it and try again"

def UNVALID_PROXY_PROTOCOL(protocol, protocols) -> str:
    return f"[bold red][ERROR][reset] Unvalid proxy protocol [bold red]'{protocol}'. the supported protocols are [bold green]{protocols}[reset] (you may keep --protocol null to test it on all protocols)"

def NO_PROXIES_WHERE_GATHERED(proxies) -> str:
    return f"[bold red][ERROR][reset] No proxies where gathered. proxies:[bold red]{proxies}[reset]"

NO_PROXIES_WHERE_FOUND_IN_THE_DATABASE = "[bold red][ERROR][reset] No proxies where found in the database"
