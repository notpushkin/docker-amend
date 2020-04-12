# docker-amend

**Install**: `pipx install docker-amend` (plain `pip` works too)

**Usage**: ```docker-amend [OPTIONS] IMAGE COMMAND...```

**Example**:

```
$ docker build -t my-image .
...
$ docker-amend my-image poetry add requests
$ docker run my-image poetry show
requests         2.23.0     Python HTTP for Humans.
$ grep requests pyproject.toml
requests = ^2.23.0
```

**Options**:

* `-t, --tag NAME[:VERSION]`: Use a different name/tag for the resulting image
* `-v, --volume SOURCE:TARGET`: Bind mount a volume (assumes --no-pwd-volume)
* `--no-cwd-volume`: Do not mount cwd as a volume
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.
