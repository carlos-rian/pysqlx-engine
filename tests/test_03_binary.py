from io import StringIO
from pathlib import Path

from dotenv import load_dotenv
from sqlx_engine._binary.engine import Engine


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


def test_04_download_remove_dot_binary():
    engine = Engine()
    Path(engine._binary_path).unlink(missing_ok=True)

    assert engine.download() is None
    assert engine.path.exists()
    assert engine.path.parent.exists()


def test_05_download_with_dot_binary():
    engine = Engine()

    assert engine.download() is None
    assert engine.path.exists()
    assert engine.path.parent.exists()


def test_06_binary_path_dot_binary():
    engine = Engine()

    path = engine.binary_path
    assert isinstance(path, str)


def test_07_binary_path_dot_binary():
    engine = Engine()
    Path(engine._binary_path).unlink(missing_ok=True)
    path = engine.binary_path
    assert isinstance(path, str)


def test_08_get_path_custom():
    env = StringIO("DIR_LOCAL_ENGINE_BINARY=.")
    load_dotenv(stream=env)

    engine = Engine()
    path = engine.path
    assert path == Path(".")
