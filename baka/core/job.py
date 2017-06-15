# -*- coding: utf-8 -*-

import os
from typing import List, Dict

from baka.core.scripting import Scriptable
from .container import Container


class Job(Scriptable):
    _home = '/home/baka'

    def __init__(self, name: str, source: str, scripts: Dict[str, str]=None, envvars: Dict[str, str]=None,
                 artifacts_path: str=None):
        super().__init__(scripts)
        self._name = name
        self._source = source
        self._source_type = 'local'
        self._envvars = envvars
        self._artifacts_path = artifacts_path or '/tmp/baka'
        # Detect source type
        if self.source.endswith('.git'):
            self._source_type = 'git'
        else:
            self._source_type = 'local'
        self._artifacts = []
        # Create artifacts dir if it doesn't exist
        if not os.path.isdir(self._artifacts_path):
            os.mkdir(self._artifacts_path)

    @property
    def name(self) -> str:
        return self._name

    @property
    def source(self) -> str:
        return self._source

    @property
    def artifacts_path(self) -> str:
        return self._artifacts_path

    @property
    def artifacts(self) -> List[str]:
        return self._artifacts

    def setup(self, c: Container, run_script=True):
        c.log('Setting up {} ...'.format(self._name))
        # Default preparation steps
        c.log('Cleaning up {} ...'.format(self._path))
        c.exec('rm', '-rf', self._path)
        # Preparing source
        if self._source_type == 'git':
            c.log('Cloning source repository ...')
            c.exec('git', 'clone', self._source, self._path)
        elif self._source_type == 'local':
            c.log('Copying sources to container ...')
            c.push(self._source, os.path.join(self._path, '..'))
            source_dir = self._source[self.source.rfind('/')+1:]
            if self._name != source_dir:
                c.exec('mv', os.path.join(self._home, source_dir), self._path)
        # Run script
        if run_script:
            self._run_script('setup', c)

    def perform(self, c: Container, run_script=True):
        c.log('Performing {} ...'.format(self._name))
        # Run script
        if run_script:
            self._run_script('perform', c)

    def finish(self, c: Container, run_script=True):
        c.log('Finishing {}...'.format(self._name))
        # Run script
        if run_script:
            self._run_script('finish', c)

    @property
    def _path(self) -> str:
        return os.path.join(self._home, self._name)

    def _path_join(self, path) -> str:
        return os.path.join(self._path, path)

    def _add_artifact(self, filepath: str):
        self._artifacts.append(filepath)
