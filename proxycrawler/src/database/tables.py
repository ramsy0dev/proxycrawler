from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    DateTime,
    JSON
)

from sqlalchemy.orm import DeclarativeBase

from proxycrawler import helpers

class Base(DeclarativeBase):
    """ Base """
    pass

# Tables
class Proxies(Base):
    """ Proxies table model for storing proxy information. """
    __tablename__ = "proxies"

    # Columns
    proxy_id    =   Column(String, primary_key=True)
    ip          =   Column(String(30))
    port        =   Column(Integer)
    proxy       =   Column(JSON)
    protocols   =   Column(String)
    country     =   Column(String(10))
    is_valid    =   Column(Boolean, default=True)
    added_at    =   Column(DateTime, default=helpers.date())

    def __repr__(self) -> str:
        return f"Proxies(proxy_id={self.proxy_id!r}, ip={self.ip!r}, port={self.port!r}, proxy={self.proxy!r}, protocols={self.protocols!r}, country={self.country!r}, is_valid={self.is_valid!r}, added_at={self.added_at!r})"
