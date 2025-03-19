from geoThings import Circle, InfLine, VertLine, fsqroot, randomList, printCircleData
from drawFuncsV2 import setup, pshow, pdraw, drawCircles, drawPoints, drawLines, drawSegments, drawPolygon, drawBox

import math
import random
import shapely as sh
from shapely import Point, LineString, Polygon
import matplotlib.pyplot as plt

def main():
    circ = Circle(Point(0,0),5)

def circLabel(circ, circleList): #finds the label of a circle on the drawing
    return circleList.index(circ)+1


#Convex polygon calculation functions
def extTangents(circ1, circ2): #calculates the two exterior tangents, notation from wikipedia page on tangent lines to circles
    #takes two circles, gives the ext tangents

    #gets both tangents
    x1,y1=circ1.tupCenter()
    r1=circ1.radius

    x2,y2=circ2.tupCenter()
    r2=circ2.radius

    dx=x2-x1
    dy=y2-y1
    dr=r2-r1

    D=circ1.center.distance(circ2.center)

    nx = dx/D
    ny = dy/D
    nr = dr/D

    k1 = 1 #these are for giving both tangent lines
    k2 = -1

    a1 = nr*nx - k1*ny*fsqroot(1-nr**2) #for ax+by+c=0 line expression
    b1 = nr*ny + k1*nx*fsqroot(1-nr**2)
    c1 = r1 - (a1*x1 + b1*y1)

    a2 = nr*nx - k2*ny*fsqroot(1-nr**2)
    b2 = nr*ny + k2*nx*fsqroot(1-nr**2)
    c2 = r2 - (a2*x2 + b2*y2)

    try:
        m1 = -1*a1/b1 #for y=mx+b expression
        b1 = -1*c1/b1
        ext1 = InfLine(m1,b1)
    except ZeroDivisionError: #in case of vertical line
        ext1=VertLine(c1)

    try:
        m2 = -1*a2/b2
        b2 = -1*c2/b2
        ext2 = InfLine(m2,b2)
    except ZeroDivisionError: #in case of vertical line
        ext2=VertLine(-1*c2)

    exts = [ext1, ext2]
    return exts


def centerHull(circleList): #finds convex hull of the centers of a list of circles
    return sh.convex_hull(sh.MultiPoint([c.tupCenter() for c in circleList]))

def configBounds(circleList):
    cHull = centerHull(circleList)

    maxRadius = sorted(
        circleList, key = lambda x: x.radius, reverse=True #is still a list of circles
        )[0].radius #takes the first circle and its radius

    aminx, aminy, amaxx, amaxy = cHull.bounds #bounds of centerHull
    minx, miny, maxx, maxy = ( #adds extra room
        aminx - 2*maxRadius,
        aminy - 2*maxRadius,
        amaxx + 2*maxRadius,
        amaxy + 2*maxRadius
        )
    bounds = (minx,miny,maxx,maxy)
    return bounds

def lineToSegment(line, bounds): #converts InfLine or VertLine to shapely LineString, bounds defines box that LineString is contained in
    minx, miny, maxx, maxy = bounds
    boundingBox = sh.box(minx,miny,maxx,maxy) #shapely polygon version of bounding box

    if type(line) is VertLine: #catches vertical lines
        segment = sh.LineString([
            (line.xInt, miny),
            (line.xInt, maxy)
            ])

    elif line.m == 0: #catches horizontal lines
        segment=sh.LineString([
                (minx,line.b),
                (maxx,line.b)
                ])

    else:
        y0 = line.m * minx + line.b
        y1 = line.m * maxx + line.b
        x0 = (miny - line.b)/line.m
        x1 = (maxy - line.b)/line.m

        bpoints = [Point(x0,miny),Point(x1,maxy),Point(minx,y0),Point(maxx,y1)]

        sorted_bpoints = sorted(bpoints, key = lambda x : boundingBox.distance(x))

        segment=sh.LineString(sorted_bpoints[:2])

    return segment


def isIntersecting(seg, circ): #if seg is tangent to circ, returns false
    return seg.distance(circ.center) +.00000001 < circ.radius #floating point stuff

def isValidTangent(tanSeg, circleList):
    cHull = centerHull(circleList)

    #cond1 checks that tanSeg DOESN'T intersect centerHull
    cond1 = not tanSeg.intersects(cHull)

    #cond2 checks that tanSeg DOESN'T intersect with any circle in circleList
    #able to check every circle without restriction since isIntersecting returns False if tanSeg and circ are tangent
    cond2 = True #starts as True, set to False if intersection detected
    for circ in circleList:
        if isIntersecting(tanSeg, circ):
            cond2 = False
            break

    if cond1 and cond2: #if both conditions are met, tanSeg is valid
        return True
    else:
        return False

