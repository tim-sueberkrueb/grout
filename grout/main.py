# -*- coding: utf-8 -*-

import os
import click

import grout.core


@click.command()
@click.option('--path', default=None, help='Path to project')
@click.option('--project-file', default='project.yaml', help='Project declaration file')
@click.option('--container-name', default=None, help='Container name')
@click.option('--container-image', default=None, help='Container image')
@click.option('--container-arch', default=None, help='Container arch')
@click.option('--container-ephemeral', 'container_ephemeral', flag_value=True, help='Set container ephemeral')
@click.option('--container-persistent', 'container_ephemeral', flag_value=False, help='Set container persistent')
def main(path: str = None, project_file: str = 'project.yaml',
         container_name: str = None, container_image: str = None,
         container_arch: str = None, container_ephemeral: bool = True):
    """Grout a simple tool and library for continuous, clean builds using LXC/LXD

    Grout was primarily created to be used in combination with Snapcraft.
    """
    cwd = os.getcwd()
    if not path:
        path = cwd
    filepath = os.path.join(path, project_file)
    grout.core.run_declarative(
        filepath, container_name=container_name, container_image=container_image,
        container_arch=container_arch, container_ephemeral=container_ephemeral
    )


if __name__ == '__main__':
    main()
