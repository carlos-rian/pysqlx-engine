import os
import platform
import tempfile
from pathlib import Path
from typing import Literal

ENGINE_VERSION = os.environ.get(
    "PRISMA_ENGINE_VERSION", "81a0ee489e5f8c8ce98440028ea9050092430503"
)

ENGINE_URL = os.environ.get(
    "PRISMA_ENGINE_URL", "https://binaries.prisma.sh/all_commits/{0}/{1}/{2}.gz"
)

GLOBAL_TEMP_DIR = (
    Path(tempfile.gettempdir()) / "prisma" / "binaries" / "engines" / ENGINE_VERSION
)

PLATFORM_NAME = platform.system().lower()

METHOD = Literal["GET", "POST"]

IMPROVED_ERROR_LOG = True


def check_extension(filename: str) -> str:
    if PLATFORM_NAME == "windows" and ".exe" not in filename:
        if ".gz" in filename:
            return filename.replace(".gz", ".exe.gz")
        return filename + ".exe"
    return filename
