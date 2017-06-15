# -*- coding: utf-8 -*-

from typing import Dict, Callable, Iterable

import abc
import pty
import os
import errno
import select
import subprocess
import time


class NotReadyError(Exception):
    pass


class NetworkError(Exception):
    pass


class CommandResult:
    def __init__(self, exit_code: int, output: str):
        self._exit_code = exit_code
        self._output = output

    @property
    def exit_code(self) -> int:
        return self._exit_code

    @property
    def output(self) -> str:
        return self._output


class BaseCommand(abc.ABC):
    def __init__(self, container_name: str, command: str, *args, path: str = None, envvars: Dict[str, str]=None,
                 stdout: Callable=None, stderr: Callable=None, collect_output: bool = False):
        self._exit_code = -1
        self._output = ''
        self._collect_output = collect_output
        self._container_name = container_name
        self._command = command
        self._args = list(args)
        self._path = path
        self._env = envvars or {}
        self._stdout = stdout
        self._stderr = stderr

    @abc.abstractmethod
    def _build_command(self) -> str:
        pass

    def run(self):
        cmd = self._build_command()
        # Adopted from https://stackoverflow.com/a/31953436
        masters, slaves = zip(pty.openpty(), pty.openpty())
        proc = subprocess.Popen(
            cmd, shell=True,
            stdin=slaves[0], stdout=slaves[0], stderr=slaves[1]
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
                        try:
                            decoded = data.decode()
                            if self._collect_output:
                                self._output += decoded
                            f = readable[fd]
                            if f is not None:
                                f(decoded)
                        except UnicodeDecodeError as e:
                            # Ignore not decodable data with a warning
                            print('Warning (detected not decodable data): ' + str(e))
        if proc.returncode:
            raise subprocess.CalledProcessError(proc.returncode, cmd)
        for fd in masters:
            os.close(fd)
        self._exit_code = proc.wait()

    @property
    def exit_code(self) -> int:
        return self._exit_code

    @property
    def output(self) -> str:
        return self._output

    @property
    def result(self) -> CommandResult:
        result = CommandResult(self._exit_code, self.output)
        return result


class BaseBackend(metaclass=abc.ABCMeta):
    def __init__(self, container, options: Dict=None):
        self._container = container
        self._ready = False
        self._options = options or {}
        # Apply default options
        default_options = self._default_options
        for def_key in default_options:
            if def_key not in self._options or self._options[def_key] is None:
                self._options[def_key] = default_options[def_key]

    @property
    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def image(self) -> str:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def arch(self) -> str:
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def ephemeral(self) -> bool:
        raise NotImplementedError()

    @property
    def _default_options(self) -> Dict:
        return {}

    def _wait_for_network(self):
        self.log('Waiting for a network connection ...')
        connected = False
        retry_count = 25
        network_probe = 'import urllib.request; urllib.request.urlopen("{}", timeout=5)' \
            .format('http://start.ubuntu.com/connectivity-check.html')
        while not connected:
            time.sleep(1)
            try:
                result = self.exec(
                    'python3', '-c', "'" + network_probe + "'",
                    collect_output=False, log_output=False
                )
                connected = result.exit_code == 0
            except subprocess.CalledProcessError:
                connected = False
                retry_count -= 1
                if retry_count == 0:
                    raise NetworkError("No network connection")
        self.log('Network connection established')

    def _envvars(self) -> Dict[str, str]:
        script = 'import os; print(repr(dict(os.environ)))'
        result = self.exec(
            'python3', '-c', "'" + script + "'",
            expand_envvars=False, collect_output=True, log_output=False
        )
        envvars = eval(result.output)
        return envvars

    def _expand_envvars(self, envvars: Dict[str, str]) -> Dict[str, str]:
        container_env = self._envvars()
        # Expand a copy of the received dictionary
        # to avoid confusion.
        envvars = envvars.copy()
        for var in envvars.keys():
            val = envvars[var]
            for def_var in container_env.keys():
                def_val = container_env[def_var]
                val = val.replace('${}'.format(def_var), def_val)
            for custom_var in envvars.keys():
                custom_val = envvars[custom_var]
                val = val.replace('${}'.format(custom_var), custom_val)
            envvars[var] = val.rstrip(':')
        return envvars

    @property
    def options(self) -> Dict:
        return self._options

    @property
    def ready(self) -> bool:
        return self._ready

    def log(self, *fragments):
        self._container.log(*fragments)

    @abc.abstractmethod
    def init(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def destroy(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def exec(self, command, *args, path: str = None, envvars: Dict[str, str]=None,
             expand_envvars: bool = True, collect_output: bool = False, log_output: bool = True) -> CommandResult:
        raise NotImplementedError()

    @abc.abstractmethod
    def push(self, source: str, dest: str):
        raise NotImplementedError()

    @abc.abstractmethod
    def pull(self, source: str, dest: str):
        raise NotImplementedError()
