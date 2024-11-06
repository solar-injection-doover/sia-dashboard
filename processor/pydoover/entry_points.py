"""
pydoover.entry_points.py
~~~~~~~~~~~~~~~~~~~~~~
This module contains the entry-point functions for the pydoover module,
that are referenced in setup.py.
"""

from os import remove
from sys import argv
from zipfile import ZipFile

import requests


def main() -> None:
    """Main package entry point.
    Delegates to other functions based on user input.
    """

    try:
        user_cmd = argv[1]
        if user_cmd == 'update_processor':
            update_processor()
        if user_cmd == 'invoke_task':
            update_processor()
        else:
            RuntimeError('please supply a command for pydoover - e.g. update_processor / invoke_task')
    except IndexError:
        RuntimeError('please supply a command for pydoover - e.g. update_processor / invoke_task')
    return None


def update_processor() -> None:
    # """Installs the latest version of the template package project."""

    # # check that the user really want to do this
    # msg = 'Download Python package template project to this directory (y/n)? '
    # user_response = input(msg)
    # if user_response != 'y':
    #     return None

    # # download ZIP archive of GitHub repository
    # url = 'https://github.com/AlexIoannides/py-package-template/archive/master.zip'
    # r = requests.get(url)
    # with open('temp.zip', 'wb') as f:
    #     f.write(r.content)

    # # extract ZIP file into calling directory
    # with ZipFile('temp.zip', 'r') as repo_zip:
    #     repo_zip.extractall('.')

    # # clean up
    # remove('temp.zip')
    return None