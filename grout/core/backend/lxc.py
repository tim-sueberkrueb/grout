# -*- coding: utf-8 -*-

from typing import Dict, List, Callable

import subprocess
import time
import pylxd
import tempfile
import pty
import os
import errno
import select

from . import base


class _ExecGenerator:
    def __init__(self, name: str, command: str, *args, path: str = None, envvars: Dict[str, str]=None,
                 stdout: Callable=None, stderr: Callable=None):
        self._exit_code = -1
        self._output = ''
        self._name = name
        self._command = command
        self._args = list(args)
        self._path = path
        self._env = envvars or {}
        self._expand_env()
        self._stdout = stdout
        self._stderr = stderr

    def run(self):
        cmd = ['lxc', 'exec', self._name]
        if self._path:
            cmd += ['--env', 'HOME={}'.format(self._path)]
        for env_var in self._env.keys():
            val = self._env[env_var]
            cmd += ['--env', '{}={}'.format(env_var, val)]
        cmd += ['--', self._command] + self._args

        # Adopted from https://stackoverflow.com/a/31953436
        masters, slaves = zip(pty.openpty(), pty.openpty())
        proc = subprocess.Popen(
            cmd, stdin=slaves[0], stdout=slaves[0], stderr=slaves[1]
        )
        for fd in slaves:
            # We don't provide any input, thus close
            os.close(fd)
        readable = {
            masters[0]: self._stdout,
            masters[1]: self._stderr,
        }
        while readable:
            for fd in select.select(readable, [], [])[0]:
                try:
                    # Read available data
                    data = os.read(fd, 1024)
                except OSError as e:
                    # EIO means EOF on some systems
                    if e.errno != errno.EIO:
                        raise
                    del readable[fd]
                else:
                    # Reached EOF
                    if not data:
                        del readable[fd]
                    else:
                        readable[fd](data.decode())
        if proc.returncode:
            raise subprocess.CalledProcessError(proc.returncode, cmd)
        for fd in masters:
            os.close(fd)
        self._exit_code = proc.wait()

    def _expand_env(self):
        default_env = {
            'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
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
    def result(self) -> base.ExecResult:
        result = base.ExecResult(self._exit_code, self.output)
        return result


class LXCBackend(base.BaseBackend):
    def __init__(self, container, options: Dict=None):
        # Initialize LXD client before base initialization
        # to support _default_options
        self._lxd = pylxd.Client()
        super().__init__(container, options)
        self._lxd_container = None
        self._name = self._options['name']
        self._image = self._options['image']
        self._arch = self._options['arch']
        self._ephemeral = self._options['ephemeral']

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
    def _default_options(self) -> Dict:
        return {
            'name': self._gen_name(),
            'image': 'ubuntu:xenial',
            'arch': 'amd64',
            'ephemeral': True
        }

    def init(self):
        self.log('Checking for container ...')
        # Find existing containers with the requested name
        existing_containers = self._lxd.containers.all()
        existing = list(filter(lambda c: c.name == self._name, existing_containers))
        # Create container or use existing one
        if len(existing) > 0:
            self.log('Launching container ...')
            self._lxd_container = existing[0]
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
            self._lxd_container = self._lxd.containers.get(self._name)
        # Configure container
        subprocess.check_call([
            'lxc', 'config', 'set', self._name,
            'environment.SNAPCRAFT_SETUP_CORE', '1'])
        # Necessary to read asset files with non-ascii characters.
        subprocess.check_call([
            'lxc', 'config', 'set', self._name,
            'environment.LC_ALL', 'C.UTF-8'])
        # Make host user root inside container
        subprocess.check_call([
            'lxc', 'config', 'set', self._name,
            'raw.idmap', 'both 1000 0'
        ])
        # Start the container (if not already running)
        self._lxd_container.start()
        # Enable most actions
        self._ready = True
        # Check for network connection
        self._wait_for_network()
        # Prepare system
        self._prepare()

    def destroy(self):
        self.log('Destroying ...')
        subprocess.check_call(['lxc', 'delete', '-f', self._name])
        self._ready = False

    def exec(self, command, *args, path: str = None, envvars: Dict[str, str]=None) -> base.ExecResult:
        gen = _ExecGenerator(self._name, command, *args, path=path, envvars=envvars, stdout=self.log, stderr=self.log)
        gen.run()
        return gen.result

    def log(self, *fragments):
        print(*fragments, end='' if fragments[-1].endswith('\n') else '\n')

    def push(self, source: str, dest: str):
        dest = dest.lstrip('/')
        subprocess.check_call(['lxc', 'file', 'push', '-r', source, self._name + '/' + dest])

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
                    raise base.NetworkError("No network connection")
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
