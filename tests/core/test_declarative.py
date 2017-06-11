# -*- coding: utf-8 -*-

import os.path

from grout.core import Container
from grout.core import Environment
from grout.core import load_project


class DeclarativeTestCase:
    _test_backend_options = {
        'name': 'test-case-container'
    }
    _assets_path = os.path.join(os.path.dirname(__file__), 'assets')

    def test_load_project(self):
        # Test properties
        p = load_project(os.path.join(self._assets_path, 'project_base.yaml'))
        assert p.name == 'test-project'
        assert p.summary == 'Test project'
        assert p.description == 'A test project'
        assert isinstance(p.environment, Environment)
        assert isinstance(p.jobs, list)
        assert len(p.jobs) == 1
        job = p.jobs[0]
        assert job.name == 'job0'

        # Test run
        c = Container(p, backend_options=self._test_backend_options)
        c.init()
        c.setup()
        c.exec('rm', '/home/grout/job_setup')
        c.exec('rm', '/home/grout/environment_setup')
        assert job.name == 'setup-name'
        c.perform()
        c.exec('rm', '/home/grout/job_perform')
        c.finish()
        c.exec('rm', '/home/grout/job_finish')
        c.destroy()
