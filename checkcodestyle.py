#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import pycodestyle


def main():
    """
    This tool is using PyCodeStyle (https://github.com/PyCQA/pycodestyle)
    to check the code against some of the PEP 8 conventions.
    The only exception from the recommended options is the line length
    which is set to 120 instead of the default 79.
    """
    print('Checking code style ...')
    report = pycodestyle.StyleGuide(
        max_line_length=120
    ).check_files(".")
    print('Done.')
    if report.get_count() > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
