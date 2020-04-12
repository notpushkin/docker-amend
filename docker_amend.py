from functools import partial
from io import BytesIO
import json
from os import getcwd
from tarfile import TarFile
from typing import List, Optional

import docker
import typer

echo = partial(typer.echo, err=True)

client = docker.from_env()


def main(
    image_name: str,
    command: List[str],
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
    no_cwd_volume: bool = typer.Option(False, help="Do not mount cwd as a volume"),
):
    """
    Amend IMAGE by running COMMAND in a separate layer.
    """

    if not no_cwd_volume:
        working_dir = client.images.get(image_name).attrs["Config"]["WorkingDir"]
        if working_dir == "":
            echo(f"WorkingDir is not set for {image_name}, not mounting cwd")
        else:
            volumes = [f"{getcwd()}:{working_dir}"]

    volumes = {
        source: {"bind": bind, "mode": "rw"}
        for source, bind in (volume.split(":", 1) for volume in volumes)
    }
    print(volumes)

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

    ## Alternate implementation:
    # dockerfile = BytesIO(
    #     f"""
    #     FROM {image_name}
    #     RUN {json.dumps(command)}
    #     """.encode()
    # )

    # image_name, logs = client.images.build(
    #     path=getcwd(), fileobj=dockerfile, tag=tag or image_name,
    # )

    # if export_files:
    #     echo("Exporting updated files from the image...")


def _run():
    typer.run(main)


if __name__ == "__main__":
    _run()
