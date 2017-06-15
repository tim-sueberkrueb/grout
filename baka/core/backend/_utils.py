import platform


_debian_arch_map = {
    'x86_64': 'amd64',
    'i686': 'i386',
    'armv7l': 'armhf',
    'aarch64': 'arm64',
    'ppc64le': 'ppc64el',
    'ppc': 'powerpc',
    's390x': 's390x'
}


def platform_architecture() -> str:
    return platform.processor()


def debian_architecture() -> str:
    return _debian_arch_map[platform_architecture()]