# largestOuterCirc :: [Circle] -> Circle
#gets circle of largest radius on the center hull
def largestOuterCirc(circleList):
    cHull = centerHull(circleList)
    
    #finds the circles corresponding to vertices of cHull
    vertices = list(cHull.exterior.coords) #vertices of cHull
    centerList = [c.center for c in circleList] #centers of circleList in same order as the circles
    outerCircs = []
    for v in vertices:
        outerCircs.append(
            circleList[centerList.index(Point(v))]
            )
    return sorted(outerCircs, key = lambda x: x.radius, reverse = True)[0] #chooses the largest circle from outerCircs as the starting circle


# allValidTangents :: [Circle] -> Bool -> [(InfLine, LineString)]
def allValidTangents(circleList, testDraw = False): #takes a list of circles and returns all of the valid exterior tangents
    #setup
    cHull = centerHull(circleList)
    bounds = configBounds(circleList)
    validTans = [] #list of all valid tangents
    if testDraw == True:
        setup(12,9)

    #actually finds the valid tangents
    #sets everything up for while loop
    startCirc = largestOuterCirc(circleList)
    currentCirc = startCirc #starts the while loop on startCirc
    prevCircs = [startCirc] #so prevCircs isn't empty the first time the while loop checks it



    #logic that actually finds and adds all the valid tangents
    done = False #initializes done
    count = 1
    while done == False:

        potentials = [] #the list of all potential valid tangents

        #Finds all potential tangents
        #ignores currentCirc since cant have tangent from circle to itself, breaks extTangents
        #ignores previous circle since we just got a tangent from there, would risk infinite loop
        for circ in [c for c in circleList if not (c == currentCirc or c == prevCircs[-1])]: #checks all circles that aren't currentCirc or the previous circle
            tans = extTangents(currentCirc, circ)
            for tan in tans: #since extTangents returns a pair of lines
                tanSeg = lineToSegment(tan,bounds)

                #checks that the current tan isn't the same slope as the previous one
                sameSlope = False #default value
                if validTans != []: #only possible if there even is a previous tangent
                    prevTan = validTans[-1][0] #gets the previous tangent line
                    anyVerts = type(tan) is VertLine or type(prevTan) is VertLine
                    if anyVerts:
                        if type(tan) is VertLine and type(prevTan) is VertLine:
                            if math.isclose(tan.xInt, prevTan.xInt, rel_tol=1e-10):
                                sameSlope = True

                    if not anyVerts and math.isclose(tan.m, prevTan.m, rel_tol=1e-10):
                        sameSlope = True


                if isValidTangent(tanSeg, circleList) and not sameSlope: #add to potentials if valid, does nothing if not
                    potentials.append([(tan, tanSeg), circ])

        #choose which tan to add to validTans, updates currentCirc and prevCircs
        if potentials != []: #potentials always supposed to have at least one thing in it
            #sorts potentials by how far the other circle is from currentCirc
            sortedPotentials = sorted(
                potentials,
                key = lambda x: x[1].center.distance(currentCirc.center),
                reverse = True
                )

            bestTan, bestCirc = sortedPotentials[0] #chooses the farthest possible thing from currentCircle

            validTans.append(bestTan) #adds the valid tangent to validTans
            prevCircs.append(currentCirc) #adds currentCirc to prevCircs, so it's ignored by for loop next cycle
            currentCirc = bestCirc #redefines currentCirc as bestCirc, essentially leapfrogs around the diagram

            if currentCirc == startCirc: #ends the while loop if the currentCircle is the starting circle, since we've gone all the way around
                done = True
        else: #not supposed to happen
            break

        if testDraw == True:
            drawCircles(circleList)
            drawPolygon(cHull)
            drawSegments([x[1] for x in validTans])
            pshow()

        count+=1

    return validTans



def findIntPoint(line1,line2): #takes two InfLines and finds the intersection
    if type(line1) is VertLine:
        result = Point(line1.xInt, line2.m*line1.xInt + line2.b)
    elif type(line2) is VertLine:
        result = Point(line2.xInt, line1.m*line2.xInt + line1.b)
    else:
        a=line1.m
        b=line2.m
        c=line1.b
        d=line2.b

        result = Point((d-c)/(a-b),a*(d-c)/(a-b)+c)

    return result



