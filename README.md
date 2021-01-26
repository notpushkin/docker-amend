# docker-amend

Amend Docker images by running a command in a temporary container.

```console
$ pipx install docker-amend  # (plain `pip` works too)
$ docker-amend [OPTIONS] IMAGE[:VERSION] COMMAND...
```

## Description

docker-amend lets you modify an IMAGE by running COMMAND inside a temporary container.
You can use it to add dependencies to your project without rebuilding the whole image
from ground.

This is basically `docker run` and `docker commit` in one go, but easier to use.

## Options

* `-t, --tag NAME[:VERSION]`: Use a different name/tag for the resulting image.
* `-v, --volume SOURCE[:TARGET[:MODE]]`: Bind mount a volume.
* `--no-cwd-volume`: Do not mount current working directory as a volume.  [default: False]
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

## Example

Let's say you're making a Python app:

```console
$ docker build -t my-image .

... (some development goes on, then:)

$ docker-amend my-image poetry add requests
$ docker run my-image poetry show
requests         2.23.0     Python HTTP for Humans.
$ grep requests pyproject.toml
requests = ^2.23.0
```
