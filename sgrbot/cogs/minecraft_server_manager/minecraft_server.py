from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Optional

import docker
from docker.errors import NotFound

from .errors import ServerStartFailed

if TYPE_CHECKING:
    import datetime

    from discord import InteractionMessage


class MinecraftServer:
    def __init__(self, *, name: str, docker_image_name: str, docker_image_tag: str,
                 container_name: str, volumes: str, ports: str, environment: dict, address: str) -> None:
        self.name = name
        self.address = address

        self.docker_client = docker.from_env()

        try:
            self.container = self.docker_client.containers.get(container_name)
        except NotFound:
            self.container = self.docker_client.containers.create(f"{docker_image_name}:{docker_image_tag}",
                                                                  name=container_name,
                                                                  volumes=volumes,
                                                                  ports=ports,
                                                                  environment=environment,
                                                                  detach=True)

        self.is_processing: bool = False
        self.status_interaction_message: Optional[InteractionMessage] = None

    @property
    def is_running(self) -> bool:
        if not self.container:
            return False

        self.container.reload()

        if self.container.status != "running":
            return False

        return True

    async def wait_until_ready(self, dt: datetime.datetime) -> None:
        while True:
            self.container.reload()

            logs = self.container.logs(since=dt).decode("utf-8")
            if "Done" in logs:
                break

            if self.container.status != "running":
                raise ServerStartFailed(self)

            await asyncio.sleep(5)

    def start(self) -> None:
        self.container.start()

    def stop(self) -> None:
        self.container.stop()

    def restart(self) -> None:
        self.stop()
        self.start()
