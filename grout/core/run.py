# -*- coding: utf-8 -*-

from .declarative import load_project
from .container import Container
from .project import Project


def run(project: Project, container_name: str = None, container_image: str = None,
        container_arch: str = None, container_ephemeral: bool = True):
    container = Container(
        project, name=container_name, image=container_image,
        arch=container_arch, ephemeral=container_ephemeral)
    container.init()
    container.run()
    if container.ephemeral:
        container.destroy()


def run_declarative(filename: str, container_name: str = None, container_image: str = None,
                    container_arch: str = None, container_ephemeral: bool = True):
    project = load_project(filename)
    run(project, container_name, container_image, container_arch, container_ephemeral)
