# -*- coding: utf-8 -*-

import unittest

import os.path

from grout.core import Project
from grout.core import Container, NotReadyError


class ContainerTestCase(unittest.TestCase):
    _test_container_name = 'test-case-container'
    _temp_dir = os.path.join('/tmp', 'grout-tests')

    def test_properties(self):
        p = Project()
        name = self._test_container_name
        c = Container(
            p, name=name
        )
        self.assertEqual(c.name, name)
        self.assertFalse(c.ready)

    def test_run(self):
        # Setup
        p = Project()
        c = Container(
            p, self._test_container_name
        )
        c.init()
        self.assertEqual(c.ready, True)
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
        self.assertTrue(os.path.isfile(os.path.join(self._temp_dir, 'test2.txt')))

        # Finish
        c.perform()
        c.finish()

        # Destroy
        c.destroy()
        self.assertEqual(c.ready, False)

    def test_not_ready(self):
        p = Project()
        c = Container(p, self._test_container_name)
        self.assertFalse(c.ready)
        methods = (
            c.run, c.setup, c.perform, c.finish,
            c.destroy, c.exec, c.push, c.pull
        )
        for m in methods:
            self.assertRaises(NotReadyError, m)
