# -*- coding: utf-8 -*-

from typing import Type

from .base import BaseBackend, ExecResult, NotReadyError, NetworkError
from .lxc import LXCBackend


_type_map = {
    'lxc': LXCBackend
}


class BackendNotFoundError(Exception):
    pass


def type_exists(type_name: str) -> bool:
    return type_name in _type_map.keys()


def by_type(type_name: str) -> Type[BaseBackend]:
    if type_name in _type_map:
        return _type_map[type_name]
    raise BackendNotFoundError('Container backend "{}" was requested but could not be found.'.format(type_name))
