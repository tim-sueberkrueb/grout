# -*- coding: utf-8 -*-

import os.path

from baka.core import Job
from baka.core import Container


class SnapcraftJob(Job):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._snap_filename = 'snapcraft_{}.snap'.format(self.name)

    def setup(self, c: Container, run_script: bool=True):
        super().setup(c, run_script=False)
        c.log('Installing snapcraft ...')
        c.exec('apt-get', 'install', '-y', 'snapcraft')
        # Run script
        if run_script:
            self._run_script('setup', c)

    def perform(self, c: Container, run_script: bool=True):
        super().perform(c, run_script=False)
        c.exec('snapcraft', 'snap', '-o', self._snap_filename, path=self.path, envvars=self._envvars)
        # Run script
        if run_script:
            self._run_script('perform', c)

    def finish(self, c: Container, run_script: bool=True):
        super().finish(c, run_script=False)
        artifact_filename = os.path.join(self._artifacts_path, self._snap_filename)
        c.pull(os.path.join(self.path, self._snap_filename), self._artifacts_path)
        self._add_artifact(artifact_filename)
        # Run script
        if run_script:
            self._run_script('finish', c)
