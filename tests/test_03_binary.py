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
