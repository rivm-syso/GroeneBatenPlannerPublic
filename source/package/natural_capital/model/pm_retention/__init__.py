"""
Code specific for the air regulation model
"""
import pcraster as pcr

from ... import checked_call2, validate
from .. import project
from ..io import IO


@checked_call2
def wrapper(project_file_pathname):
    """
    Calculate air regulation by vegetation

    :param str project_file_pathname: Name of project file
    """
    configuration = project.configuration(project_file_pathname)
    io = IO(configuration)

    # Inputs
    land_cover_pathname = configuration.input_raster_pathname(
        "pm_retention", "land_cover"
    )
    pm_10_pathname = configuration.input_raster_pathname("pm_retention", "pm_10")
    pm_25_pathname = configuration.input_raster_pathname("pm_retention", "pm_25")
    trees_pathname = configuration.input_raster_pathname("pm_retention", "trees")
    shrubs_pathname = configuration.input_raster_pathname("pm_retention", "shrubs")
    grass_pathname = configuration.input_raster_pathname("pm_retention", "grass")
    resuspension_fractionpm10 = configuration.float_value(
        "pm_retention", "resuspension_fractionpm10"
    )
    resuspension_fractionpm25 = configuration.float_value(
        "pm_retention", "resuspension_fractionpm25"
    )
    deposition_lut_pathname = configuration.input_table_pathname(
        "pm_retention", "deposition_lut"
    )
    deposition_tree_lut_pathname = configuration.input_table_pathname(
        "pm_retention", "deposition_tree_lut"
    )
    resuspension_fractionpm10_lut_pathname = configuration.input_table_pathname(
        "pm_retention", "resuspension_fractionpm10_lut"
    )
    resuspension_fractionpm25_lut_pathname = configuration.input_table_pathname(
        "pm_retention", "resuspension_fractionpm25_lut"
    )

    # Outputs
    capture_pm10_pathname = configuration.output_raster_pathname(
        "pm_retention", "capture_pm10"
    )
    capture_pm25_pathname = configuration.output_raster_pathname(
        "pm_retention", "capture_pm25"
    )
    map_total_pm10_pathname = configuration.output_raster_pathname(
        "pm_retention", "map_total_pm10"
    )
    map_total_pm25_pathname = configuration.output_raster_pathname(
        "pm_retention", "map_total_pm25"
    )
    perc_conc_change_pm10_pathname = configuration.output_raster_pathname(
        "pm_retention", "perc_conc_change_pm10"
    )
    perc_conc_change_pm25_pathname = configuration.output_raster_pathname(
        "pm_retention", "perc_conc_change_pm25"
    )
    perc_conc_change_pm10_pathname = configuration.output_raster_pathname(
        "pm_retention", "perc_conc_change_pm10"
    )
    perc_conc_change_pm25_pathname = configuration.output_raster_pathname(
        "pm_retention", "perc_conc_change_pm25"
    )

    land_cover = io.read_raster(land_cover_pathname)
    pm_10 = io.read_raster(pm_10_pathname)
    pm_25 = io.read_raster(pm_25_pathname)

    # Fill no-data cells with zero
    trees = io.read_raster(trees_pathname)
    trees = pcr.ifthenelse(pcr.defined(trees), trees, 0.0)
    shrubs = io.read_raster(shrubs_pathname)
    shrubs = pcr.ifthenelse(pcr.defined(shrubs), shrubs, 0.0)
    grass = io.read_raster(grass_pathname)
    grass = pcr.ifthenelse(pcr.defined(grass), grass, 0.0)

    deposition_velocity = pcr.lookupscalar(deposition_lut_pathname, land_cover)
    deposition_velocity_trees = pcr.lookupscalar(
        deposition_tree_lut_pathname, land_cover
    )

    resuspension_fractionpm10 = pcr.lookupscalar(
        resuspension_fractionpm10_lut_pathname, land_cover
    )

    resuspension_fractionpm25 = pcr.lookupscalar(
        resuspension_fractionpm25_lut_pathname, land_cover
    )

    (
        capture_pm10,
        capture_pm25,
        map_total_pm10,
        map_total_pm25,
        perc_conc_change_pm10,
        perc_conc_change_pm25,
    ) = function(
        land_cover,
        pm_10,
        pm_25,
        trees,
        shrubs,
        grass,
        resuspension_fractionpm10,
        resuspension_fractionpm25,
        deposition_velocity,
        deposition_velocity_trees,
    )

    io.write_raster(capture_pm10, capture_pm10_pathname)
    io.write_raster(capture_pm25, capture_pm25_pathname)
    io.write_raster(map_total_pm10, map_total_pm10_pathname)
    io.write_raster(map_total_pm25, map_total_pm25_pathname)
    io.write_raster(perc_conc_change_pm10, perc_conc_change_pm10_pathname)
    io.write_raster(perc_conc_change_pm25, perc_conc_change_pm25_pathname)


