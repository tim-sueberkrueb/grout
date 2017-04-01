# -*- coding: utf-8 -*-

import os
import click

from typing import Tuple

import grout.core
import grout.core.backend


@click.command()
@click.option('--path', default=None, help='Path to project')
@click.option('--project-file', default='project.yaml', help='Project declaration file')
@click.option('--skip', 'skip_jobs', default=None, multiple=True, help='Skip a job by its name')
@click.option('--skip-environment', 'skip_environment', flag_value=True, help='Skip environment setup')
@click.option('--backend', 'backend_type', default='lxc', help='Container backend to use')
@click.option('--name', 'backend_name', default=None, help='Container backend name')
@click.option('--image', 'backend_image', default=None, help='Container backend image')
@click.option('--arch', 'backend_arch', default=None, help='Container backend arch')
@click.option('--persistent', 'backend_ephemeral', flag_value=False, help='Set container persistent')
def main(path: str = None, project_file: str = 'project.yaml',
         skip_jobs: Tuple[str] = None, skip_environment: bool = False,
         backend_type: str = 'lxc', backend_name: str = None, backend_image: str = None,
         backend_arch: str = None, backend_ephemeral: bool = True):
    """Grout a simple tool and library for continuous, clean builds.

    Grout was primarily created to be used in combination with Snapcraft.
    """
    cwd = os.getcwd()
    if not path:
        path = cwd
    filepath = os.path.join(path, project_file)
    if not grout.core.backend.type_exists(backend_type):
        raise click.ClickException('The requested container backend "{}" could not be found.'.format(backend_type))
    backend_options = {
        'name': backend_name,
        'image': backend_image,
        'arch': backend_arch,
        'ephemeral': backend_ephemeral
    }
    grout.core.run_declarative(
        filepath, backend_type=backend_type, backend_options=backend_options,
        skip_jobs=skip_jobs, skip_environment=skip_environment
    )


if __name__ == '__main__':
    main()
