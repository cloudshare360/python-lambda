FROM mcr.microsoft.com/devcontainers/python:3.13

ARG USERNAME=vscode

RUN apt-get update \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y --no-install-recommends \
        curl \
        zip \
        unzip \
        git \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 --no-cache-dir install --upgrade pip

USER ${USERNAME}

RUN pip3 --no-cache-dir install --user flake8 black isort pytest

WORKDIR /workspaces/python-lambda
