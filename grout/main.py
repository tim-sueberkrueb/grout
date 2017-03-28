# -*- coding: utf-8 -*-

import os
import click

from typing import Tuple

import grout.core


@click.command()
@click.option('--path', default=None, help='Path to project')
@click.option('--project-file', default='project.yaml', help='Project declaration file')
@click.option('--container-name', default=None, help='Container name')
@click.option('--container-image', default=None, help='Container image')
@click.option('--container-arch', default=None, help='Container arch')
@click.option('--container-ephemeral', 'container_ephemeral', flag_value=True, help='Set container ephemeral')
@click.option('--container-persistent', 'container_ephemeral', flag_value=False, help='Set container persistent')
@click.option('--skip', 'skip_jobs', default=None, multiple=True, help='Skip a list of jobs by name separated by spaces')
@click.option('--skip-environment', 'skip_environment', flag_value=True, help='Skip environment setup')
def main(path: str = None, project_file: str = 'project.yaml',
         container_name: str = None, container_image: str = None,
         container_arch: str = None, container_ephemeral: bool = True,
         skip_jobs: Tuple[str] = None, skip_environment: bool = False):
    """Grout a simple tool and library for continuous, clean builds using LXC/LXD

    Grout was primarily created to be used in combination with Snapcraft.
    """
    cwd = os.getcwd()
    if not path:
        path = cwd
    filepath = os.path.join(path, project_file)
    grout.core.run_declarative(
        filepath, container_name=container_name, container_image=container_image,
        container_arch=container_arch, container_ephemeral=container_ephemeral,
        skip_jobs=skip_jobs, skip_environment=skip_environment
    )


if __name__ == '__main__':
    main()
