# -*- coding: utf-8 -*-

from typing import Dict

import abc


class NotReadyError(Exception):
    pass


class NetworkError(Exception):
    pass


class ExecResult:
    def __init__(self, exit_code: int, output: str):
        self._exit_code = exit_code
        self._output = output

    @property
    def exit_code(self) -> int:
        return self._exit_code

    @property
    def output(self) -> str:
        return self._output


class BaseBackend(metaclass=abc.ABCMeta):
    def __init__(self, container, options: Dict=None):
        self._container = container
        self._ready = False
        self._options = options or {}
        # Apply default options
        default_options = self._default_options
        for def_key in default_options:
            if def_key not in self._options or self._options[def_key] is None:
                self._options[def_key] = default_options[def_key]

    @property
    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def image(self) -> str:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def arch(self) -> str:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def ephemeral(self) -> bool:
        raise NotImplementedError()

    @property
    def _default_options(self) -> Dict:
        return {}

    @property
    def options(self) -> Dict:
        return self._options

    @property
    def ready(self) -> bool:
        return self._ready

    def log(self, *fragments):
        self._container.log(*fragments)

    @abc.abstractmethod
    def init(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def destroy(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def exec(self, command, *args, path: str = None, envvars: Dict[str, str]=None) -> ExecResult:
        raise NotImplementedError()

    @abc.abstractmethod
    def push(self, source: str, dest: str):
        raise NotImplementedError()

    @abc.abstractmethod
    def pull(self, source: str, dest: str):
        raise NotImplementedError()
