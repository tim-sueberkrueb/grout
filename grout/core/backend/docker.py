# -*- coding: utf-8 -*-

from typing import Dict, List

import subprocess
import time

from . import base


class DockerBackend(base.BaseBackend):
    def __init__(self, container, options: Dict=None):
        super().__init__(container, options)
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
            'image': 'ubuntu',
            'arch': 'amd64',
            'ephemeral': True
        }

    def init(self):
        self.log('Checking for container ...')
        # Find existing containers with the requested name
        existing = self._name in self._forgiven_names()
        # Create container or use existing one
        if existing:
            self.log('Launching container ...')
        else:
            self.log('Creating and launching container ...')
            cmd = ['docker', 'create', '-it', '--name', self._name]
            if self._ephemeral:
                cmd += ['--rm']
            cmd += [self._image]
            subprocess.check_call(cmd)
        # Start the container (if not already running)
        subprocess.check_call(['docker', 'start', self._name])
        # Enable most actions
        self._ready = True
        # Prepare system
        self._prepare()

    def destroy(self):
        self.log('Destroying ...')
        subprocess.check_call(['docker', 'rm', '-f', self._name])
        self._ready = False

    def exec(self, command, *args, path: str = None, envvars: Dict[str, str]=None) -> base.CommandResult:
        cmd = base.Command(
            ['docker', 'exec', '-i', self._name], command, *args, path=path, envvars=envvars
        )
        cmd.run()
        return cmd.result

    def log(self, *fragments):
        print(*fragments, end='' if fragments[-1].endswith('\n') else '\n')

    def push(self, source: str, dest: str):
        dest = dest.lstrip('/')
        subprocess.check_call(['docker', 'cp', source, self._name + ':/' + dest])

    def pull(self, source: str, dest: str):
        source = source.lstrip('/')
        subprocess.check_call(['docker', 'cp', self._name + ':/' + source, dest])

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
        # Make sure add-apt-repository and others are available
        assert self.exec('apt-get', 'install', '-y', 'software-properties-common').exit_code == 0

    @staticmethod
    def _existing_containers() -> List[Dict[str, str]]:
        out = subprocess.check_output(
            ['docker', 'ps', '-a', '--no-trunc', '--format', '{{.ID}}\t{{.Names}}\t{{.Image}}']
        )
        lines = out.decode('utf-8').splitlines()
        containers = []
        for line in lines:
            id_, names, image = line.split('\t')
            containers.append({
                'id': id_,
                'name': names,
                'image': image
            })
        return containers

    def _forgiven_names(self) -> List[str]:
        names = []
        for container in self._existing_containers():
            names.append(container['name'])
        return names

    def _gen_name(self):
        no = 0
        forgiven = self._forgiven_names()
        name = 'grout-whale-0'
        while name in forgiven:
            name = 'grout-whale-' + str(no)
            no += 1
        return name
