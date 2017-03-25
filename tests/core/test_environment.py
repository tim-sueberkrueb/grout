# -*- coding: utf-8 -*-

import unittest

from grout.core import Environment
from grout.core import Container
from grout.core import Project


class _TestEnvironment(Environment):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_attribute = None


class EnvironmentTestCase(unittest.TestCase):
    def test_scripts(self):
        test_string = 'Hello Environment'
        dummy_c = Container(Project())
        env = _TestEnvironment(scripts={
            'setup': 'this.test_attribute = "{}"'.format(test_string)
        })
        env.setup(dummy_c)
        self.assertEqual(env.test_attribute, test_string)
