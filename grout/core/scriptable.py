# -*- coding: utf-8 -*-

from typing import Dict


class Scriptable:
    def __init__(self, scripts: Dict[str, str]=None):
        self._scripts = scripts or {}

    def _run_script(self, name: str, container):
        if name in self._scripts:
            script = self._scripts[name]
            env_locals = {
                'this': self,
                'container': container
            }
            exec(script, {}, env_locals)
