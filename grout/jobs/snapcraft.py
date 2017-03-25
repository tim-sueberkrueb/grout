# -*- coding: utf-8 -*-

import os.path

from grout.core import Job
from grout.core import Container


class SnapcraftJob(Job):
    _snap_filename = 'target.snap'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setup(self, c: Container, run_script: bool=True):
        super().setup(c, run_script=False)
        # Set snap name
        self._snap_filename = 'snapcraft_{}_{}.snap'.format(self.name, c.arch)
        c.log('Installing snapcraft ...')
        c.exec('apt-get', 'install', '-y', 'snapcraft')
        # Run script
        if run_script:
            self._run_script('setup', c)

    def perform(self, c: Container, run_script: bool=True):
        super().perform(c, run_script=False)
        c.exec('snapcraft', 'snap', '-o', self._snap_filename, path=self._path)
        # Run script
        if run_script:
            self._run_script('perform', c)

    def finish(self, c: Container, run_script: bool=True):
        super().finish(c, run_script=False)
        artifact_filename = os.path.join(self._artifacts_path, self._snap_filename)
        c.pull(os.path.join(self._path, self._snap_filename), self._artifacts_path)
        self._add_artifact(artifact_filename)
        # Run script
        if run_script:
            self._run_script('finish', c)
