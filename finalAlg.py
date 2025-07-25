from geoThings import Circle, randomList, newCircle
from packingAlgs import radSumAlg, polyAreaAlg, randomAlg
from convPolyFuncs import convPoly
from drawFuncsV2 import setup, pshow, pdraw, drawCircles, drawPolygon

from shapely import Polygon
from math import pi


'''
this file has the function maxClusterArea, which takes in a list of radii and directly returns the area of the maximum cluster.
'''

#mainly just to make sure everything still works before a commit
def main():
    rads1 = [5]
    rads2 = [4,5]
    rads3 = [3,6,19,15,6,10,11,11]
    rads4 = [500,1850,2950,900]

    circs = radSumAlg(rads4)

    setup()
    drawCircles(circs)
    drawPolygon(convPoly(circs))
    pshow()

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

def actualClusterArea(circleList):
    if len(circleList) == 1:
        return pi*circleList[0].radius**2
    else:
        return convPoly(circleList).area


if __name__ == "__main__":
    main()