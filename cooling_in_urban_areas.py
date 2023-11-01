"""
Code specific for the cool city model
"""
import pcraster as pcr

from ... import algorithm, checked_call2, validate
from .. import project
from ..io import IO


@checked_call2
def wrapper(project_file_pathname):
    """
    Calculate cooling effect of vegetation and water on urban heat
    island effect

    :param str project_file_pathname: Name of project file
    """
    configuration = project.configuration(project_file_pathname)
    io = IO(configuration)

    # Inputs
    land_cover_pathname = configuration.input_raster_pathname(
        "cooling_in_urban_areas", "land_cover"
    )
    roughness_length_pathname = configuration.input_table_pathname(
        "cooling_in_urban_areas", "roughness_length"
    )
    wind_speed_pathname = configuration.input_raster_pathname(
        "cooling_in_urban_areas", "wind_speed"
    )
    wind_class_pathname = configuration.input_table_pathname(
        "cooling_in_urban_areas", "wind_class"
    )
    population_pathname = configuration.input_raster_pathname(
        "cooling_in_urban_areas", "population"
    )
    built_up_pathname = configuration.input_table_pathname(
        "cooling_in_urban_areas", "built_up"
    )
    uhi_reduction_lut_pathname = configuration.input_table_pathname(
        "cooling_in_urban_areas", "uhi_reduction_lut"
    )

    trees_pathname = configuration.input_raster_pathname(
        "cooling_in_urban_areas", "trees"
    )
    shrubs_pathname = configuration.input_raster_pathname(
        "cooling_in_urban_areas", "shrubs"
    )
    grass_pathname = configuration.input_raster_pathname(
        "cooling_in_urban_areas", "grass"
    )

    # Outputs
    maximum_uhi_effect_pathname = configuration.output_raster_pathname(
        "cooling_in_urban_areas", "maximum_uhi_effect"
    )
    potential_uhi_effect_pathname = configuration.output_raster_pathname(
        "cooling_in_urban_areas", "potential_uhi_effect"
    )
    in_situ_cooling_effect_pathname = configuration.output_raster_pathname(
        "cooling_in_urban_areas", "in_situ_cooling_effect"
    )
    actual_uhi_effect_pathname = configuration.output_raster_pathname(
        "cooling_in_urban_areas", "actual_uhi_effect"
    )
    cooling_effect_pathname = configuration.output_raster_pathname(
        "cooling_in_urban_areas", "cooling_effect"
    )

    land_cover = io.read_raster(land_cover_pathname)
    roughness_length = pcr.lookupscalar(roughness_length_pathname, land_cover)

    wind_speed = io.read_raster(wind_speed_pathname)
    wind_speed = pcr.lookupscalar(wind_class_pathname, wind_speed)

    population = io.read_raster(population_pathname)

    built_up = pcr.lookupboolean(built_up_pathname, land_cover)
    uhi_reduction = pcr.lookupscalar(uhi_reduction_lut_pathname, land_cover)

    trees = io.read_raster(trees_pathname)
    shrubs = io.read_raster(shrubs_pathname)
    grass = io.read_raster(grass_pathname)

    (
        maximum_uhi_effect,
        potential_uhi_effect,
        in_situ_cooling_effect,
        actual_uhi_effect,
        cooling_effect,
    ) = function(
        land_cover,
        roughness_length,
        wind_speed,
        population,
        built_up,
        uhi_reduction,
        trees,
        shrubs,
        grass,
    )

    io.write_raster(maximum_uhi_effect, maximum_uhi_effect_pathname)
    io.write_raster(potential_uhi_effect, potential_uhi_effect_pathname)
    io.write_raster(in_situ_cooling_effect, in_situ_cooling_effect_pathname)
    io.write_raster(actual_uhi_effect, actual_uhi_effect_pathname)
    io.write_raster(cooling_effect, cooling_effect_pathname)


