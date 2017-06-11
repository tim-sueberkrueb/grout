# -*- coding: utf-8 -*-

from grout.core import Environment
from grout.core import Container
from grout.core import Project


class _TestEnvironment(Environment):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_attribute = None


class EnvironmentTestCase:
    def test_scripts(self):
        test_string = 'Hello Environment'
        dummy_c = Container(Project())
        env = _TestEnvironment(scripts={
            'setup': 'this.test_attribute = "{}"'.format(test_string)
        })
        env.setup(dummy_c)
        assert env.test_attribute == test_string
