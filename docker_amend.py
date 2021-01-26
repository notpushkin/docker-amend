from functools import partial
from os import getcwd
from os.path import abspath, normpath
from typing import Iterable, List, Optional, Tuple

import docker
import typer
from typer.models import Required

echo = partial(typer.echo, err=True)

client = docker.from_env()


def _parse_volumes(volumes: Iterable[str]) -> List[Tuple[str, dict]]:
    def _parse_volume(volume: str) -> dict:
        parts = volume.split(":")
        if len(parts) > 3:
            raise typer.BadParameter(
                f"volume '{volume}' has incorrect format, should be SOURCE[:TARGET[:MODE]]",
            )

        source = abspath(parts[0])
        target = normpath(parts[1]) if len(parts) > 1 else source

        return source, {
            "bind": target,
            "mode": parts[2] if len(parts) > 2 else "rw",
        }

    return dict(_parse_volume(volume) for volume in volumes)


def main(
    image_name: str = typer.Argument(Required, metavar="IMAGE[:VERSION]"),
    command: List[str] = typer.Argument(Required),
    tag: Optional[str] = typer.Option(
        None,
        "-t",
        "--tag",
        metavar="NAME[:VERSION]",
        help="Use a different name/tag for the resulting image.",
    ),
    volumes: List[str] = typer.Option(
        None,
        "-v",
        "--volume",
        metavar="SOURCE[:TARGET[:MODE]]",
        help="Bind mount a volume.",
        callback=_parse_volumes,
    ),
    no_cwd_volume: bool = typer.Option(
        False,
        "--no-cwd-volume",
        help="Do not mount current working directory as a volume.",
    ),
):
    """
    Amend IMAGE by running COMMAND in a separate layer.
    """

    if tag is None:
        tag = image_name

    if not no_cwd_volume and getcwd() not in volumes:
        working_dir = client.images.get(
            image_name,
        ).attrs["Config"]["WorkingDir"]
        if working_dir == "":
            echo(f"WorkingDir is not set for {image_name}, not mounting cwd")
        else:
            volumes[getcwd()] = {"bind": working_dir, "mode": "rw"}

    container = client.containers.create(
        image_name, command, volumes=volumes, detach=True,
    )
    container.start()
    for line in container.attach(stdout=True, stderr=True, stream=True, logs=True):
        # TODO: attach stdout to stdout
        echo(line, nl=False)

    status_code = container.wait()["StatusCode"]
    if status_code == 0:
        container.commit(tag)
        container.remove()
    else:
        echo(
            f"\nExited with code {status_code}, leaving {tag} at old version. If you still want to override it, run:\n"
            + f"  docker commit {container.id} {tag}",
        )


def _run():
    typer.run(main)


if __name__ == "__main__":
    _run()
