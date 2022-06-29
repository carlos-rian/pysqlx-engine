import gzip
import logging
import os
import shutil
from os import environ
from pathlib import Path

import httpx
from pydantic import BaseModel

from .const import ENGINE_URL, ENGINE_VERSION, GLOBAL_TEMP_DIR, check_extension
from .platform import binary_platform

log: logging.Logger = logging.getLogger()


class Engine(BaseModel):
    name: str = "query-engine"
    env: str = "PRISMA_QUERY_ENGINE_BINARY"
    _session: httpx.Client = httpx.Client()

    def download(self) -> None:
        url = self.url
        dest = self.path
        if dest.exists():
            log.debug(f"{self.name} is cached, skipping download")
            return

        log.debug(f"Downloading from {url} to {dest}")
        self._download(url=url, to=str(dest.absolute()))
        log.debug(f"Downloaded {self.name} to {dest.absolute()}")

    def _download(self, url: str, to: str):
        if Path(to).exists():
            Path(to).parent.unlink()

        Path(to).parent.mkdir(parents=True, exist_ok=True)
        tmp = to + ".tmp"
        tar = to + ".gz.tmp"

        with self._session.stream("GET", url, timeout=None) as resp:
            resp.raise_for_status()
            with open(tar, "wb") as fd:
                for chunk in resp.iter_bytes():
                    fd.write(chunk)

        # decompress to a tmp file before replacing the original
        with gzip.open(tar, "rb") as f_in:
            with open(tmp, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

        # chmod +x
        status = os.stat(tmp)
        os.chmod(tmp, status.st_mode | 0o111)

        # override the original
        shutil.copy(tmp, to)

        # remove temporary files
        os.remove(tar)
        os.remove(tmp)

    @property
    def binary_path(self) -> str:
        if not self.path:
            self.download()
        return str(self.path)

    @property
    def url(self) -> str:
        return check_extension(
            ENGINE_URL.format(ENGINE_VERSION, binary_platform(), self.name)
        )

    @property
    def path(self) -> Path:
        env = environ.get(self.env)
        if env is not None:
            log.debug(f"Using environment variable location: {env} for {self.name}")
            return Path(env)

        binary_name = binary_platform()
        return Path(
            check_extension(
                str(GLOBAL_TEMP_DIR.joinpath(f"prisma-{self.name}-{binary_name}"))
            )
        )
