import httpx
import toml

with open("pyproject.toml", mode="r") as file:
	text: str = file.read()


def get_version():
	uri = "https://pypi.org/pypi/pysqlx-engine/json"
	for _ in range(3):
		resp = httpx.get(uri)
		if resp.is_success:
			break
	json: dict = resp.json()

	releases = json["releases"]
	versions = sorted(releases.keys(), key=lambda x: int(x.replace(".", "").replace("b", "")), reverse=True)
	versions = [v for v in versions if v.startswith("0.3.0") and "b" in v]
	return versions[0] if versions else "0.3.0b-1"


file_version = toml.loads(text)["tool"]["poetry"]["version"]

version: str = get_version()
print("Package version:", version)

# MAJOR, MINOR, PATCH = version.replace("b", "").split(".")
MAJOR, MINOR, PATCH = version.split(".")

PATCH, BETA = PATCH.split("b")

BETA = int(BETA) + 1

PATCH = "".join([PATCH, "b", str(BETA)])

new_version: str = ".".join([MAJOR, MINOR, str(PATCH)])

print("Package new version:", new_version)

new_text = text.replace(f'version = "{file_version}"', f'version = "{new_version}"')

with open("pyproject.toml", mode="w") as file:
	file.write(new_text)
