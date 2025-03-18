from packingAlgs import radSumAlg, randomAlg
from geoThings import Circle, InfLine, VertLine, fsqroot, randomList, printCircleData
from drawFuncsV2 import setup, pshow, pdraw, drawCircles, drawPoints, drawLines, drawSegments, drawPolygon, drawBox

import math
import random
import shapely as sh
from shapely import Point, LineString, Polygon
import matplotlib.pyplot as plt
import time

def main():

    radii = randomList(15,10,20)
    radii1 = [3,6]
    radii3 = randomList(50,2,3)

    testc = radSumAlg(radii)
    bounds = configBounds(testc)
    cHull = centerHull(testc)

    printCircleData(testc)

    testp = convPoly(testc)


    setup(12,9)
    drawCircles(testc)
    drawPolygon(testp, 'green')
    pshow()


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



def allValidTangents(circleList, testDraw = False): #takes a list of circles and returns all of the valid exterior tangents
    #setup
    cHull = centerHull(circleList)
    bounds = configBounds(circleList)
    validTans = [] #list of all valid tangents
    if testDraw == True:
        setup(12,9)

    #finds the circles corresponding to vertices of cHull
    vertices = list(cHull.exterior.coords) #vertices of cHull
    centerList = [c.center for c in circleList] #centers of circleList in same order as the circles
    outerCircs = []
    for v in vertices:
        outerCircs.append(
            circleList[centerList.index(Point(v))]
            )
    print([circleList.index(c)+1 for c in outerCircs])


    #actually finds the valid tangents
    #sets everything up for while loop
    startCirc = sorted(outerCircs, key = lambda x: x.radius, reverse = True)[0] #chooses the largest circle from outerCircs as the starting circle
    print('startCircle:',circLabel(startCirc, circleList))
    currentCirc = startCirc #starts the while loop on startCirc
    prevCircs = [startCirc] #so prevCircs isn't empty the first time the while loop checks it



    #logic that actually finds and adds all the valid tangents
    done = False #initializes done
    count = 1
    while done == False:
        print('\n\n\nCURRENT CYCLE:', count)
        print('Current circle is', circLabel(currentCirc, circleList))

        potentials = [] #the list of all potential valid tangents

        #Finds all potential tangents
        #ignores currentCirc since cant have tangent from circle to itself, breaks extTangents
        #ignores previous circle since we just got a tangent from there, would risk infinite loop
        print('ignored circles for for loop:', [circLabel(currentCirc, circleList), circLabel(prevCircs[-1], circleList)])
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
                                print('same slope at', circLabel(circ, circleList))

                    if not anyVerts and math.isclose(tan.m, prevTan.m, rel_tol=1e-10):
                        sameSlope = True
                        print('same slope at', circLabel(circ, circleList))


                if isValidTangent(tanSeg, circleList) and not sameSlope: #add to potentials if valid, does nothing if not
                    potentials.append([(tan, tanSeg), circ])

        #choose which tan to add to validTans, updates currentCirc and prevCircs
        if potentials != []: #potentials always supposed to have at least one thing in it
            print('\npotential circles:', [circLabel(x[1], circleList) for x in potentials])
            print('potentials data:', [
                (circLabel(x[1], circleList),
                x[1].center.distance(currentCirc.center)
                ) for x in potentials])
            #sorts potentials by how far the other circle is from currentCirc
            sortedPotentials = sorted(
                potentials,
                key = lambda x: x[1].center.distance(currentCirc.center),
                reverse = True
                )

            bestTan, bestCirc = sortedPotentials[0] #chooses the farthest possible thing from currentCircle

            print('best circle:', circLabel(bestCirc, circleList))
            if type(bestTan[0]) is VertLine:
                print('best tan line xInt:', bestTan[0].xInt)
            else:
                print('best tan line:', bestTan[0].m, bestTan[0].b)
            print('best tanSeg:', bestTan[1])
            validTans.append(bestTan) #adds the valid tangent to validTans
            prevCircs.append(currentCirc) #adds currentCirc to prevCircs, so it's ignored by for loop next cycle
            currentCirc = bestCirc #redefines currentCirc as bestCirc, essentially leapfrogs around the diagram

            if currentCirc == startCirc: #ends the while loop if the currentCircle is the starting circle, since we've gone all the way around
                done = True
                print('reached done')
        else: #not supposed to happen
            print('No possible tangents at', circLabel(currentCirc, circleList))
            break

        if testDraw == True:
            drawCircles(circleList)
            drawPolygon(cHull)
            drawSegments([x[1] for x in validTans])
            pshow()

        count+=1

    print('\n\nFinished Tangents')
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

def convPoly(circleList):
    #separate logic for 1, 2, and 3+ circles
    if len(circleList) == 1: #defines a square
        c = circleList[0].center
        r = circleList[0].radius
        v1 = Point(c.x-r,c.y-r)
        v2 = Point(c.x-r,c.y+r)
        v3 = Point(c.x+r,c.y+r)
        v4 = Point(c.x+r,c.y-r)
        convPoly = Polygon([v1,v2,v3,v4,v1])

        return convPoly

    if len(circleList) == 2: #defines a trapezoid type thing
        sortedCircs = sorted(circleList, key = lambda x: x.tupCenter())
        c1 = sortedCircs[0]
        c2 = sortedCircs[1]
        tan1, tan3 = extTangents(c1,c2)

        centerSeg = LineString([c1.tupCenter(), c2.tupCenter()])
        slope = (c2.center.y - c1.center.y)/(c2.center.x-c1.center.x)
        perpSlope = -1/slope
        print(slope, perpSlope)

        angle1 =  math.atan(slope)
        angle2 = angle1 + math.pi
        print(math.degrees(angle1), math.degrees(angle2))

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
        convPoly = Polygon(intPoints + [intPoints[0]])

        return convPoly

    else:
        exteriorTangents = [t[0] for t in allValidTangents(circleList)]
        intPoints = []
        for index in range(len(exteriorTangents)):
            tN = exteriorTangents[index]
            tNp1 = exteriorTangents[(index+1)%len(exteriorTangents)]

            intPoints.append(findIntPoint(tN, tNp1))

        convPoly = Polygon(intPoints + [intPoints[0]])

        return convPoly


if __name__ == '__main__':
    main()
