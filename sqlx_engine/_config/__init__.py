import platform
import tempfile
from pathlib import Path
from typing import Literal

from pydantic import BaseConfig


class Config(BaseConfig):
    improved_error_log: bool = True
    platform_name: str = platform.system().lower()
    method: Literal = Literal["GET", "POST"]
    engine_version: str = "9f27eed0f8b8773287ff09e657bfa267983e5948"
    # engine_version: str = "81a0ee489e5f8c8ce98440028ea9050092430503"
    engine_url: str = "https://binaries.prisma.sh/all_commits/{0}/{1}/{2}.gz"
    global_temp_dir: Path = (
        Path(tempfile.gettempdir()) / "prisma" / "binaries" / "engines" / engine_version
    )


config = Config()


def check_extension(filename: str) -> str:
    if config.platform_name == "windows" and ".exe" not in filename:
        if ".gz" in filename:
            return filename.replace(".gz", ".exe.gz")
        return filename + ".exe"
    return filename
