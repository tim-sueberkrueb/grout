# -*- coding: utf-8 -*-

import os.path
import pytest

from grout.core import Project
from grout.core import Container, NotReadyError


class TestContainer:
    _test_backend_options = {
        'name': 'test-case-container'
    }
    _temp_dir = os.path.join('/tmp', 'grout-tests')

    def test_options(self):
        p = Project()
        c = Container(
            p, backend_options=self._test_backend_options
        )
        assert c.name == self._test_backend_options['name']
        assert not c.ready

    def test_run(self):
        # Setup
        p = Project()
        c = Container(
            p, backend_options=self._test_backend_options
        )
        c.init()
        assert c.ready
        c.setup()

        # Test push/pull & exec
        filepath = os.path.join(self._temp_dir, 'test.txt')
        if not os.path.isdir(self._temp_dir):
            os.mkdir(self._temp_dir)
        with open(filepath, 'w') as file:
            file.write('lorem ipsum dolor sit amet')
        c.push(filepath, '/home/grout/')
        c.exec('mv', '/home/grout/test.txt', '/home/grout/test2.txt')
        c.pull('/home/grout/test2.txt', self._temp_dir)
        assert os.path.isfile(os.path.join(self._temp_dir, 'test2.txt'))

        # Finish
        c.perform()
        c.finish()

        # Destroy
        c.destroy()
        assert not c.ready

    def test_not_ready(self):
        p = Project()
        c = Container(p, backend_options=self._test_backend_options)
        assert not c.ready
        methods = (
            c.run, c.setup, c.perform, c.finish,
            c.destroy, c.exec, c.push, c.pull
        )
        for m in methods:
            with pytest.raises(NotReadyError):
                m()
