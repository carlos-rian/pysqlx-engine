import socket
from pathlib import Path

import aiofiles
from pydantic import BaseModel


def get_open_port() -> int:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("", 0))
    port = sock.getsockname()[1]
    sock.close()
    return int(port)


async def get_dml() -> str:
    path = f"{Path(__file__).parent.absolute()}/schema.prisma"
    async with aiofiles.open(path, mode="r") as file:
        content = await file.read()
    return content


class BaseRow(BaseModel):
    ...
