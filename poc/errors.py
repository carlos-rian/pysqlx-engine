"""
Connection pool errors.
"""

# Copyright (C) 2021 The Psycopg Team


class PoolClosed(Exception):
    """Attempt to get a connection from a closed pool."""

    __module__ = "psycopg_pool"


class PoolTimeout(Exception):
    """The pool couldn't provide a connection in acceptable time."""

    __module__ = "psycopg_pool"


class TooManyRequests(Exception):
    """Too many requests in the queue waiting for a connection from the pool."""

    __module__ = "psycopg_pool"


class OperationalError(Exception): ...


class ConnectionTimeout(OperationalError):
    """Timeout waiting for a connection from the pool."""

    __module__ = "psycopg_pool"
