#!/usr/bin/env python
"""
Implementation of the ncm_rasterdescriptions.py command-line utility
"""
import configparser
import json
import os
import sys

import docopt
import numpy as np
import pcraster as pcr


def main():
    """
    Main entry point of the command
    """
    # pylint: disable=consider-using-f-string, too-many-locals
    doc_string = """\
Creates JSON description files for PCRaster maps in input folder

usage:
    {command} <input> <descriptions>
    {command} (-h | --help)

options:
    -h --help  Show this screen
    <input>          Pathname of directory containing PCRaster maps (*.map)
    <descriptions>   Pathname of description file. This is an ini file structure.
                     Sections are filenames for PCRaster files (without extension).
                     Same-named files will be overwritten.

The input pathnames must be a pathname to a folder containing PCRaster maps.
The command creates a json file for every map name found in descriptions file.
No json files are created for maps not found in descriptions.
""".format(
        command=os.path.basename(sys.argv[0])
    )

    arguments = docopt.docopt(doc_string)
    input_pathname = arguments["<input>"]
    descriptions_pathname = arguments["<descriptions>"]
    input_pathname = os.path.join(input_pathname, "")

    config = configparser.ConfigParser()
    config.optionxform = str  # type: ignore
    config.read(descriptions_pathname)
    for mapname in config.sections():
        mapfilename = os.path.join(input_pathname, mapname + ".map")
        if os.path.isfile(mapfilename):
            jsondata = {}
            tableop = "sum"
            for key, value in config.items(mapname):
                # print("key",key)
                jsondata[key] = value
                if key == "tableop":
                    tableop = value

            pcrastermap = pcr.readmap(mapfilename)
            nr_rows = pcr.clone().nrRows()
            nr_cols = pcr.clone().nrCols()
            cell_size = pcr.clone().cellSize()
            ymax = pcr.clone().north()
            xmin = pcr.clone().west()
            ymin = ymax - nr_rows * cell_size
            xmax = xmin + nr_cols * cell_size

            mapextent = {}
            mapextent["xmin"] = xmin
            mapextent["xmax"] = xmax
            mapextent["ymin"] = ymin
            mapextent["ymax"] = ymax
            jsondata["geobox"] = mapextent  # type: ignore

            p2n = pcr.pcr2numpy(pcrastermap, np.NaN)
            jsondata["min"] = "{:.1e}".format(float(np.nanmin(p2n)))
            jsondata["max"] = "{:.1e}".format(float(np.nanmax(p2n)))
            jsondata["avg"] = "{:.1e}".format(float(np.nanmean(p2n)))
            jsondata["sum"] = "{:.1e}".format(float(np.nansum(p2n)))

            jsondata["tablevalue"] = "{:.1e}".format(float(np.nansum(p2n)))
            if tableop == "sum":
                jsondata["tablevalue"] = "{:.1e}".format(float(np.nansum(p2n)))
            elif tableop == "avg":
                jsondata["tablevalue"] = "{:.1e}".format(float(np.nanmean(p2n)))
            elif tableop == "min":
                jsondata["tablevalue"] = "{:.1e}".format(float(np.nanmin(p2n)))
            elif tableop == "max":
                jsondata["tablevalue"] = "{:.1e}".format(float(np.nanmax(p2n)))

            jsonfilename = os.path.join(input_pathname, mapname + ".json")
            with open(jsonfilename, "w", encoding="utf-8") as write_file:
                json.dump(jsondata, write_file)


if __name__ == "__main__":
    sys.exit(main())
