# -*- coding: utf-8 -*-


def source_type(source: str) -> str:
    if source.endswith('.git'):
        return 'git'
    else:
        return 'local'
