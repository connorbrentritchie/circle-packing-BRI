import convPolyFuncs as cpf
import packingAlgs as pa
import drawFuncsV2 as df
import shapely as sh
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


if __name__ == "__main__":
    unittest.main()
    main()