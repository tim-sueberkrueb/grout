# -*- coding: utf-8 -*-

from typing import Dict

from . import _api


class Scriptable:
    def __init__(self, scripts: Dict[str, str]=None):
        self._scripts = scripts or {}

    def _run_script(self, name: str, container):
        if name in self._scripts:
            script = self._scripts[name]
            backend = {
                'job': self,
                'container': container
            }

            def require_wrapper(module: str, min_version: str, max_version: str = None):
                return _api.require(
                    module, min_version, max_version, backend=backend
                )

            exec(script, {}, {'require': require_wrapper})
