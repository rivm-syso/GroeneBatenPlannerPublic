#!/usr/bin/env python
"""
Implementation of the cooling_in_urban_areas.py command-line utility
"""
import os
import sys

import docopt
from natural_capital.model.hl import cooling_in_urban_areas


def main():
    """
    Main entry point of the command
    """
    doc_string = """\
Calculate cooling effect of vegetation and water on urban heat island effect

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

    return cooling_in_urban_areas(project_file_pathname)


if __name__ == "__main__":
    sys.exit(main())
