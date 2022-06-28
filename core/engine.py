import asyncio
import logging
import subprocess
import sys
from os import environ
from pathlib import Path
from typing import List

import httpx
from binary import check_binary

from core.abc import AbstractEngine

from . import common
from .errors import AlreadyConnectedError, EngineConnectionError

log: logging.Logger = logging.getLogger()


class Engine(AbstractEngine):
    def __init__(
        self,
        url: str = None,
        process: subprocess.Popen = None,
        session: httpx.AsyncClient = None,
    ) -> None:
        self.url: str = url
        self.process: subprocess.Popen = process
        self.session: httpx.AsyncClient = session
        self._binary_path: Path = None

    async def connect(self) -> None:
        if not self.process:
            raise AlreadyConnectedError("Already connected to the engine")

        self.session: httpx.AsyncClient = await httpx.AsyncClient()
        self._binary_path = check_binary()

        try:
            await self.spawn(file=Path(self._binary_path))
        except Exception:
            await self.disconnect()
            raise

    async def spawn(self, file: Path) -> None:
        port = common.get_open_port()
        log.debug(f"Running engine on port: {port}")

        self.url = f"http://localhost:{port}"

        dml = """
            generator client {
                provider = "prisma-client-py"
            }
            datasource db {
                provider = "postgresql"
                url      = env("DATABASE_URL")
            }
        """

        env = environ.copy()

        env.update(
            PRISMA_DML=dml,
            RUST_LOG="error",
            RUST_LOG_FORMAT="json",
            PRISMA_CLIENT_ENGINE_TYPE="binary",
        )

        args: List[str] = [str(file.absolute()), "-p", str(port), "--enable-raw-queries"]

        log.debug("Starting engine...")
        self.process = subprocess.Popen(
            args,
            env=env,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )

    async def check(self, timeout: int = 10):
        last_exc = None
        for _ in range(int(timeout / 0.1)):
            try:
                data = await self.session.get("/status")
                resp = data.json()
                if data.is_success and resp.get("status", "") == "ok":
                    return True
            except Exception as exc:
                last_exc = exc
                log.debug(
                    "Could not connect to query engine due to %s; retrying...",
                    type(exc).__name__,
                )
                await asyncio.sleep(0.1)

            if data.get("Errors") is not None:
                log.debug("Could not connect due to gql errors; retrying...")
                await asyncio.sleep(0.1)
                break
        else:
            raise EngineConnectionError(
                "Could not connect to the engine..."
            ) from last_exc
