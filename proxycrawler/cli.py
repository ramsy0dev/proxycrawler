import os
import sys
import typer

from rich import print
from rich.console import Console

from proxycrawler import helpers
from proxycrawler import constants
from proxycrawler.messages import (
    info,
    errors
)
from proxycrawler.src.proxycrawler import ProxyCrawler
from proxycrawler.src.database.database_handler import DatabaseHandler

from proxycrawler.src.models.cli_options_model import CLIOptions

# Init cli
cli = typer.Typer()

# Init console
console = Console()

# Configuring console
console._log_render.omit_repeated_times = False # Repeat the timestamp even if the logs were logged on the same time

@cli.command()
def version():
    """ proxycrawler's version """
    print(f"[bold white]Version [bold cyan]{constants.VERSION}[bold white]")

@cli.command()
def scrap(
    enable_save_on_run: bool = typer.Option(True, "--enable-save-on-run", help="Save valid proxies while proxycrawler is still running (can be useful in case of a bad internet connection)"),
    group_by_protocol: bool = typer.Option(False, "--group-by-protocol", help="Save proxies into seperate files based on the supported protocols [http, https, socks4, sock5]"),
    output_file_path: str = typer.Option(None, "--output-file-path", help="Costum output file path to save results (.txt)"),
    validate_proxies: bool = typer.Option(False, "--validate", help="Validate each proxy that was found (this will make the scrapper run more slower)"),
    debug_mode: bool = typer.Option(False, "--debug-mode", help="Enable debug mode.")
):
    """ Start scrapping proxies """
    cli_options = CLIOptions(
        enable_save_on_run=enable_save_on_run,
        group_by_protocol=group_by_protocol,
        output_file_path=output_file_path,
        validate_proxies=validate_proxies,
        debug_mode=debug_mode
    )

    # Check output file path
    if cli_options.output_file_path is not None and not os.path.exists("/".join(cli_options.output_file_path.split("/")[:-1])):
        console.log(
            errors.UNVALID_OUTPUT_FILE_PATH(
                output_file_path=cli_options.output_file_path
            )
        )
        sys.exit(1)

    # Init database handler
    database_handler = DatabaseHandler()

    # Init ProxyCrawler
    proxy_crawler = ProxyCrawler(
        database_handler=database_handler,
        console=console,
        cli_options=cli_options
    )

    # Fetching proxies and validating them
    proxy_crawler.crawl_proxies()

@cli.command()
def export_db(
    proxies_count: int = typer.Option(None, "--proxies-count", help="Number of proxies to export (exports all by default)"),
    validate_proxies: bool = typer.Option(False, "--validate", help="Validate proxies"),
    group_by_protocol: bool = typer.Option(False, "--group-by-protocol", help="Save proxies into seperate files based on the supported protocols [http, https, sock4, sock5]"),
    output_file_path: str = typer.Option(None, "--output-file-path", help="Costum output file path to save results (.txt)"),
    debug_mode: bool = typer.Option(False, "--debug-mode", help="Enable debug mode.")
):
    """ Export proxies from the database """
    cli_options = CLIOptions(
        proxies_count=proxies_count,
        group_by_protocol=group_by_protocol,
        output_file_path=output_file_path,
        validate_proxies=validate_proxies,
        debug_mode=debug_mode
    )

    # Check output file path
    if cli_options.output_file_path is not None and not os.path.exists("/".join(cli_options.output_file_path.split("/")[:-1])):
        console.log(
            errors.UNVALID_OUTPUT_FILE_PATH(
                output_file_path=cli_options.output_file_path
            )
        )
        sys.exit(1)

    # Init database handler
    database_handler = DatabaseHandler()

    # Init proxycrawler
    proxy_crawler = ProxyCrawler(
        database_handler=database_handler,
        console=console,
        cli_options=cli_options
    )

    console.log(
        info.FETCHING_AND_VALIDATING_PROXIES_FROM_DATABASE
    )

    proxy_crawler.export_database_proxies()

@cli.command()
def validate(
    proxy_file_path: str = typer.Option(None, "--proxy-file", help="path to the proxy file"),
    protocol: str = typer.Option(None, "--protocol", help="Set a specific protocol to test the proxies on"),
    test_all_protocols: bool = typer.Option(False, "--test-all-protocols", help="Test all the protocols on a proxy"),
    group_by_protocol: bool = typer.Option(False, "--group-by-protocol", help="Save proxies into seperate files based on the supported protocols [http, https, sock4, sock5]"),
    output_file_path: str = typer.Option(None, "--output-file-path", help="Costum output file path to save results (.txt)"),
    debug_mode: bool = typer.Option(False, "--debug-mode", help="Enable debug mode.")
):
    """ Validate a proxies list file """
    cli_options = CLIOptions(
        proxy_file_path=proxy_file_path,
        protocol=protocol,
        group_by_protocol=group_by_protocol,
        output_file_path=output_file_path,
        test_all_protocols=test_all_protocols,
        debug_mode=debug_mode
    )

    # Init database handler
    database_handler = DatabaseHandler()

    # Init proxycrawler
    proxy_crawler = ProxyCrawler(
        database_handler=database_handler,
        console=console,
        cli_options=cli_options
    )

    # Check output file path
    if cli_options.output_file_path is not None and not os.path.exists("/".join(cli_options.output_file_path.split("/")[:-1])):
        console.log(
            errors.UNVALID_OUTPUT_FILE_PATH(
                output_file_path=cli_options.output_file_path
            )
        )
        sys.exit(1)

    # Check if the proxies file exists
    if not os.path.exists(cli_options.proxy_file_path):
        console.log(errors.PROXY_FILE_DOESNT_EXIST)
        sys.exit(1)

    # Check the file's extension
    if not cli_options.proxy_file_path.endswith(".txt"):
        console.log(errors.FILE_EXTENSION_NOT_SUPPORTED)
        sys.exit(1)

    # Check the format of the proxies
    proxies = [proxy.strip() for proxy in open(cli_options.proxy_file_path, "r").readlines()]
    results = []

    for proxy in proxies:
        if not proxy_crawler.check_proxy_fromat(proxy=proxy):
            results.append(proxy)

    if len(results) != 0:
        console.log(errors.UNVALID_PROXY_FORMAT)
        sys.exit(1)

    # Check the protocol
    if cli_options.protocol is not None and cli_options.protocol not in cli_options.protocols:
        console.log(
            errors.UNVALID_PROXY_PROTOCOL(
                protocol=protocol
            )
        )
        sys.exit(1)

    # Validate the list of proxies
    console.log(
        info.VALIDATING_PROXIES_FROM_FILE(
            proxies_count=len(proxies),
            proxy_file_path=cli_options.proxy_file_path
        )
    )

    proxy_crawler.validate_proxies(proxies=proxies)

@cli.command()
def update():
    """ Update proxycrawler """
    with console.status("Checking for new updates") as status:
        is_to_update, latest_tag = helpers.check_for_update()

        if not is_to_update:
            console.log(info.NO_UPDATE_FOUND)
            sys.exit(0)

        console.log(info.NEW_UPDATE_FOUND(latest_tag=latest_tag))

        status.update(f"Updating proxycrawler to [bold yellow]`{latest_tag}`")
        helpers.self_update()

        console.log(f"[bold green][INFO][reset] proxycrawler updated to [bold yellow]`{latest_tag}`")

def run():
    """ Runs proxycrawler """
    helpers.banner()
    cli()
