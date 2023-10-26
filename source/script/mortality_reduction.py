#!/usr/bin/env python

"""
Implementation of the mortality_reduction.py command-line utility


"""

import os
import sys

import docopt
from natural_capital.model.hl import mortality_reduction


def main():
    """
    Main entry point of the command
    """
    doc_string = """\
Calculate reduced mortality by vegetation


usage:
    {command} <project>
    {command} (-h | --help)

options:
    -h --help   Show this screen
    <project>   Project file

Information from the project file is used to configure the model run
""".format(
        command=os.path.basename(sys.argv[0])
    )

    arguments = docopt.docopt(doc_string)
    project_file_pathname = arguments["<project>"]

    return mortality_reduction(project_file_pathname)


if __name__ == "__main__":
    sys.exit(main())
