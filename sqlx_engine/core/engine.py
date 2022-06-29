import asyncio
import json
import logging
import subprocess
from os import environ
from pathlib import Path
from typing import Any, Dict, List

import httpx

from ..binary import check_binary
from ..binary.const import METHOD
from . import common
from .abc import AbstractEngine
from .errors import (
    AlreadyConnectedError,
    BaseStartEngineError,
    EngineConnectionError,
    EngineRequestError,
    NotConnectedError,
    StartEngineError,
    UnprocessableEntityError,
    handler_error,
)

log: logging.Logger = logging.getLogger()


class AsyncEngine(AbstractEngine):
    def __init__(
        self,
        db_uri: str,
        db_provider: str,
        db_timeout: int = 10,
        url: str = None,
        process: subprocess.Popen = None,
        session: httpx.AsyncClient = None,
    ) -> None:
        self.db_uri = db_uri
        self.db_provider = db_provider
        self.db_timeout = db_timeout

        self.url: str = url
        self.process: subprocess.Popen = process
        self.session: httpx.AsyncClient = session
        self.connected = False
        self._binary_path: Path = None

    async def _close(self):
        if self.session and not self.session.is_closed:
            await self.session.aclose()
        self.session = None

    async def connect(self) -> None:
        if self.process:
            raise AlreadyConnectedError("Already connected to the engine")

        self.session: httpx.AsyncClient = httpx.AsyncClient()
        self._binary_path = check_binary()

        try:
            await self.spawn(file=Path(self._binary_path))
        except Exception:
            await self._close()
            raise

    async def disconnect(self) -> None:
        await self._close()
        if not self.process:
            raise NotConnectedError("Not connected")

        self.url = None
        self.process.kill()
        self.process = None
        self.connected = False

    async def spawn(self, file: Path) -> None:
        port = common.get_open_port()
        log.debug(f"Running engine on port: {port}")

        self.url = f"http://localhost:{port}"

        dml = await common.get_dml()

        dml = dml.replace("postgres", self.db_provider)
        dml = dml.replace("DATASOURCE_URL", self.db_uri)

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
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        start_err = None #self.process.stderr.readlines()
        if start_err:
            stderr = start_err[0].decode()
            try:
                data = json.loads(stderr)
                raise StartEngineError(error=data)
            except (json.JSONDecodeError, TypeError):
                raise BaseStartEngineError(stderr)

        await self._check_connect()

    async def request(
        self, method: METHOD, path: str, *, content: Any = None
    ) -> Dict[str, Any]:
        if not self.url:
            raise NotConnectedError("Not connected to the engine")

        kwargs = {
            "headers": {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        }

        if content:
            kwargs["content"] = content

        url = self.url + path
        log.debug(f"Sending {method} request to {url} with content: {content}")

        resp = await self.session.request(method=method, url=url, **kwargs)

        if resp.is_success:
            response = resp.json()

            log.debug(f"{method} {url} returned {len(response)} results")

            errors_data = response.get("errors")
            if errors_data:
                return handler_error(errors=errors_data)

            return response

        elif resp.status == 422:
            raise UnprocessableEntityError(resp)

        raise EngineRequestError(f"{resp.status_code}: {resp.text}")

    async def _check_connect(self) -> None:
        last_err = None
        for _ in range(int(self.db_timeout / 0.1)):
            try:
                data = await self.request("GET", "/status")
                if data.get("status", "") == "ok":
                    self.connected = True
                    return
            except Exception as err:
                await asyncio.sleep(0.1)
                log.debug(
                    (
                        "Could not connect to engine due to "
                        f"{err.__class__.__name__}; retrying..."
                    )
                )
                last_err = err

        raise EngineConnectionError("Could not connect to the engine") from last_err
