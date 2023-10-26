"""
Code related to dealing with rasters
"""
import json
import os
import os.path

import pcraster as pcr

from . import checked_call2, print_warning_message, process


def is_raster_instance(instance):
    """
    Return whether the instance passed in is a PCRaster raster instance
    """
    return isinstance(instance, pcr._pcraster.Field)  # pylint: disable=protected-access


def as_raster(raster, value):
    """
    Return a new raster with value assigned to each cell for which the input raster contains
    a valid value
    """
    return pcr.ifthen(pcr.defined(raster), pcr.scalar(value))


def zeros(raster):
    """
    Return a raster with zero assigned to each cell for which the input raster contains a
    valid value
    """
    return as_raster(raster, 0)


def deep_copy(raster):
    """
    Return a new raster, which is a deep copy of the input raster

    Note that assigning a variable pointing to a raster to a new variable does not copy
    anything. It only results in two variables referring to the same underlying raster object.
    This is fast, but something a actual copy is needed.
    """
    return pcr.ifthen(pcr.defined(raster), raster)


def raster_info(raster_pathname):
    """
    Obtain gdalinfo output of the raster passed in as a json string
    """
    command = f"gdalinfo -json {raster_pathname}"
    result = process.checked_call(command)

    # GDAL outputs invalid json in case the raster contains only NaNs.
    # Fix this.
    result = result.replace('"min":nan', '"min":"nan"')
    result = result.replace('"max":nan', '"max":"nan"')

    return json.loads(result)


def value_scale(raster_pathname):
    """
    Return the PCRaster value scale of the raster passed in
    """
    info = raster_info(raster_pathname)
    metadata = info["metadata"][""]

    return (
        metadata["PCRASTER_VALUESCALE"] if "PCRASTER_VALUESCALE" in metadata else None
    )


def raster_extent(raster_pathname):
    """
    Return the extent of the raster pointed to by the input pathname

    The values in the list returned are ordered like this: x_min, y_max, x_max, y_min
    """
    info = raster_info(raster_pathname)
    extent = info["cornerCoordinates"]
    upper_left = extent["upperLeft"]
    lower_right = extent["lowerRight"]

    return [upper_left[0], upper_left[1], lower_right[0], lower_right[1]]


@checked_call2
def cookie_cut(
    source_raster_pathname,
    extent,
    destination_raster_pathname,
    use_indices=False,
    output_format="PCRaster",
):
    """
    Select a subset from a raster and write it to a new raster dataset

    :param str source_raster_pathname: Pathname of source raster
    :param extent: Name of raster or list of four coordinates
        ([x_min, y_max, x_max, y_min]). In the first case, the extent
        will be read from the raster.
    :param str destination_raster_pathname: Pathname of destination raster
    :param bool use_indices: Whether or not the coordinates must be
        interpreted as cell indices (zero-based)
    :param str output_format: Format to use for destination raster
    :raises ValueError: In case the extent is invalid (e.g.: x_min > x_max)

    The new raster dataset will only contain the selected cells. The cells
    in the new raster dataset will have the same size as the cells in the
    original raster. The coordinate reference system (if any) will also be
    the same.

    If a list of coordinates is passed in, this is their interpretation:

    - x_min: Coordinate of western-most column to select
    - y_max: Coordinate of northern-most row to select
    - x_max: Coordinate of one-past-the-easter-most column to select
    - y_min: Coordinate of one-past-the-southern-most row to select
    """
    if isinstance(extent, str):
        assert not use_indices
        extent = raster_extent(extent)

    x_min, y_max, x_max, y_min = extent

    if x_min > x_max:
        raise ValueError(
            "Western-most coordinate must be smaller than eastern-most coordinate"
        )

    if not use_indices:
        if y_min > y_max:
            raise ValueError(
                "Northern-most coordinate must be larger than southern-most coordinate"
            )
    else:
        if y_min < y_max:
            raise ValueError(
                "Northern-most coordinate must be smaller than southern-most coordinate"
            )

    # Copy the cells selected by the extent passed in to a new raster
    method = "projwin" if not use_indices else "srcwin"
    command = (
        f"gdal_translate -q -of {output_format} -{method} "
        f"{x_min} {y_max} {x_max} {y_min} "
        f"{source_raster_pathname} {destination_raster_pathname}"
    )
    process.checked_call(command)


def is_raster(pathname):
    """
    Return whether the file pointed to by the input pathname contains a raster dataset
    """
    try:
        raster_info(pathname)
        result = True
    except Exception:  # pylint: disable=broad-exception-caught
        result = False

    return result


def is_directory(pathname):
    """
    Return whether the input pathname points to an existing directory
    """
    return os.path.isdir(pathname)


