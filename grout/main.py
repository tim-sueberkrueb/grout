# -*- coding: utf-8 -*-

import os
import click

import grout.core


@click.command()
@click.option('--path', default=None, help='Path to project')
@click.option('--project-file', default='project.yaml', help='Project declaration file')
@click.option('--container-name', default=None, help='Container name')
def main(path: str = None, project_file: str = 'project.yaml',
         container_name: str = None):
    """Grout a simple tool and library for continuous, clean builds using LXC/LXD

    Grout was primarily created to be used in combination with Snapcraft.
    """
    cwd = os.getcwd()
    if not path:
        path = cwd
    filepath = os.path.join(path, project_file)
    grout.core.run_declarative(filepath, container_name=container_name)


if __name__ == '__main__':
    main()
