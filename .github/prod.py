import os
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

	return json["info"]["version"]


file_version = toml.loads(text)["tool"]["poetry"]["version"]

current_version: str = get_version()
print("Package version:", current_version)

if file_version.replace(".", "") > current_version.replace(".", ""):
	MAJOR, MINOR, PATCH = file_version.split(".")

else:
	MAJOR, MINOR, PATCH = current_version.split(".")
	PATCH = str(int(PATCH) + 1)

new_version: str = ".".join([MAJOR, MINOR, PATCH])

print("Package new version:", new_version)

new_text = text.replace(f'version = "{file_version}"', f'version = "{new_version}"')

with open("pyproject.toml", mode="w") as file:
	file.write(new_text)

env_file = os.getenv("GITHUB_ENV")

with open(env_file, mode="a") as file:
	file.write(f"\nPY_SQLX_VERSION=v{new_version}")
