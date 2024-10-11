from typing import Union

from ..aconn import PySQLXEngine
from ..conn import PySQLXEngineSync


def validate_uri(uri: str):
	_providers = ["postgresql", "mysql", "sqlserver", "sqlite"]
	if not uri or not any([uri.startswith(prov) for prov in [*_providers, "file"]]):
		raise ValueError(f"invalid uri: {uri}, check the usage uri, accepted providers: {', '.join(_providers)}")


TPySQLXEngineConn = Union[PySQLXEngine, PySQLXEngineSync]
