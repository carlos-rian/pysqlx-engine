import re
import subprocess
import sys
from functools import lru_cache
from typing import Tuple

from .._config import config


@lru_cache(maxsize=None)
def binary_platform(*args, **kwargs) -> str:
    if config.platform_name != "linux":
        return config.platform_name

    distro = linux_distro()
    ssl = get_openssl()

    return "linux-musl" if distro == "alpine" else f"{distro}-openssl-{ssl}"


def linux_distro() -> str:
    dist_id, dist_like = _get_linux_distro_details()
    types = {
        "alpine": "alpine",
        "rhel": "rhel",
    }
    _name = any([_d in dist_like for _d in ["centos", "fedora", "rhel"]])
    distro = types.get(dist_id) or types.get("rhel" if _name else "")

    return distro or "debian"  # default debian


def _get_linux_distro_details() -> Tuple[str, str]:
    process = subprocess.run(
        ["cat", "/etc/os-release"], stdout=subprocess.PIPE, check=True
    )
    output = str(process.stdout, sys.getdefaultencoding())

    match = re.search(r'ID="?([^"\n]*)"?', output)
    distro_id = match.group(1) if match else ""  # type: str

    match = re.search(r'ID_LIKE="?([^"\n]*)"?', output)
    distro_id_like = match.group(1) if match else ""  # type: str
    return distro_id, distro_id_like


def get_openssl() -> str:
    process = subprocess.run(
        ["openssl", "version", "-v"], stdout=subprocess.PIPE, check=True
    )
    return parse_openssl_version(str(process.stdout, sys.getdefaultencoding()))


def parse_openssl_version(string: str) -> str:
    match = re.match(r"^OpenSSL\s(\d+\.\d+)\.\d+", string)
    return "1.1.x" if match is None else match.group(1) + ".x"
