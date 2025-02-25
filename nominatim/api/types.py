# SPDX-License-Identifier: GPL-3.0-or-later
#
# This file is part of Nominatim. (https://nominatim.org)
#
# Copyright (C) 2023 by the Nominatim developer community.
# For a full list of authors see the git log.
"""
Complex datatypes used by the Nominatim API.
"""
from typing import Optional, Union, NamedTuple
import dataclasses
import enum
from struct import unpack

@dataclasses.dataclass
class PlaceID:
    """ Reference an object by Nominatim's internal ID.
    """
    place_id: int


@dataclasses.dataclass
class OsmID:
    """ Reference by the OSM ID and potentially the basic category.
    """
    osm_type: str
    osm_id: int
    osm_class: Optional[str] = None

    def __post_init__(self) -> None:
        if self.osm_type not in ('N', 'W', 'R'):
            raise ValueError(f"Illegal OSM type '{self.osm_type}'. Must be one of N, W, R.")


PlaceRef = Union[PlaceID, OsmID]


class Point(NamedTuple):
    """ A geographic point in WGS84 projection.
    """
    x: float
    y: float


    @property
    def lat(self) -> float:
        """ Return the latitude of the point.
        """
        return self.y


    @property
    def lon(self) -> float:
        """ Return the longitude of the point.
        """
        return self.x


    def to_geojson(self) -> str:
        """ Return the point in GeoJSON format.
        """
        return f'{{"type": "Point","coordinates": [{self.x}, {self.y}]}}'


    @staticmethod
    def from_wkb(wkb: bytes) -> 'Point':
        """ Create a point from EWKB as returned from the database.
        """
        if len(wkb) != 25:
            raise ValueError("Point wkb has unexpected length")
        if wkb[0] == 0:
            gtype, srid, x, y = unpack('>iidd', wkb[1:])
        elif wkb[0] == 1:
            gtype, srid, x, y = unpack('<iidd', wkb[1:])
        else:
            raise ValueError("WKB has unknown endian value.")

        if gtype != 0x20000001:
            raise ValueError("WKB must be a point geometry.")
        if srid != 4326:
            raise ValueError("Only WGS84 WKB supported.")

        return Point(x, y)


class GeometryFormat(enum.Flag):
    """ Geometry output formats supported by Nominatim.
    """
    NONE = 0
    GEOJSON = enum.auto()
    KML = enum.auto()
    SVG = enum.auto()
    TEXT = enum.auto()


@dataclasses.dataclass
class LookupDetails:
    """ Collection of parameters that define the amount of details
        returned with a search result.
    """
    geometry_output: GeometryFormat = GeometryFormat.NONE
    """ Add the full geometry of the place to the result. Multiple
        formats may be selected. Note that geometries can become quite large.
    """
    address_details: bool = False
    """ Get detailed information on the places that make up the address
        for the result.
    """
    linked_places: bool = False
    """ Get detailed information on the places that link to the result.
    """
    parented_places: bool = False
    """ Get detailed information on all places that this place is a parent
        for, i.e. all places for which it provides the address details.
        Only POI places can have parents.
    """
    keywords: bool = False
    """ Add information about the search terms used for this place.
    """
