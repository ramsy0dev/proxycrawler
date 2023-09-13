import os

from typing import List

from sqlalchemy import (
    create_engine,
    select,
    update
)
from sqlalchemy.orm import sessionmaker

from proxycrawler import constants
from proxycrawler.src.database.tables import Base, Proxies

class DatabaseHandler (object):
    """ proxycrawler's database handler """
    def __init__(self) -> None:
        """ Initializes the DatabaseHandler. """
        self.database_url = constants.DATABASE_URL

        # Check the database url
        if not self._check_database_url():
            self._create_database()

        # Init engine
        self.engine: create_engine = self.create_engine()

        # Create tables in case they don't exist
        self.create_tables()

    def create_engine(self) -> create_engine:
        """ Creates and returns a SQLAlchemy engine object. """
        return create_engine(
            url=self.database_url,
        )

    def create_tables(self) -> None:
        """ Creates all the necessary database tables. """
        session = sessionmaker(bind=self.engine)

        with session() as session:
            Base.metadata.create_all(bind=self.engine) # Create all the tables
            session.commit()

    def save_proxy(self, proxy: Proxies) -> None:
        """
        Saves a proxy into the 'proxies' table.

        Args:
            proxy (Proxies): The proxy to be saved.

        Returns:
            None: This method doesn't return anything.
        """
        session = sessionmaker(bind=self.engine)

        with session() as session:
            # Check if the proxy already exists in the database
            if len(session.execute(select(Proxies).where(Proxies.ip == proxy.ip and Proxies.port == proxy.port)).fetchall()) > 0:
                # Check if the protocols are the same
                if len(session.execute(select(Proxies).where(Proxies.proxy == proxy.proxy and Proxies.protocols == proxy.protocols)).fetchall()) == 0:
                    session.execute(
                        update(
                            Proxies
                        ).where(
                            Proxies.proxy_id == proxy.proxy_id
                        ).values(
                            proxy=proxy.proxy,
                            protocols=proxy.protocols
                        )
                    )
                    session.commit()

                return

            # Save the proxy to the database
            session.add(proxy)
            session.commit()

    def fetch_proxies(self, proxies_count: int | None = None) -> List[tuple[Proxies]]:
        """
        Fetches proxies from the 'proxies' table.

        Args:
            proxies_count (int, optional, default: None): The number of proxies to fetch. If None, all proxies are fetched.

        Returns:
            List[tuple[Proxies]]: A list of tuples containing the fetched proxies.
        """
        session = sessionmaker(bind=self.engine)

        proxies = None
        with session() as session:
            if proxies_count is not None:
                proxies = session.execute(
                    select(Proxies).limit(proxies_count)
                ).fetchall()
            else:
                proxies = session.execute(
                    select(Proxies)
                ).fetchall()

        return proxies

    def update_proxy_valid_value(self, proxy: Proxies) -> None:
        """
        Updates the 'is_valid' value of a proxy in the 'proxies' table.

        Args:
            proxy (Proxies): The proxy to be updated.

        Returns:
            None: This method dones't return anything.
        """
        session = sessionmaker(
            bind=self.engine
        )

        with session() as session:
            session.execute(
                update(Proxies).where(
                    Proxies.proxy_id == proxy.proxy_id
                ).values(
                    is_valid=proxy.is_valid
                )
            )

            session.commit()

    def _check_database_url(self) -> bool:
        """ Checks if the database URL is valid. """
        database_path = self.database_url.replace("sqlite+pysqlite:///", "")

        return os.path.exists(database_path)

    def _create_database(self) -> None:
        """ Creates the SQLite database at the specified path. """
        database_path = self.database_url.replace("sqlite+pysqlite:///", "")

        os.makedirs(
            database_path.replace("/database.db", ""),
            exist_ok=True
        ) # Create the directory leading to the database file

        open(database_path, "a").close() # Creating the database file
