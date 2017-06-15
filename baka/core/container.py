# -*- coding: utf-8 -*-

import os

from typing import Callable, Any, Dict, Tuple

from . import project
from . import backend


def _require_ready(f: Callable[..., Any]):
    def wrapper(this, *args, **kwargs):
        if not this.ready:
            raise backend.NotReadyError('This container has not yet been initialized.')
        return f(this, *args, **kwargs)
    return wrapper


class Container:
    def __init__(self, project_: project.Project,
                 backend_type: str = None, backend_options: Dict = None):
        self._project = project_
        if backend_type:
            self._backend_type = backend_type
        else:
            if 'BAKA_DEFAULT_BACKEND' in os.environ:
                self._backend_type = os.environ['BAKA_DEFAULT_BACKEND']
            else:
                self._backend_type = 'lxc'
        self._backend_class = backend.by_type(self._backend_type)
        self._backend = self._backend_class(self, backend_options)

    @property
    def name(self) -> str:
        return self._backend.name

    @property
    def image(self) -> str:
        return self._backend.image

    @property
    def arch(self) -> str:
        return self._backend.arch

    @property
    def ephemeral(self) -> bool:
        return self._backend.ephemeral

    @property
    def ready(self):
        return self._backend.ready

    def init(self):
        if self.ready:
            print('Warning: Container already initialized.')
            return
        self._backend.init()

    @_require_ready
    def run(self, skip_jobs: Tuple[str]=None, skip_environment: bool=False):
        self.setup(skip_jobs=skip_jobs, skip_environment=skip_environment)
        self.perform(skip_jobs=skip_jobs)
        self.finish(skip_jobs=skip_jobs)

    @_require_ready
    def setup(self, skip_jobs: Tuple[str]=None, skip_environment: bool=False):
        env = self._project.environment
        if env and not skip_environment:
            self.log('Setting up the project environment ...')
            env.setup(self)
        self.log('Setting up jobs ...')
        for job in self._project.jobs:
            if not skip_jobs or (job.name not in skip_jobs and job.name + '.setup' not in skip_jobs):
                job.setup(self)

    @_require_ready
    def perform(self, skip_jobs: Tuple[str]=None):
        self.log('Performing jobs ...')
        for job in self._project.jobs:
            if not skip_jobs or (job.name not in skip_jobs and job.name + '.perform' not in skip_jobs):
                job.perform(self)

    @_require_ready
    def finish(self, skip_jobs: Tuple[str]=None):
        self.log('Finishing ...')
        for job in self._project.jobs:
            if not skip_jobs or (job.name not in skip_jobs and job.name + '.finish' not in skip_jobs):
                job.finish(self)

    @_require_ready
    def destroy(self):
        self._backend.destroy()

    @_require_ready
    def exec(self, command, *args, path: str = None, envvars: Dict[str, str]=None,
             collect_output: bool = False, log_output: bool = True) -> backend.CommandResult:
        return self._backend.exec(
            command, *args, path=path, envvars=envvars, collect_output=collect_output,
            log_output=log_output
        )

    def log(self, *fragments):
        print(*fragments, end='' if fragments[-1].endswith('\n') else '\n')

    @_require_ready
    def push(self, source: str, dest: str):
        self._backend.push(source, dest)

    @_require_ready
    def pull(self, source: str, dest: str):
        self._backend.pull(source, dest)
