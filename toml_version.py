import httpx

with open("pyproject.toml", mode="r") as file:
    text: str = file.read()


def get_version():
    uri = "https://pypi.org/pypi/pysqlx-engine/json"
    for _ in range(3):
        resp = httpx.get(uri)
        if resp.is_success:
            break
    json: dict = resp.json()
    return json["info"]["version"]


version: str = get_version()
print("Package version:", version)

MAJOR, MINOR, PATCH = version.split(".")

PATCH = int(PATCH) + 1

new_version: str = ".".join([MAJOR, MINOR, str(PATCH)])

print("Package new version:", new_version)

new_text = text.replace(f'version = "{version}"', f'version = "{new_version}"')

with open("pyproject.toml", mode="w") as file:
    file.write(new_text)
