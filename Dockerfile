FROM bitnami/minideb:latest
RUN install_packages python3 python3-pip python3-setuptools python3-wheel
RUN pip3 install poetry
RUN ln -s /usr/bin/python3 /usr/bin/python
ENV POETRY_VIRTUALENVS_CREATE false
WORKDIR /opt/docker-amend
