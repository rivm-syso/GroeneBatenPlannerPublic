#!/usr/bin/env python
"""
Implementation of the cookie_cut.py command-line utility
"""
import os
import sys

import docopt
from natural_capital.raster import cookie_cut


def main():
    """
    Main entry point of the command
    """
    doc_string = """\
Create a new raster by cookie-cutting an existing one

usage:
    {command} [--indices] <source> <x_min> <y_max> <x_max> <y_min>
        <destination>
    {command} <source> <extent> <destination>
    {command} (-h | --help)

options:
    -h --help      Show this screen
    <source>       Raster to cookie-cut
    <destination>  Raster to create
    <extent>       Raster to obtain extent from
    [--indices]    Coordinates are row/column indices (zero-based)
    <x_min>        Western-most x-coordinate of column to select
    <y_max>        Northern-most y-coordinate of row to select
    <x_max>        Eastern-most x-coordinate of one-passed-the-column to select
    <y_min>        Southern-most y-coordinate of one-passed-the-row to select
""".format(
        command=os.path.basename(sys.argv[0])
    )

    arguments = docopt.docopt(doc_string)
    source_raster_pathname = arguments["<source>"]
    destination_raster_pathname = arguments["<destination>"]

    extent_raster_pathname = arguments["<extent>"]

    if extent_raster_pathname is not None:
        extent = extent_raster_pathname
    else:
        x_min = float(arguments["<x_min>"])
        y_max = float(arguments["<y_max>"])
        x_max = float(arguments["<x_max>"])
        y_min = float(arguments["<y_min>"])
        extent = [x_min, y_max, x_max, y_min]

    use_indices = arguments["--indices"]

    return cookie_cut(
        source_raster_pathname,
        extent,
        destination_raster_pathname,
        use_indices=use_indices,
        output_format="PCRaster",
    )


if __name__ == "__main__":
    sys.exit(main())
