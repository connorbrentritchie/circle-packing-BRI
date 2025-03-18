import convPolyFuncs as cpf
import packingAlgs as pa
import drawFuncsV2 as df
from shapely import Point, Polygon
from geoThings import Circle, InfLine, VertLine
from math import isclose, pi
import unittest


def main():    
    radii = [500,1850,2950,900]
    circs = pa.radSumAlg(radii)

    lines = [thing[0] for thing in cpf.allValidTangents(circs)]
    lineSegs = [thing[1] for thing in cpf.allValidTangents(circs)]

    df.setup()
    df.drawCircles(circs)
    df.drawSegments(lineSegs)
    df.pshow()


class Testing(unittest.TestCase):
    def test_sum(self):
        self.assertEqual(3, 2 + 1)
    

    def test_convPoly_returns_area_of_circle_with_only_one_circle(self):
        circ = Circle(Point(0,0), 5.0)
        polyArea = cpf.convPoly([circ])
        self.assertTrue(isclose(
            polyArea, 25.0 * pi
        ))

    def test_convPoly_2_circles_returns_rectangle(self):
        circs = pa.radSumAlg([5,5])
        poly = cpf.convPoly(circs)
        self.assertTrue(isclose(
            poly.area, 200.0
        ))


if __name__ == "__main__":
    unittest.main()
    main()