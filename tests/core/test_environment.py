# -*- coding: utf-8 -*-

from baka.core import Environment
from baka.core import Container
from baka.core import Project


class TestEnvironment:
    def test_scripts(self):
        dummy_c = Container(Project())
        env = Environment(scripts={
            'setup': "require('python', '3.5.0'); require('baka', '0.1.0')"
        })
        env.setup(dummy_c)