def function(
    land_cover,  # pylint: disable=unused-argument
    pm_10_concentration,
    pm_25_concentration,
    trees,
    shrubs,
    grass,
    resuspension_fractionpm10,
    resuspension_fractionpm25,
    deposition_velocity,
    deposition_velocity_trees,
):
    """
    Calculate health effects of green space

    :param nominal_raster land_cover: Land cover
    :param scalar_raster pm_10_concentration: Concentration of PM10
    :param scalar_raster trees: Percentage coverage by vegetation > 2.5m
    :param scalar_raster shrubs: Percentage coverage by vegetation 1-2.5m
    :param scalar_raster grass: Percentage coverage by vegetation < 1m
    :param float resuspension_fraction: Fraction resuspension
    :param scalar_raster deposition_velocity: Deposition velocities for
        non-trees (m/s)
    :param scalar_raster deposition_velocity_trees: Deposition velocities
        for trees (m/s)

    :return: Tuple of

        - Amount of PM10 captured by vegetation (kg/ha/yr)
        - Amount of PM2.5 captured by vegetation (kg/ha/yr)

    :rtype: tuple of scalar rasters
    """
    validate.in_range([trees, shrubs, grass], 0, 1)
    validate.in_range([resuspension_fractionpm10], 0, 1)
    validate.in_range([resuspension_fractionpm25], 0, 1)
    validate.greater_equal_than([deposition_velocity, deposition_velocity_trees], 0)

    cell_size = pcr.cellvalue(pcr.celllength(), 0)[0]
    vegetated = trees + shrubs + grass
    # validate.in_range(vegetated, 0, 1)
    vegetated = pcr.ifthenelse(vegetated > 1, 1, vegetated)
    non_vegetated = 1.0 - vegetated

    deposition_velocity = (
        trees * deposition_velocity_trees
        + shrubs * 0.3
        + grass * 0.2
        + non_vegetated * deposition_velocity
    )

    pm_10_concentration = pcr.windowaverage(pm_10_concentration, 2 * 100 + cell_size)
    pm_25_concentration = pcr.windowaverage(pm_25_concentration, 2 * 100 + cell_size)
    validate.greater_equal_than(pm_10_concentration, -1e-5)
    pm_10_concentration = pcr.ifthenelse(
        pm_10_concentration < 0, 0, pm_10_concentration
    )
    pm_25_concentration = pcr.ifthenelse(
        pm_25_concentration < 0, 0, pm_25_concentration
    )

    # Conversion factor from cm/s * μg/m³ → kg/dam2/yr
    unit_conversion = 0.031536

    capture_pm10 = (
        deposition_velocity
        * pm_10_concentration
        * (1 - resuspension_fractionpm10)
        * unit_conversion
    )

    capture_pm25 = (
        deposition_velocity
        * 0.2
        * pm_25_concentration
        * (1 - resuspension_fractionpm25)
        * unit_conversion
    )

    # from kg/dam/yr to ug/m3/d = 0.00137
    conc_change_pm10 = capture_pm10 * 0.00137
    perc_conc_change_pm10 = (conc_change_pm10 / pm_10_concentration) * 100
    conc_change_pm25 = capture_pm25 * 0.00137
    perc_conc_change_pm25 = (conc_change_pm25 / pm_25_concentration) * 100
    map_total_pm10 = pcr.maptotal(capture_pm10)
    map_total_pm25 = pcr.maptotal(capture_pm25)

    return (
        capture_pm10,
        capture_pm25,
        map_total_pm10,
        map_total_pm25,
        perc_conc_change_pm10,
        perc_conc_change_pm25,
    )
