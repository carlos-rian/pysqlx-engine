import re
import subprocess
import sys
from functools import lru_cache
from typing import Tuple

from .version import PLATFORM_NAME


# 01 =======GET PLATFORM NAME=========
@lru_cache(maxsize=None)
def binary_platform() -> str:
    if PLATFORM_NAME != "linux":
        return PLATFORM_NAME

    distro = linux_distro()
    if distro == "alpine":
        return "linux-musl"

    ssl = get_openssl()
    return f"{distro}-openssl-{ssl}"


# 02 =======GET LINUX DISTRO==========
def linux_distro() -> str:
    distro_id, distro_id_like = _get_linux_distro_details()
    if distro_id == "alpine":
        return "alpine"
    if any(distro in distro_id_like for distro in ["centos", "fedora", "rhel"]):
        return "rhel"
    return "debian"


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


# 03 ======GET OPEN SSL VERSION=======
def get_openssl() -> str:
    process = subprocess.run(
        ["openssl", "version", "-v"], stdout=subprocess.PIPE, check=True
    )
    return parse_openssl_version(str(process.stdout, sys.getdefaultencoding()))


def parse_openssl_version(string: str) -> str:
    match = re.match(r"^OpenSSL\s(\d+\.\d+)\.\d+", string)
    if match is None:
        # default
        return "1.1.x"

    return match.group(1) + ".x"
