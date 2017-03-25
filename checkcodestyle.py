#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pycodestyle


def main():
    """
    This tool is using PyCodeStyle (https://github.com/PyCQA/pycodestyle)
    to check the code against some of the PEP 8 conventions.
    The only exception from the recommended options is the line length
    which is set to 120 instead of the default 79.
    """
    print('Checking code style ...')
    pycodestyle.StyleGuide(
        max_line_length=120
    ).check_files(".")
    print('Done.')


if __name__ == '__main__':
    main()
