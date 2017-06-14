# -*- coding: utf-8 -*-

import os.path

from baka.core import run_declarative


class TestSnapcraft:
    _assets_path = os.path.join(os.path.dirname(__file__), 'assets')
    _test_backend_options = {
        'name': 'test-case-container'
    }

    def test_snap_declarative(self):
        project_path = os.path.join(self._assets_path, 'test-project')
        assert os.path.isdir(project_path)
        run_declarative(
            os.path.join(project_path, 'project.yaml'),
            backend_options=self._test_backend_options
        )
