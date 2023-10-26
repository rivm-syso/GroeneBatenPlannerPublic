"""
This module contains functions that can be used during the development
of models

Depending on the cost of the assertion function you use, you may want
to keep the test in the production version of your model
"""
import collections.abc
import numbers

import pcraster as pcr


def less_equal_than(data, upper_bound):
    """
    Assert that *data* <= upper_bound

    :param data: A raster or a number, or an iterable of zero or more rasters
        or numbers
    :param upper_bound: The upper bound of valid values
    :raises RuntimeError: In case *data* contains at least one
        valid value and the upper bound in *data* is larger
        than *upper_bound*
    """
    if isinstance(data, collections.abc.Iterable):
        for item in data:
            less_equal_than(item, upper_bound)
    else:
        if isinstance(data, numbers.Number):
            upper_bound_in_collection = data
        else:
            upper_bound_in_collection, is_valid = pcr.cellvalue(pcr.mapmaximum(data), 0)

            if not is_valid:
                return

        if upper_bound_in_collection > upper_bound:
            raise RuntimeError(
                f"Out of range values: {upper_bound_in_collection} > {upper_bound}"
            )


def greater_equal_than(data, lower_bound):
    """
    Assert that *lower_bound* <= *data*

    :param data: A raster or a number, or an iterable of zero or more rasters
        or numbers
    :param lower_bound: The lower bound of valid values
    :raises RuntimeError: In case *data* contains at least one
        valid value and the lower bound in *data* is smaller
        than *lower_bound*
    """
    if isinstance(data, collections.abc.Iterable):
        for item in data:
            greater_equal_than(item, lower_bound)
    else:
        if isinstance(data, numbers.Number):
            lower_bound_in_collection = data
        else:
            lower_bound_in_collection, is_valid = pcr.cellvalue(pcr.mapminimum(data), 0)

            if not is_valid:
                return

        if lower_bound_in_collection < lower_bound:
            raise RuntimeError(
                f"Out of range values: {lower_bound_in_collection} < {lower_bound}"
            )


def in_range(data, lower_bound, upper_bound):
    """
    Assert that *lower_bound* <= *data* <= *upper_bound*

    :param data: A raster or a number, or an iterable of zero or more rasters
        or numbers
    :param lower_bound: The lower bound of valid values
    :param upper_bound: The upper bound of valid values
    :raises RuntimeError: In case *data* contains at least one
        valid value and the lower bound in *data* is smaller
        than *lower_bound* or the upper bound in *data* is larger
        than *upper_bound*
    """
    greater_equal_than(data, lower_bound)
    less_equal_than(data, upper_bound)
