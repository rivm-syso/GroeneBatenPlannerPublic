#!/usr/bin/env python
"""
Implementation of the ncm_diff.py command-line utility
"""
import os
import sys

import docopt
from natural_capital.raster import diff


def main():
    """
    Main entry point of the command
    """
    doc_string = """\
Compare two rasters or two directories containing rasters

usage:
    {command} <input1> <input2> <output>
    {command} (-h | --help)

options:
    -h --help  Show this screen
    <input1>   Pathname of raster or directory containing rasters
    <input2>   Pathname of raster or directory containing rasters
    <output>   Pathname of directory where results will be written to.
               This directory must exist. Same-named files will be
               overwritten.

The input pathnames must be both pathnames to rasters or both pathnames to
directories. Absolute and relative changes in values are calculated
relative to the raster(s) pointed to by input1.
""".format(
        command=os.path.basename(sys.argv[0])
    )

    arguments = docopt.docopt(doc_string)
    input1_pathname = arguments["<input1>"]
    input2_pathname = arguments["<input2>"]
    output_pathname = arguments["<output>"]

    return diff(input1_pathname, input2_pathname, output_pathname)


if __name__ == "__main__":
    sys.exit(main())
