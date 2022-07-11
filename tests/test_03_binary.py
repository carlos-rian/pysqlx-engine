from io import StringIO
from pathlib import Path

import pytest
from dotenv import load_dotenv
from httpx import HTTPStatusError
from sqlx_engine._binary.download import check_binary
from sqlx_engine._binary.engine import Engine
from sqlx_engine._config import config


def test_01_platform_linux():
    from sqlx_engine._binary.platform import binary_platform

    name = binary_platform()
    assert name == "debian-openssl-1.1.x"


def test_02_platform_windows():
    from sqlx_engine._binary.platform import binary_platform, config

    platform_name = config.platform_name

    config.platform_name = "windows"
    name = binary_platform("try")
    assert name == "windows"

    config.platform_name = platform_name


def test_03_download_without_dot_binary():
    engine = Engine()
    Path(engine._binary_path).unlink(missing_ok=True)

    # remove file and folder where save binary
    engine.path.unlink(missing_ok=True)
    engine.path.parent.rmdir()

    assert engine.download() is None

    assert engine.path.exists()
    assert engine.path.parent.exists()


def test_04_download_with_dot_binary():
    engine = Engine()

    assert engine.download() is None
    assert engine.path.exists()
    assert engine.path.parent.exists()


def test_05_binary_path_with_dot_binary():
    engine = Engine()

    path = engine.binary_path
    assert isinstance(path, str)


def test_06_binary_path_without_dot_binary():
    engine = Engine()
    Path(engine._binary_path).unlink(missing_ok=True)
    path = engine.binary_path
    assert isinstance(path, str)


def test_07_linux_get_url():
    engine = Engine()
    url = engine.url
    assert isinstance(url, str)
    assert url.startswith("https://binaries.prisma.sh")
    assert url.endswith("query-engine.gz")


def test_08_windows_get_url():
    engine = Engine()
    config.platform_name = "windows"
    url = engine.url
    assert isinstance(url, str)
    assert url.startswith("https://binaries.prisma.sh")
    assert url.endswith("query-engine.exe.gz")


def test_09_windows_get_url_without_dot_gz():
    engine = Engine()
    config.platform_name = "windows"
    config.engine_url = config.engine_url.replace(".gz", "")
    url = engine.url
    assert isinstance(url, str)
    assert url.startswith("https://binaries.prisma.sh")
    assert url.endswith("query-engine.exe")


def test_10_download_http_status_error():
    engine_version = config.engine_version
    path = config.global_temp_dir

    config.global_temp_dir = Path(str(path).replace(engine_version, "error"))
    config.engine_version = "error"

    engine = Engine()
    Path(engine._binary_path).unlink(missing_ok=True)

    with pytest.raises(HTTPStatusError):
        check_binary("test-binary")

    config.engine_version = engine_version
    config.global_temp_dir = path
