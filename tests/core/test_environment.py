# -*- coding: utf-8 -*-

from baka.core import Environment
from baka.core import Container
from baka.core import Project


class _TestEnvironment(Environment):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_attribute = None


class TestEnvironment:
    def test_scripts(self):
        test_string = 'Hello Environment'
        dummy_c = Container(Project())
        env = _TestEnvironment(scripts={
            'setup': 'this.test_attribute = "{}"'.format(test_string)
        })
        env.setup(dummy_c)
        assert env.test_attribute == test_string
