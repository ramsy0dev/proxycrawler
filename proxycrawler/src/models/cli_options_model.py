
class CLIOptions(object):
    """
    A model that holds CLI options
    """
    def __init__(self, enable_save_on_run: bool = True, proxy_file_path: str = None, proxies_count: int = None, group_by_protocol: bool = False, output_file_path: str = None, validate_proxies: bool = False, protocol: str = None, test_all_protocols: bool = False, debug_mode: bool = False) -> None:
        self.enable_save_on_run     =   enable_save_on_run
        self.proxy_file_path        =   proxy_file_path
        self.proxies_count          =   proxies_count
        self.group_by_protocol      =   group_by_protocol
        self.output_file_path       =   output_file_path
        self.validate_proxies       =   validate_proxies
        self.test_all_protocols     =   test_all_protocols
        self.protocol               =   protocol
        self.debug_mode             =   debug_mode
