from functools import partial
from io import BytesIO
import json
from os import getcwd
from tarfile import TarFile
from typing import List, Optional

import docker
import typer
from typer.models import Required

echo = partial(typer.echo, err=True)

client = docker.from_env()


def main(
    image_name: str = typer.Argument(Required, metavar="IMAGE"),
    command: List[str] = typer.Argument(Required),
    tag: Optional[str] = typer.Option(
        None,
        "-t",
        "--tag",
        metavar="NAME[:VERSION]",
        help="Use a different name/tag for the resulting image",
    ),
    volumes: List[str] = typer.Option(
        None,
        "-v",
        "--volume",
        metavar="SOURCE:TARGET",
        help="Bind mount a volume (assumes --no-pwd-volume)",
    ),
    no_cwd_volume: bool = typer.Option(
        False, "--no-cwd-volume", help="Do not mount cwd as a volume"
    ),
):
    """
    Amend IMAGE by running COMMAND in a separate layer.
    """

    volumes = {
        source: {"bind": bind, "mode": "rw"}
        for source, bind in (volume.split(":", 1) for volume in volumes)
    }

    if not no_cwd_volume and getcwd() not in volumes:
        working_dir = client.images.get(image_name).attrs["Config"]["WorkingDir"]
        if working_dir == "":
            echo(f"WorkingDir is not set for {image_name}, not mounting cwd")
        else:
            volumes[getcwd()] = {"bind": working_dir, "mode": "rw"}

    container = client.containers.create(
        image_name, command, volumes=volumes, detach=True
    )
    container.start()
    logs = container.attach(stdout=True, stderr=True, stream=True, logs=True)
    for line in logs:
        echo(line, nl=False)

    status_code = container.wait()["StatusCode"]
    if status_code == 0:
        container.commit(tag or image_name)
        container.remove()
    else:
        echo(
            f"Exited with code {status_code}, leaving {tag or image_name} at old version"
        )
        container.remove()


def _run():
    typer.run(main)


if __name__ == "__main__":
    _run()
