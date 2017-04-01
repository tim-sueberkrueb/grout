# -*- coding: utf-8 -*-

import unittest
import os.path

from grout.core import Container
from grout.core import Environment
from grout.core import load_project


class DeclarativeTestCase(unittest.TestCase):
    _test_backend_options = {
        'name': 'test-case-container'
    }
    _assets_path = os.path.join(os.path.dirname(__file__), 'assets')

    def test_load_project(self):
        # Test properties
        p = load_project(os.path.join(self._assets_path, 'project_base.yaml'))
        self.assertEqual(p.name, 'test-project')
        self.assertEqual(p.summary, 'Test project')
        self.assertEqual(p.description, 'A test project')
        self.assertIsInstance(p.environment, Environment)
        self.assertIsInstance(p.jobs, list)
        self.assertEqual(len(p.jobs), 1)
        job = p.jobs[0]
        self.assertEqual(job.name, 'job0')

        # Test run
        c = Container(p, backend_options=self._test_backend_options)
        c.init()
        c.setup()
        c.exec('rm', '/home/grout/job_setup')
        c.exec('rm', '/home/grout/environment_setup')
        self.assertEqual(job.name, 'setup-name')
        c.perform()
        c.exec('rm', '/home/grout/job_perform')
        c.finish()
        c.exec('rm', '/home/grout/job_finish')
        c.destroy()
