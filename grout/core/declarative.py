# -*- coding: utf-8 -*-

import yaml
import os.path

from .project import Project
from .environment import Environment
from .job import Job
from . import sources

from grout import jobs

from typing import Type


def _job_by_type(job_type: str) -> Type[Job]:
    return jobs.by_declarative_type(job_type)


def load_project(filename: str) -> Project:
    filedir = os.path.dirname(filename)

    with open(filename, 'r') as file:
        data = yaml.load(file)
    env = None
    if 'environment' in data:
        data_env = data['environment']
        assert type(data_env) == dict
        data_env_scripts = data_env['scripts']
        assert type(data_env_scripts) == dict
        env_scripts = {}
        for name in data_env_scripts:
            script = data_env_scripts[name]
            assert type(script) == str
            env_scripts[name] = script
        env = Environment(
            scripts=env_scripts
        )
    jobs = []
    if 'jobs' in data:
        data_jobs = data['jobs']
        assert type(data_jobs) == list
        for data_job in data_jobs:
            assert type(data_job) == dict
            job_scripts = {}
            source = data_job['source']
            source_type = sources.source_type(source)
            if source_type == 'local':
                source = os.path.join(filedir, source)
            if 'scripts' in data_job:
                data_job_scripts = data_job['scripts']
                assert type(data_job_scripts) == dict
                for name in data_job_scripts:
                    script = data_job_scripts[name]
                    assert type(script) == str
                    job_scripts[name] = data_job_scripts[name]
            job_envvars = None
            if 'envvars' in data_job:
                data_job_envvars = data_job['envvars']
                assert type(data_job_envvars) == dict
                job_envvars = data_job_envvars
            job = _job_by_type(data_job['type'])(
                name=data_job['name'],
                source=source,
                scripts=job_scripts,
                envvars=job_envvars
            )
            jobs.append(job)

    project = Project(
        name=data['name'],
        summary=data['summary'] if 'summary' in data else None,
        description=data['description'] if 'description' in data else None,
        environment=env,
        jobs=jobs
    )
    return project
