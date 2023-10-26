#!/usr/bin/env python
"""
Example script to determine projected coordinates, given geographical
coordinates
"""
import sys

from pyproj import Transformer


def main():
    """
    Main entry point of the command
    """
    wgs_84 = "epsg:4326"
    rd_new = "epsg:28992"
    transformer = Transformer.from_crs(wgs_84, rd_new)

    angle_tuples = [
        (52.2746, 4.6665),
        (52.4743, 5.1270),
    ]

    for angle_tuple in angle_tuples:
        lat, lon = angle_tuple
        x, y = transformer.transform(lat, lon)  # pylint: disable=E0633

        print(f"{lat}, {lon} -> {x}, {y}")


if __name__ == "__main__":
    sys.exit(main())
