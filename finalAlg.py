from geoThings import Circle, randomList
from packingAlgs import radSumAlg, polyAreaAlg, randomAlg
from convPolyFuncs import convPoly
from drawFuncsV2 import setup, pshow, pdraw, drawCircles, drawPolygon

from shapely import Polygon
from math import pi

#mainly just to make sure everything still works before a commit
def main():
    rads1 = [5]
    rads2 = [4,5]
    rads3 = [3,6,19,15,6,10,11,11]
    rads4 = [500,1850,2950,900]

    print(1)

    print(maxClusterArea(rads1), maxClusterArea(rads2), maxClusterArea(rads3), maxClusterArea(rads4))

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

if __name__ == "__main__":
    main()