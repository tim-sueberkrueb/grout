# -*- coding: utf-8 -*-

from grout.core.job import Job
from .snapcraft import SnapcraftJob


_declarative_type_map = {
    'snapcraft': SnapcraftJob
}


def by_declarative_type(type_name: str):
    if type_name in _declarative_type_map:
        return _declarative_type_map[type_name]
    return Job
