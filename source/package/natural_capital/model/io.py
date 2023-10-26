"""
Code related to I/O
"""
import json
import os.path

import numpy as np
import pcraster as pcr


class IO:
    """
    Class for handling the I/O taking information from configuration into account
    """

    def __init__(self, configuration):
        self.configuration = configuration

    # def output_raster_pathname(
    #         self,
    #         basename):
    #     return os.path.join(
    #         self.configuration.raster_output_data_pathname, basename)

    def read_raster(self, pathname):
        """
        Read a raster
        """
        # TODO This should shortcut when this raster is already read
        # return readmap(input_raster_pathname(name))
        return pcr.readmap(pathname)

    def write_raster(self, variable, pathname):
        """
        Write a raster
        """
        if not os.path.isabs(pathname):
            pathname = self.configuration.output_raster_pathname(pathname)

        pcr.report(variable, pathname)

    def write_raster_info(self, variable, pathname, mapinfo):
        """
        Write raster information
        """
        if not os.path.isabs(pathname):
            pathname = self.configuration.output_raster_pathname(pathname)
        pathname = os.path.splitext(pathname)[0] + ".json"
        mapname = os.path.splitext(os.path.split(pathname)[1])[0]
        data = {}
        data["name"] = mapname
        data["code"] = mapinfo["code"]
        data["model"] = mapinfo["model"]
        data["class"] = mapinfo["class"]
        data["units"] = mapinfo["units"]
        data["legendrgbmin"] = mapinfo["legendrgbmin"]
        data["legendmin"] = mapinfo["legendmin"]
        data["legendrgbmax"] = mapinfo["legendrgbmax"]
        data["legendmax"] = mapinfo["legendmax"]

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

        data["geobox"] = mapextent

        p2n = pcr.pcr2numpy(variable, np.NaN)
        data["min"] = float(np.nanmin(p2n))
        data["max"] = float(np.nanmax(p2n))
        data["avg"] = float(np.nanmean(p2n))
        data["sum"] = float(np.nansum(p2n))

        with open(pathname, "w", encoding="utf-8") as write_file:
            json.dump(data, write_file)