def compare_rasters(input1_pathname, input2_pathname, output_pathname):
    """
    Compare two rasters and write the results to an output file

    A tuple of error and warning messages is returned. Rasters with absolute and relative
    differences are written to files named after the output pathname passed in.
    """
    errors = []
    warnings = []

    input1_is_raster = is_raster(input1_pathname)
    input2_is_raster = is_raster(input2_pathname)

    if not input1_is_raster:
        errors.append(f"File {input1_pathname} must be a raster")
    if not input2_is_raster:
        errors.append(f"File {input2_pathname} must be a raster")

    def compare_info_item(info1, info2, item):
        if info1[item] != info2[item]:
            errors.append(f"{item} is different: {info1[item]} != {info2[item]}")

    if input1_is_raster and input2_is_raster:
        # Compare the rasters
        # Only handle the important stuff. Skip things that are OK to
        # be different, like the format driver and the no-data value.

        raster_info1 = raster_info(input1_pathname)
        raster_info2 = raster_info(input2_pathname)

        compare_info_item(raster_info1, raster_info2, "cornerCoordinates")
        # compare_info_item(
        #         raster_info1, raster_info2, "wgs84Extent")
        compare_info_item(raster_info1, raster_info2, "geoTransform")
        compare_info_item(raster_info1, raster_info2, "size")

        if (
            raster_info1["driverShortName"] == "PCRaster"
            and raster_info2["driverShortName"] == "PCRaster"
        ):
            compare_info_item(raster_info1, raster_info2, "metadata")

        nr_bands1 = len(raster_info1["bands"])
        nr_bands2 = len(raster_info2["bands"])

        if nr_bands1 != nr_bands2:
            errors.append(f"nr of bands is different: {nr_bands1} != {nr_bands2}")
        else:
            for idx in range(len(raster_info1["bands"])):
                band_info1 = raster_info1["bands"][idx]
                band_info2 = raster_info2["bands"][idx]

                # compare_info_item(band_info1, band_info2, "min")
                # compare_info_item(band_info1, band_info2, "max")
                compare_info_item(band_info1, band_info2, "type")

        # Calculate the absolute and relative change.
        # - Actual change is the difference between some value and the
        #   reference value.
        # - Relative change is the relative change divided by the absolute
        #   reference value.
        # Here, the first raster is considered de reference value.
        # https://en.wikipedia.org/wiki/Relative_change_and_difference
        output_raster_pathname = os.path.join(
            output_pathname, os.path.splitext(os.path.basename(input1_pathname))[0]
        )
        actual_change_raster_pathname = f"{output_raster_pathname}_actual_change.map"
        relative_change_raster_pathname = (
            f"{output_raster_pathname}_relative_change.map"
        )

        reference_value = pcr.readmap(input1_pathname)
        some_value = pcr.readmap(input2_pathname)

        actual_change = some_value - reference_value
        relative_change = actual_change / pcr.abs(reference_value)

        pcr.report(actual_change, actual_change_raster_pathname)
        pcr.report(relative_change, relative_change_raster_pathname)

        if errors:
            errors.insert(
                0,
                f"Errors found comparing {input1_pathname} with {input2_pathname}",
            )

    return errors, warnings


def compare_directories_with_rasters(input1_pathname, input2_pathname, output_pathname):
    """
    Compare the rasters named the same, but stored in two different directories
    """
    # Both input pathnames point to directories containing rasters. We
    # need to select names of rasters that are in present in both
    # directories. For other files, we print a warning message.

    filenames1 = set(os.listdir(input1_pathname))
    filenames2 = set(os.listdir(input2_pathname))

    common_filenames = filenames1 & filenames2
    unique_filenames1 = filenames1 - filenames2
    unique_filenames2 = filenames2 - filenames1

    errors = []
    warnings = []

    for filename in unique_filenames1:
        warnings.append(
            f"Skipping file {filename} that only exists in {input1_pathname}"
        )

    for filename in unique_filenames2:
        warnings.append(
            f"Skipping file {filename} that only exists in {input2_pathname}"
        )

    for filename in common_filenames:
        raster1_pathname = os.path.join(input1_pathname, filename)
        raster2_pathname = os.path.join(input2_pathname, filename)

        if value_scale(raster1_pathname) != "VS_SCALAR":
            warnings.append(f"Skipping file {filename} that is not a scalar")

        elif not is_raster(raster1_pathname) and not is_raster(raster2_pathname):
            warnings.append(f"Skipping file {filename} that is not a raster")
        else:
            error, warning = compare_rasters(
                os.path.join(input1_pathname, filename),
                os.path.join(input2_pathname, filename),
                output_pathname,
            )
            errors += error
            warnings += warning

    return errors, warnings


@checked_call2
def diff(input1_pathname, input2_pathname, output_pathname):
    """
    Compare rasters and write the results to the output directory

    :param str input1_pathname: Pathname of raster or directory containing
        rasters
    :param str input2_pathname: Pathname of raster or directory containing
        rasters
    :param str output_pathname: Pathname of directory where results will
        be written to. This directory must exist. Same-named files will be
        overwritten.
    :raises ValueError: In case input1_pathname and input2_pathname do not
        both point to rasters or to directories
    :raises ValueError: In case output_pathname does not point to an
        existing directory

    Relative changes in values are calculated relative to the raster(s)
    pointed to by input1_pathname.
    """
    inputs_are_rasters = False
    inputs_are_directories = False

    if is_raster(input1_pathname) and is_raster(input2_pathname):
        inputs_are_rasters = True
    elif is_directory(input1_pathname) and is_directory(input2_pathname):
        inputs_are_directories = True

    if not (inputs_are_rasters or inputs_are_directories):
        raise ValueError("Input pathnames must both point to rasters or to directories")

    if not is_directory(output_pathname):
        raise ValueError(
            f"Output pathname {output_pathname} must point to an existing directory"
        )

    comparator = (
        compare_rasters if inputs_are_rasters else compare_directories_with_rasters
    )

    errors, warnings = comparator(input1_pathname, input2_pathname, output_pathname)

    if errors:
        raise RuntimeError("\n".join(errors))

    for message in warnings:
        print_warning_message(message)
