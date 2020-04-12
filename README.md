# docker-amend

```
Usage: docker-amend [OPTIONS] IMAGE COMMAND...

  Amend IMAGE by running COMMAND in a separate layer.

Options:
  -t, --tag NAME[:VERSION]        Use a different name/tag for the resulting
                                  image

  -v, --volume SOURCE:TARGET      Bind mount a volume
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.

  --help                          Show this message and exit.
```

Example usage:

```
$ docker build -t my-image .
...
$ docker-amend my-image poetry add requests
$ docker run my-image poetry show
requests         2.23.0     Python HTTP for Humans.
$ grep requests pyproject.toml
requests = ^2.23.0
```
