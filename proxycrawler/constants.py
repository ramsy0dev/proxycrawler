import os

# Package main info
PACKAGE = "proxycrawler"
VERSION = "0.2.0"
AUTHOR = "ramsy0dev"
GITHUB = "https://github.com/ramsy0dev/proxycrawler"

# Banner
BANNER = f"""[bold white]
                                                          __
    ____  _________  _  ____  ________________ __      __/ /__  _____
   / __ \/ ___/ __ \| |/_/ / / / ___/ ___/ __ `/ | /| / / / _ \/ ___/
  / /_/ / /  / /_/ />  </ /_/ / /__/ /  / /_/ /| |/ |/ / /  __/ /
 / .___/_/   \____/_/|_|\__, /\___/_/   \__,_/ |__/|__/_/\___/_/ Version [bold cyan]{VERSION}[bold white]
/_/                    /____/
                            Made by [bold green]`ramsy0dev`[bold white]
"""

# Home path
HOME = os.path.expanduser("~")

# Database URL
DATABASE_URL = f"sqlite+pysqlite:///{HOME}/.proxycrawler/database.db"

# Debug proxycrawler
DEBUG = False # Set this to True to enable debug mode
