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
    df.drawLines(lines)
    # df.drawPolygon(cpf.convPoly(circs))
    df.pshow()


class Testing(unittest.TestCase):
    def setUp(self):
        testRadii1 = [5,6,7,8]
        self.testCircleList1 = pa.radSumAlg(testRadii1)
        self.testPolygon1 = cpf.convPoly(self.testCircleList1)
        
        testRadii2 = [500,1850,2950,900]
        self.testCircleList2 = pa.polyAreaAlg(testRadii2)
        self.testPolygon2 = cpf.convPoly(self.testCircleList2)
    
    def test_convPoly_one_circle_throws_error(self):
        circ = Circle(Point(0,0), 5.0)
        with self.assertRaises(Exception):
            cpf.convPoly(circ)

    def test_convPoly_2_circles_returns_rectangle(self):
        circs = pa.radSumAlg([5,5])
        poly = cpf.convPoly(circs)
        self.assertTrue(isclose(
            poly.area, 200.0
        ))

    def test_convPoly_checkPolygon_workaround(self):
        self.assertAlmostEqual(52575222.6210679, self.testPolygon2.area, 3)

    def test_checkPolygon_1(self):
        self.assertTrue(cpf.checkPolygon(self.testCircleList1, self.testPolygon1))


if __name__ == "__main__":
    do_tests = True
    if do_tests == True:
        unittest.main()
    else:
        main()