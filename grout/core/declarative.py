# -*- coding: utf-8 -*-

import yaml
import pykwalify.core
import os.path

from .project import Project
from .environment import Environment
from .job import Job
from . import sources

from grout import jobs

from typing import Type


def _extended_job(job_name: str) -> Type[Job]:
    return jobs.job_by_declarative_name(job_name)


def _validate(source_data: str):
    validator = pykwalify.core.Core(
        source_data=source_data,
        schema_files=[
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'validation/project_schema.yaml'
            )
        ]
    )
    validator.validate(raise_exception=True)


def load_project(filename: str) -> Project:
    filedir = os.path.dirname(filename)

    with open(filename, 'r') as file:
        data = yaml.load(file)

    _validate(data)

    env = None

    if 'environment' in data:
        data_env = data['environment']
        data_env_scripts = data_env['scripts']
        env_scripts = {}
        for name in data_env_scripts:
            script = data_env_scripts[name]
            env_scripts[name] = script
        env = Environment(
            scripts=env_scripts
        )
    jobs = []
    if 'jobs' in data:
        data_jobs = data['jobs']
        for data_job in data_jobs:
            job_scripts = {}
            source = data_job['source']
            source_type = sources.source_type(source)
            if source_type == 'local':
                source = os.path.abspath(os.path.join(filedir, source))
            if 'scripts' in data_job:
                data_job_scripts = data_job['scripts']
                for name in data_job_scripts:
                    job_scripts[name] = data_job_scripts[name]
            job_envvars = None
            if 'envvars' in data_job:
                data_job_envvars = data_job['envvars']
                job_envvars = data_job_envvars
            job_extends = 'base'
            if 'extends' in data_job:
                job_extends = data_job['extends']
            elif 'type' in data_job:
                print(
                    'Warning: Using "type" to specify a job to extend is deprecated.'
                    'Use "extends" instead.'
                )
                job_extends = data_job['type']
            job = _extended_job(job_extends)(
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
