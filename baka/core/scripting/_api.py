from typing import Dict, Iterable, Optional
from distutils.version import StrictVersion

import collections
import sys

RunResult = collections.namedtuple(
    'RunResult', ('output', 'exit_code')
)


class APIError(Exception):
    pass


def since(version: str):
    def _since(f):
        def wrapper(self, *args, **kwargs):
            if StrictVersion(self._version) < StrictVersion(version):
                raise APIError(
                    'Method baka.{} is not supported in {}'.format(
                        f.__name__, repr(self._version)
                    ))
            return f(self, *args, **kwargs)

        return wrapper

    return _since


class API:
    _module_name = 'baka'
    _supported_versions = ('0.1.0',)

    def __init__(self, version: str, backend: dict):
        if version not in self._supported_versions:
            raise APIError(
                'Version {} of module {} is not supported'.format(
                    repr(version), repr(self._module_name)
                ))
        self._version = version
        self._container = backend['container']
        self._job = backend['job']

    @property
    @since('0.1.0')
    def image(self) -> str:
        return self._container.image

    @property
    @since('0.1.0')
    def arch(self) -> str:
        return self._container.arch

    @property
    @since('0.1.0')
    def artifacts(self) -> Iterable:
        return self._job.artifacts

    @property
    @since('0.1.0')
    def artifacts_path(self) -> str:
        return self._job.artifacts_path

    @since('0.1.0')
    def run(self, command, *args, path: str = None, envvars: Dict[str, str] = None,
            collect_output: bool = False, log_output: bool = True) -> RunResult:
        cmd_result = self._container.exec(
            command, *args, path=path, envvars=envvars, collect_output=collect_output, log_output=log_output
        )
        run_result = RunResult(
            output=cmd_result.output,
            exit_code=cmd_result.exit_code
        )
        return run_result

    @since('0.1.0')
    def log(self, *fragments):
        self._container.log(*fragments)


def require(module: str, min_version: str, max_version: str = None, backend: dict = None) -> Optional[API]:
    if module == 'python':
        python_version_str = '{}.{}.{}'.format(*sys.version_info[0:3])
        if StrictVersion(python_version_str) < StrictVersion(min_version):
            raise APIError('Python version {} is not supported'.format(python_version_str))
        if max_version:
            if StrictVersion(python_version_str) >= StrictVersion(max_version):
                raise APIError('Python version {} is not supported'.format(python_version_str))
        return
    if module != 'baka':
        raise APIError('No module named {}'.format(repr(module)))
    return API(min_version, backend=backend)
