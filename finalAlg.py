from geoThings import Circle, randomList
from packingAlgs import radSumAlg, polyAreaAlg, randomAlg
from convPolyFuncs import convPoly
from drawFuncsV2 import setup, pshow, pdraw, drawCircles, drawPolygon

from shapely import Polygon
from math import pi

def maxClusterArea(radii):
    if len(radii) == 1:
        return pi*radii[0]**2 #returns area of the one circle
    if len(radii) <= 10:
        try:
            return convPoly(polyAreaAlg(radii)).area #slower, but more accurate at small number of radii
        except:
            return convPoly(radSumAlg(radii)).area #sometimes can happen that there's three circles, but effectively only 2 for the polygon, so it breaks
    else:
        return convPoly(radSumAlg(radii)).area #way faster and just about as accurate at large number of radii
