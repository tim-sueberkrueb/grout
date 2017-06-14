# -*- coding: utf-8 -*-


class Project:
    def __init__(self, name: str=None, summary: str=None, description: str=None, environment=None, jobs=None):
        self.name = name
        self.summary = summary
        self.description = description
        self.environment = environment or None
        self.jobs = jobs or []
