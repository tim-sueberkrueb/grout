# -*- coding: utf-8 -*-

import subprocess
import time
import pylxd

from typing import List, Callable, Any, Dict

from . import project


class NetworkError(Exception):
    pass


class NotReadyError(Exception):
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


class ExecGenerator:
    def __init__(self, name: str, command: str, *args, path: str = None, envvars: Dict[str, str]=None):
        self._exit_code = -1
        self._output = ''
        self._name = name
        self._command = command
        self._args = list(args)
        self._path = path
        self._env = envvars or {}
        self._expand_env()

    def __iter__(self):
        cmd = ['lxc', 'exec', self._name]
        if self._path:
            cmd += ['--env', 'HOME={}'.format(self._path)]
        for env_var in self._env.keys():
            val = self._env[env_var]
            cmd += ['--env', '{}={}'.format(env_var, val)]
        cmd += ['--', self._command] + self._args
        p = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        for line in p.stdout:
            self._output += line.decode()
            yield line.decode()
        exit_code = p.wait()
        if exit_code:
            raise subprocess.CalledProcessError(exit_code, cmd)
        self._exit_code = exit_code

    def _expand_env(self):
        default_env = {
            'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
            'LD_LIBRARY_PATH': ''
        }
        for var in self._env.keys():
            val = self._env[var]
            for def_var in default_env.keys():
                def_val = default_env[def_var]
                val = val.replace('${}'.format(def_var), def_val)
            for custom_var in self._env.keys():
                custom_val = self._env[custom_var]
                val = val.replace('${}'.format(custom_var), custom_val)
            self._env[var] = val.rstrip(':')

    @property
    def exit_code(self) -> int:
        return self._exit_code

    @property
    def output(self) -> str:
        return self._output

    @property
    def result(self) -> ExecResult:
        result = ExecResult(self._exit_code, self.output)
        return result


def _require_ready(f: Callable[..., Any]):
    def wrapper(this, *args, **kwargs):
        if not this.ready:
            raise NotReadyError('This container has not yet been initialized.')
        return f(this, *args, **kwargs)

    return wrapper


class Container:
    def __init__(self, project_: project.Project,
                 name: str = None, image: str = None, arch: str = None, ephemeral: bool = True):
        self._project = project_
        self._lxd = pylxd.Client()
        self._name = name if name else self._gen_name()
        self._image = image or 'ubuntu:xenial'
        self._arch = arch or 'amd64'
        self._ephemeral = ephemeral
        self._container = None
        self._ready = False

    @property
    def name(self) -> str:
        return self._name

    @property
    def image(self) -> str:
        return self._image

    @property
    def arch(self) -> str:
        return self._arch

    @property
    def ephemeral(self) -> bool:
        return self._ephemeral

    @property
    def ready(self):
        return self._ready

    def init(self):
        if self._ready:
            print('Warning: Container already initialized.')
            return
        self.log('Checking for container ...')
        # Find existing containers with the requested name
        existing_containers = self._lxd.containers.all()
        existing = list(filter(lambda c: c.name == self._name, existing_containers))
        # Create container or use existing one
        if len(existing) > 0:
            self.log('Launching container ...')
            self._container = existing[0]
        else:
            self.log('Creating and launching container ...')
            cmd = [
                'lxc', 'launch',
                '{}/{}'.format(self._image, self._arch),
                self._name
            ]
            if self._ephemeral:
                cmd += ['-e']
            subprocess.check_call(cmd)
            self._container = self._lxd.containers.get(self._name)
        # Start the container (if not already running)
        self._container.start()
        # Enable most actions
        self._ready = True
        # Check for netowrk connection
        self._wait_for_network()
        # Prepare system
        self._prepare()

    @_require_ready
    def run(self):
        self.setup()
        self.perform()
        self.finish()

    @_require_ready
    def setup(self):
        env = self._project.environment
        if env:
            self.log('Setting up the project environment ...')
            env.setup(self)
        self.log('Setting up jobs ...')
        for job in self._project.jobs:
            job.setup(self)

    @_require_ready
    def perform(self):
        self.log('Performing jobs ...')
        for job in self._project.jobs:
            job.perform(self)

    @_require_ready
    def finish(self):
        self.log('Finishing ...')
        for job in self._project.jobs:
            job.finish(self)

    @_require_ready
    def destroy(self):
        self.log('Destroying ...')
        subprocess.check_call(['lxc', 'delete', '-f', self._name])
        self._ready = False

    @_require_ready
    def exec(self, command, *args, path: str = None, envvars: Dict[str, str]=None) -> ExecResult:
        gen = ExecGenerator(self._name, command, *args, path=path, envvars=envvars)
        for line in gen:
            self.log(line)
        return gen.result

    def log(self, *fragments):
        print(*fragments, end='' if fragments[-1].endswith('\n') else '\n')

    @_require_ready
    def push(self, source: str, dest: str):
        dest = dest.lstrip('/')
        subprocess.check_call(['lxc', 'file', 'push', '-r', source, self._name + '/' + dest])

    @_require_ready
    def pull(self, source: str, dest: str):
        source = source.lstrip('/')
        subprocess.check_call(['lxc', 'file', 'pull', '-r', self._name + '/' + source, dest])

    def _wait_for_network(self):
        self.log('Waiting for a network connection ...')
        connected = False
        retry_count = 25
        network_probe = 'import urllib.request; urllib.request.urlopen("{}", timeout=5)' \
            .format('http://start.ubuntu.com/connectivity-check.html')
        while not connected:
            time.sleep(1)
            try:
                result = self.exec('python3', '-c', network_probe)
                connected = result.exit_code == 0
            except subprocess.CalledProcessError:
                connected = False
                retry_count -= 1
                if retry_count == 0:
                    raise NetworkError("No network connection")
        self.log('Network connection established')

    def _prepare(self):
        self.log('Preparing system ...')
        assert self.exec('mkdir', '-p', '/home/grout').exit_code == 0
        self.log('Updating and upgrading system ...')
        assert self.exec('apt-get', 'update').exit_code == 0
        assert self.exec('apt-get', 'update').exit_code == 0

    def _forgiven_names(self) -> List[str]:
        names = []
        containers = self._lxd.containers.all()
        for c in containers:
            names.append(c.name)
        return names

    def _gen_name(self):
        no = 0
        forgiven = self._forgiven_names()
        name = 'grout-builder-0'
        while name in forgiven:
            name = 'grout-builder-' + str(no)
            no += 1
        return name
