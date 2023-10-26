"""
Code specific for the reduced mortality model
"""
import pcraster as pcr

from ... import checked_call2, validate
from .. import project
from ..io import IO


@checked_call2
def wrapper(project_file_pathname):
    """
    Calculate reduced mortality by added vegetation through an increase in NDVI

    :param str project_file_pathname: Name of project file
    """
    configuration = project.configuration(project_file_pathname)
    io = IO(configuration)

    # Inputs
    ndvi_pathname = configuration.input_raster_pathname("mortality_reduction", "ndvi")
    mort_pathname = configuration.input_raster_pathname("mortality_reduction", "mort")
    population_pathname = configuration.input_raster_pathname(
        "mortality_reduction", "population"
    )
    # Outputs
    mortality_reduction_pathname = configuration.output_raster_pathname(
        "mortality_reduction", "mortality_reduction"
    )
    mortality_reduction_total_pathname = configuration.output_raster_pathname(
        "mortality_reduction", "mortality_reduction_total"
    )
    mortality_reduction_per_100k_pathname = configuration.output_raster_pathname(
        "mortality_reduction", "mortality_reduction_per_100k"
    )

    # Initialise rasters and Fill no-data cells with zero
    ndvi = io.read_raster(ndvi_pathname)
    mort = io.read_raster(mort_pathname)
    population = io.read_raster(population_pathname)

    (
        mortality_reduction,
        mortality_reduction_total,
        mortality_reduction_per_100k,
    ) = function(ndvi, mort, population)

    io.write_raster(mortality_reduction, mortality_reduction_pathname)
    io.write_raster(mortality_reduction_total, mortality_reduction_total_pathname)
    io.write_raster(mortality_reduction_per_100k, mortality_reduction_per_100k_pathname)


def function(
    ndvi,
    mort,
    population,
):
    r"""
    Calculate reduced mortality from added NDVI

       :param scalar_raster mort: mort is mortality rate per year.
       [mortality per gemeente 2022]/[inwonerspergemeente in 2022]
        as calculated from: D:\Mart\Projects\mortreduc
       :param scalar_raster ndvi: nvdi is ndvi averaged summer value based on
        all available less then 5 percent cloud covered sentinel images
        for year 2022 from 1 may - 31 August [-]

       :return: Tuple of

        - mortality_reduction: Reduction in mortality [nr people/100m2/yr]
        - mortality_reduction_total: Summed reduction of mortality in the project area [nr people]
        - mortality_reduction_per_100k: Summed reduction in mortality (nr people per 100.000 inhabitants)

    :rtype: tuple of scalar rasters
    """
    validate.in_range([ndvi], -1, 1)

    cell_size = pcr.cellvalue(pcr.celllength(), 0)[0]

    ndvi_mask = ndvi > 0
    ndvi_pos = pcr.ifthen(ndvi_mask, ndvi)

    ndvi_wa = pcr.windowaverage(ndvi_pos, 300 * 2 + cell_size)

    mortality_reduction_perc = (
        2.3 * ndvi_wa * 10
    )  # percentage reduced mort risk, 2.3% reductie in mortality risk voor elke 0.1 stijging NDVI
    mortality_reduction = (
        mortality_reduction_perc / 100 * population * mort
    )  # change in mortality per cell: mortality per inwoner * fraction * nr inwoners in a cell

    # below code is not needed, but should be implemented in ncmdiff to result in only positives for diff map?
    # mortality_reduction_pos_bol = mortality_reduction > 0
    # mortality_reduction_pos = pcr.ifthenelse(
    #    mortality_reduction_pos_bol, mortality_reduction, 0
    # )

    mortality_reduction_total = pcr.maptotal(mortality_reduction)
    inwoner_total = pcr.maptotal(population)

    mortality_reduction_per_100k = (
        mortality_reduction_total / inwoner_total * 100000
    )  # percentage mortality out of 100k total population

    # years_lost = mortality_reduction_total * 81.4 # average life expectancy
    # years_lost = mortality_reduction_total * 17.06 # 1/mortality at age = 81.5.
    # years_lost = mortality_reduction_total * (
    #    81.4 - 42.4 - 10
    # )  # cbs average age nl = 42.4.
    # But people under 20 years are not included in mortality in paper,
    # so this is overestimating, so distracting 20/2.
    # TODO: 2.3 in ncm als parameter for sens analysis
    # TODO:output naar toegenomen levensjaren aanpassen,
    # dit omzetten naar volys en dalys, check bij Loes, Hanneke?

    return mortality_reduction, mortality_reduction_total, mortality_reduction_per_100k
