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
    _binary_path: str = f"{Path(__package__).absolute()}/.binary"

    def download(self) -> None:
        local_path = self._read_local_binary_path()
        if local_path:
            log.debug(f"{self.name} is cached, skipping download")
            return

        url = self.url
        dest = self.path
        if dest.exists():
            log.debug(f"{self.name} is cached, skipping download")
            self._write_local_binary_path(to=str(dest.absolute()))
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
        self._write_local_binary_path(to=to)

        # remove temporary files
        os.remove(tar)
        os.remove(tmp)

    def _write_local_binary_path(self, to: str):
        with open(self._binary_path, mode="wb") as file:
            file.write(to.encode())

    def _read_local_binary_path(self) -> str:
        if not Path(self._binary_path).exists():
            return
        with open(self._binary_path, mode="rb") as file:
            data = file.read().decode()
        return data

    @property
    def binary_path(self) -> str:
        path = self._read_local_binary_path()
        if not path:
            self.download()
            return self._read_local_binary_path()
        return path

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
