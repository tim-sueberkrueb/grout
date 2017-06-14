# -*- coding: utf-8 -*-

from typing import Tuple, Dict

from .declarative import load_project
from .container import Container
from .project import Project


def run(project: Project, backend_type: str = None, backend_options: Dict = None,
        skip_jobs: Tuple[str] = None, skip_environment: bool = True):
    container = Container(project, backend_type=backend_type, backend_options=backend_options)
    container.init()
    container.run(skip_jobs=skip_jobs, skip_environment=skip_environment)
    if container.ephemeral:
        container.destroy()


def run_declarative(filename: str, backend_type: str = None, backend_options: Dict=None,
                    skip_jobs: Tuple[str] = None, skip_environment: bool = True,
                    artifacts_path: str = None):
    project = load_project(filename, artifacts_path=artifacts_path)
    run(project, backend_type, backend_options, skip_jobs, skip_environment)