#sometimes with 2 big circles and some small ones, it breaks
#example is [50,1850,1950]
#bandaid fix for now is to try except into just doing convPoly of the first two circles
def convPoly(circleList):
    #separate logic for 1, 2, and 3+ circles
    if len(circleList) == 1: #throws an error, should be handled by maxClusterArea
        raise Exception("Can't make polygon from one circle, should have been handled by maxClusterArea")

    if len(circleList) == 2: #defines a trapezoid type thing
        sortedCircs = sorted(circleList, key = lambda x: x.tupCenter())
        c1 = sortedCircs[0]
        c2 = sortedCircs[1]
        tan1, tan3 = extTangents(c1,c2)

        centerSeg = LineString([c1.tupCenter(), c2.tupCenter()])
        slope = (c2.center.y - c1.center.y)/(c2.center.x-c1.center.x)
        perpSlope = -1/slope

        angle1 =  math.atan(slope)
        angle2 = angle1 + math.pi

        newx1 = c1.radius * math.cos(angle2) + c1.center.x
        newy1 = c1.radius * math.sin(angle2) + c1.center.y

        newx2 = c2.radius * math.cos(angle1) + c2.center.x
        newy2 = c2.radius * math.sin(angle1) + c2.center.y

        tan2 = InfLine(perpSlope, newy1 - perpSlope*newx1)
        tan4 = InfLine(perpSlope, newy2 - perpSlope*newx2)

        tans = [tan1,tan2,tan3,tan4]

        intPoints = []
        for index in range(len(tans)):
            tN = tans[index]
            tNp1 = tans[(index+1)%len(tans)]
            intPoints.append(findIntPoint(tN, tNp1))
        resultConvPoly = Polygon(intPoints + [intPoints[0]])

        return resultConvPoly

    else:
        try:
            #default algorithm
            tangentTuples = allValidTangents(circleList)
            exteriorTangents = [t[0] for t in tangentTuples]
            
            intPoints = []
            for index in range(len(exteriorTangents)):
                tN = exteriorTangents[index]
                tNp1 = exteriorTangents[(index+1)%len(exteriorTangents)]

                intPoints.append(findIntPoint(tN, tNp1))

            resultConvPoly = Polygon(intPoints + [intPoints[0]])
            
            #checks to see if the polygon is actually valid. If not, takes first and last tangent and adds a tangent to the first circle and redoes finding the intersection points to hopefully complete the polygon.
            if not checkPolygon(circleList, resultConvPoly):
                #adds a horizontal line on the starting Circle
                startCirc = largestOuterCirc(circleList)
                newTangent1 = InfLine(0.0, startCirc.center.y - startCirc.radius)
                newTangent2 = InfLine(0.0, startCirc.center.y + startCirc.radius)
                bounds = configBounds(circleList)

                newTanSeg1, newTanSeg2 = lineToSegment(newTangent1, bounds), lineToSegment(newTangent2, bounds)

                if isValidTangent(newTanSeg1, circleList):
                    exteriorTangents.append(newTangent1)
                elif isValidTangent(newTanSeg2, circleList):
                    exteriorTangents.append(newTangent2)
                else:
                    raise Exception("Adding horizontal tangent failed (from checkPolygon fail)\n", "radii:", list(map(lambda c: c.radius, circleList)))

                intPoints = []
                for index in range(len(exteriorTangents)):
                    tN = exteriorTangents[index]
                    tNp1 = exteriorTangents[(index+1)%len(exteriorTangents)]

                    intPoints.append(findIntPoint(tN, tNp1))

                resultConvPoly = Polygon(intPoints + [intPoints[0]])
            
            return resultConvPoly

        except: #sometimes breaks as described above, just does the correct alg with the first two circles in the list
            return convPoly(circleList[:2])



# checkPolygon :: [Circle] -> shapely Polygon -> Bool
#checks if all the circles are inside the polygon, and the area of the polygon is bigger than the sum of all the circles' area
def checkPolygon(circleList, polygon):
    cond1 = polygon.covers(centerHull(circleList))

    cond2 = polygon.area > sum(map(lambda c: c.getArea(), circleList))

    if not cond1:
        print("checkPolygon failed: polygon does not contain some or all circles")
        print("radii", list(map(lambda c: c.radius, circleList)))
    if not cond2:
        print("cond2 failed: polygon area smaller than expected")
        print("radii", list(map(lambda c: c.radius, circleList)))

    return cond1 & cond2


if __name__ == '__main__':
    main()
