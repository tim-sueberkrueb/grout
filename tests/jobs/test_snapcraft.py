# -*- coding: utf-8 -*-

import unittest
import os.path

from grout.core import run_declarative


class SnapcraftTestCase(unittest.TestCase):
    _assets_path = os.path.join(os.path.dirname(__file__), 'assets')
    _test_container_name = 'test-case-container'

    def test_snap_declarative(self):
        project_path = os.path.join(self._assets_path, 'test-project')
        self.assertTrue(os.path.isdir(project_path))
        run_declarative(
            os.path.join(project_path, 'project.yaml'),
            container_name=self._test_container_name
        )
