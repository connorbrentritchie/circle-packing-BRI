from shapely import Point
from math import sqrt, pi
import random

class Circle:
    def __init__(self, center: Point, radius: float):
        self.center=center
        self.radius=float(radius)
    def tupCenter(self): # returns the center of the circle as a tuple
        return (self.center.x, self.center.y)
    def data(self):
        return [(self.center.x,self.center.y), self.radius]
    def getArea(self):
        return pi*self.radius**2

class InfLine: #expressed as y=mx+b, short for infinite line
    def __init__(self, slope, yInt):
        self.m=slope
        self.b=yInt

class VertLine: #extTangents can give vertical lines, and InfLine can't represent these
    def __init__(self, xInt):
        self.xInt = xInt



#these are here because they don't fit anywhere else, and every other file imports geoThings
def fsqroot(val: float):
    if val>=0:
        return sqrt(val)
    else:
        return 0

def randomList(length,min,max):
    list=[]
    for i in range(length):
        list.append(random.randint(min,max))
    return list

def printCircleData(circList, doTerm = True):
    print('\nCIRCLE DATA')
    with open('Testing.txt','w') as testing:
        for index, circ in enumerate(circList):
            if doTerm:
                print('\nCircle number', index+1, end=' ')
                print('(testCluster index:', index, end=')\n')

                print('\tCenter:', circ.tupCenter())
                print('\tRadius:', circ.radius)

            print('\nCircle number', index+1, end=' ', file=testing)
            print('(testCluster index:', index, end=')\n', file=testing)

            print('\tCenter:', circ.tupCenter(), file=testing)
            print('\tRadius:', circ.radius, file=testing)

if __name__ == '__main__':
    print("hi command line :D")

