from geoThings import Circle, newCircle

import pandas as pd
from shapely import Point, Polygon
import simplekml as skml
import utm

'''
utm uses lat, lon
kml.newpoint uses lon lat
'''


test_filepath = "D:\\Work\\QGIS Stuff\\TestStuff\\"
coord = (42.068611, -111.786667)

east, north, znum, zletter = utm.from_latlon(coord[0], coord[1])


kml = skml.Kml()

p1 = kml.newpoint(
    name = "Point1",
    coords = [(45, -70)[::-1]]
)

p2 = kml.newpoint(
    name = "Point2",
    coords = [(45, -71)[::-1]]
)

v1 = utm.to_latlon(east, north, znum, zletter)[::-1]
v2 = utm.to_latlon(east + 100, north, znum, zletter)[::-1]
v3 = utm.to_latlon(east + 100, north + 100, znum, zletter)[::-1]
v4 = utm.to_latlon(east, north + 100, znum, zletter)[::-1]

poly = kml.newpolygon(
    name = "Square",
    outerboundaryis = [v1,v2,v3,v4]
)

kml.document.name = "Potato"

kml.savekmz(test_filepath + "testing.kml")
print('yay')