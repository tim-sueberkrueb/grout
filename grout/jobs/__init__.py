# -*- coding: utf-8 -*-

from grout.core.job import Job
from .snapcraft import SnapcraftJob


_declarative_name_map = {
    'snapcraft': SnapcraftJob
}


def job_by_declarative_name(name: str):
    if name in _declarative_name_map:
        return _declarative_name_map[name]
    return Job