def function(
    land_cover,
    roughness_length,
    wind_speed_100m,
    population,
    built_up,
    uhi_reduction,
    trees,
    shrubs,
    grass,
):
    """
    Calculate cooling effect of vegetation and water on urban heat
    island effect

    :param nominal_raster land_cover: Land cover
    :param scalar_raster roughness_length: Roughness length for momentum
    :param scalar_raster wind_speed_100m: Average wind speed at 100m height
    :param scalar_raster population: Number of inhabitants per cell
    :param boolean_raster built_up: Whether or not a cell is built-up
    :param scalar_raster uhi_reduction: Reduction rates per land-cover class
    :param scalar_raster trees: Percentage coverage by trees
    :param scalar_raster shrubs: Percentage coverage by shrubs
    :param scalar_raster grass: Percentage coverage by grass
    :return: Tuple of

        - Maximum UHI effect, ℃
        - Potential UHI effect, ℃
        - In-situ cooling effect of urban green and water, ℃
        - Actual local UHI effect, ℃
        - Cooling effect of urban green and water, ℃

    :rtype: tuple of scalar rasters
    """

   
    validate.greater_equal_than(population, 0.0)
    validate.in_range(trees, 0.0, 1.0)
    validate.in_range(shrubs, 0.0, 1.0)
    validate.in_range(grass, 0.0, 1.0)

    
    mask = pcr.defined(land_cover)
    trees = pcr.ifthenelse(pcr.pcrand(pcr.pcrnot(pcr.defined(trees)), mask), 0, trees)
    shrubs = pcr.ifthenelse(
        pcr.pcrand(pcr.pcrnot(pcr.defined(shrubs)), mask), 0, shrubs
    )
    grass = pcr.ifthenelse(pcr.pcrand(pcr.pcrnot(pcr.defined(grass)), mask), 0, grass)


    wind_speed_10m = (
        wind_speed_100m
        * pcr.ln(10.0 / roughness_length)
        / pcr.ln(100.0 / roughness_length)
    )

    # Smooth wind speed in 50m radius
    wind_speed_10m = pcr.windowaverage(wind_speed_10m, 2 * 50)
    validate.greater_equal_than(wind_speed_10m, -1e-6)
    wind_speed_10m = pcr.ifthenelse(wind_speed_10m < 0, 0, wind_speed_10m)

    population_10km = algorithm.windowtotal(population, 2 * 10000)
    population_10km = pcr.ifthenelse(population_10km < 0, 0, population_10km)

    maximum_uhi_effect = (
        -1.605 + (1.062 * pcr.log10(population_10km)) - (0.356 * wind_speed_10m)
    )
    maximum_uhi_effect = pcr.ifthenelse(
        maximum_uhi_effect < 0, 0, maximum_uhi_effect
    )  # RK: added for national calculation
    validate.greater_equal_than(maximum_uhi_effect, 0)

    green = trees + shrubs + grass
    green = pcr.ifthenelse(green > 1, 1, green)  # remove values above 1
    built_up_corrected = pcr.ifthenelse(built_up, 1.0 - green, 0.0)
    built_up_1km = algorithm.windowaverage(built_up_corrected, 2 * 1000)
    built_up_1km = pcr.ifthenelse(built_up_1km < 0, 0, built_up_1km)
    potential_uhi_effect = maximum_uhi_effect * built_up_1km

    non_green = 1 - green

    # Percentage reduction of the UHI effect of the land-cover type
    reduction = trees * 0.5 + shrubs * 0.3 + grass * 0.2 + non_green * uhi_reduction
    # validate.in_range(reduction, 0.0, 1.0)
    reduction = pcr.ifthenelse(reduction < 0, 0, reduction)

    in_situ_cooling_effect = potential_uhi_effect * reduction

    reduction_30m = pcr.windowaverage(reduction, 2 * 30)
    reduction_30m = pcr.ifthenelse(reduction_30m < 0, 0, reduction_30m)

    actual_uhi_effect = potential_uhi_effect * (1.0 - reduction_30m)
    cooling_effect = maximum_uhi_effect - actual_uhi_effect

    validate.greater_equal_than(
        [
            maximum_uhi_effect,
            potential_uhi_effect,
            in_situ_cooling_effect,
            actual_uhi_effect,
            cooling_effect,
        ],
        0.0,
    )

    return (
        maximum_uhi_effect,
        potential_uhi_effect,
        in_situ_cooling_effect,
        actual_uhi_effect,
        cooling_effect,
    )
