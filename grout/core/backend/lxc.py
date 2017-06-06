# -*- coding: utf-8 -*-

from typing import Dict, List

import subprocess
import pylxd

from . import base


class LXCCommand(base.BaseCommand):
    def _build_command(self) -> str:
        cmd = ['lxc', 'exec', self._container_name]
        if self._path:
            cmd += ['--env', 'HOME={}'.format(self._path)]
        for env_var in self._env.keys():
            val = self._env[env_var]
            cmd += ['--env', '{}={}'.format(env_var, val)]
        cmd += ['--', self._command] + self._args
        return ' '.join(cmd)


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

    def exec(self, command, *args, path: str = None, envvars: Dict[str, str]=None) -> base.CommandResult:
        cmd = LXCCommand(
            self._name, command, *args,
            path=path, envvars=envvars, stdout=self.log, stderr=self.log
        )
        cmd.run()
        return cmd.result

    def log(self, *fragments):
        print(*fragments, end='' if fragments[-1].endswith('\n') else '\n')

    def push(self, source: str, dest: str):
        dest = dest.lstrip('/')
        subprocess.check_call(['lxc', 'file', 'push', '-r', source, self._name + '/' + dest])

    def pull(self, source: str, dest: str):
        source = source.lstrip('/')
        subprocess.check_call(['lxc', 'file', 'pull', '-r', self._name + '/' + source, dest])

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
