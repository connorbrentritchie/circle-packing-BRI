import math
import random
import shapely as sh
from shapely import Point
import matplotlib.pyplot as plt
import openpyxl as pxl


class Circle:
    def __init__(self, center: sh.Point, radius: float):
        self.center=center
        self.radius=float(radius)
    def tupCenter(self): # returns the center of the circle as a tuple
        return (self.center.x, self.center.y)

class InfLine: #expressed as y=mx+b
    def __init__(self, slope, yInt):
        self.m=slope
        self.b=yInt

class VertLine: #extTangents can give vertical lines
    def __init__(self, xInt):
        self.xInt = xInt


def main():

    width_of_fig = 12
    height_of_fig = 10
    '''
    testRadii1 = [9,8,5]
    testRadii1a = [9,9,8,5]
    testRadii2 = [10,8.5,7.5,3.5,3,1.5]
    testRadii3 = [15,14,13,10,8,2,1.5,1]

    radii=testRadii3

    answer=getRadii()
    radii=answer[0]
    resultCell=answer[1]
    radii.sort()
    radii.reverse()

    testCluster = randomClusterAlg(radii)
    #testCluster=radSumClusterAlg(radii)

    centerHull = sh.convex_hull(sh.MultiPoint([c.tupCenter() for c in testCluster]))

    testTangents = validExtTangents(testCluster)
    allTestLines = [t[0] for t in testTangents[1]]
    allTestSegs = [t[1] for t in testTangents[1]]
    validTestLines = [t[0] for t in testTangents[0]]
    validTestSegs = [t[1] for t in testTangents[0]]
    #validTangents, allTangents, [(minx, miny),(maxx,maxy)]

    #drawComplete(width_of_fig, height_of_fig, testCluster, centerHull, testTangents[2], validTestLines, None)
    drawComplete(width_of_fig, height_of_fig, testCluster, centerHull, testTangents[2], None, validTestSegs)
    #Order: drawComplete(width, height, circleList=None, polygon=None, pointList=None, lineList=None, lineSegList=None)

    #printCircleData(testCluster)
    '''



#Misc functions
def fsqroot(val):
    try:
        return math.sqrt(val)
    except:
        print('ERROR', val)
        return 0

def printCircleData(circList):
    print('\nCIRCLE DATA')
    for index, circ in enumerate(circList):
        print('\nCircle number', index+1, end=' ')
        print('(testCluster index:', index, end=')\n')

        print('\tCenter:', circ.tupCenter())
        print('\tRadius:', circ.radius)

#Drawing
def drawComplete(width, height, circleList=None, polygon=None, pointList=None, lineList=None, lineSegList=None): #draws list of circles
    # Create a figure and axis
    fig, ax = plt.subplots()
    fig.set_figwidth(width)
    fig.set_figheight(height)

    if circleList is not None: #draws circles
        for k in range(len(circleList)):
            circ=plt.Circle(circleList[k].tupCenter(), circleList[k].radius, fill=False)
            ax.add_patch(circ)

            dx=circleList[k].center.x #x and y coords of center of kth circle
            dy=circleList[k].center.y

            plt.plot(dx, dy, 'bo')

            label=str(k+1)
            plt.annotate(label,
                        (dx, dy),
                        textcoords = "offset points",
                        xytext=(7,7),
                        ha='center')

    if polygon is not None: #draws polygon
        vertices = list(polygon.exterior.coords)
        for i in range(len(vertices)-1):
            xs=(vertices[i][0], vertices[i+1][0])
            ys=(vertices[i][1], vertices[i+1][1])
            plt.plot(xs, ys, 'r-')
            plt.plot(vertices[i][0],vertices[i][1], 'ro')

    if pointList is not None:
        xs = [p[0] for p in pointList]
        ys = [p[1] for p in pointList]
        rect = plt.Rectangle((xs[0],ys[0]), xs[1]-xs[0], ys[1]-ys[0], fill = False)

        plt.plot(xs, ys, 'gp')
        ax.add_patch(rect)

    if lineList is not None:
        anyVerts=False
        for line in lineList:
            if type(line) is VertLine:
                ax.axvline(line.xInt)
                anyVerts = True
            else:
                ax.axline(
                    (0,line.b),
                    slope=line.m,
                    color='C' + str(math.floor(lineList.index(line)/2))
                    )
        if anyVerts == True:
            print('Vertical line detected')

    if lineSegList is not None:
        for seg in lineSegList:
            x0 = list(seg.coords)[0][0]
            x1 = list(seg.coords)[1][0]
            y0 = list(seg.coords)[0][1]
            y1 = list(seg.coords)[1][1]
            plt.plot([x0,x1],[y0,y1],color='C' + str(lineSegList.index(seg)), marker='+')

    ax.grid(True, which='both')
    ax.axhline(y=0, color='k')
    ax.axvline(x=0, color='k')

    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)
    plt.axis('equal')  # To ensure the aspect ratio is maintained
    plt.show(block=True)




#Excel
wb=pxl.load_workbook('Circle Data.xlsx')
sheet=wb['Sheet1']

def getRadii():
    startCell=str(input('Enter starting cell: '))
    column=startCell[0]
    index=int(startCell[1])
    radii=[]
    while True:
        if sheet[column+str(index)].value == None:
            break
        radii.append(
            float(sheet[column+str(index)].value)
            )
        index+=1
    finalCell=column + str(index)
    return radii, finalCell

#Convex polygon calculation functions
def extTangents(circ1, circ2): #calculates two exterior tangents, notation from wikipedia page on tangent lines to circles
    #takes two circles, gives the two exterior tangents as [InfLine1, InfLine2]
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

    return ext1, ext2

def doesLineIntersectCircle(line, circ): #does what it says, takes LineString and Circle, returns bool

    l1,l2=list(line.coords)

    slope=(l2.y - l1.y)/(

    d = -1*1/slope #for slope of diameter

    #Done at origin
    R = circ.radius**2
    A = d**2+1
    B = 0
    C = -R

    prex1 = (-B + fsqroot(B**2-4*A*C))/(2*A)
    prex2 = (-B - fsqroot(B**2-4*A*C))/(2*A)
    prey1 = d*prex1
    prey2 = d*prex2

    #Translated to actual spot
    p1 = (prex1 - circ.center.x, prey1 - circ.center.y)
    p2 = (prex2 - circ.center.x, prey2 - circ.center.y)

    diam = sh.LineString[p1,p2]
    print(diam)

    return diam.intersect(line)



def validExtTangents(circleList): #takes a list of circles and returns all of the valid exterior tangents
    #setup
    allTangents=[] #each element is a tuple of the InfLine and its clipped version: (InfLine, LineString)
    validTangents=[] #same, but now just the valid ones
    centerHull = sh.convex_hull(
        sh.MultiPoint([c.tupCenter() for c in circleList])
        )


    #converts centerHull back into a list of circles
    outerCircles=[]
    centerList=[c.center for c in circleList] #these two in same order, reference same objects
    hullPoints = [Point(p) for p in list(centerHull.exterior.coords)] #list of centerHull vertices as points

    for hullp in hullPoints: #takes each hullp, finds index in centerList, adds circle with same index from circleList
        outerCircles.append(
            circleList[centerList.index(hullp)]
            )


    #gets the bounds on the circle collection
    maxRadius = sorted(
        circleList, key = lambda x: x.radius, reverse=True #is still a list of circles
        )[0].radius #takes the first circle and its radius

    aminx, aminy, amaxx, amaxy = centerHull.bounds #bounds of centerHull
    minx, miny, maxx, maxy = ( #adds extra room
        aminx - 2*maxRadius,
        aminy - 2*maxRadius,
        amaxx + 2*maxRadius,
        amaxy + 2*maxRadius
        )
    boundingBox = sh.box(minx,miny,maxx,maxy) #shapely polygon version of bounding box


    #gets all the tangents from outerCircles
    for index, circ in enumerate(outerCircles):
        if index == len(outerCircles)-1: #last circle is a copy of the first, so skip it
            break
        else:
            ithTangents = extTangents(outerCircles[index], outerCircles[index+1])
            for line in ithTangents:
                #converts InfLine to line segment
                clippedLine=None
                if type(line) is VertLine: #catches vertical lines
                    clippedLine = sh.LineString([
                        (line.xInt, miny),
                        (line.xInt, maxy)
                        ])

                elif line.m == 0: #catches horizontal lines
                    clippedLine=sh.LineString([
                            (minx,line.b),
                            (maxx, line.b)
                            ])

                else:
                    y0 = line.m * minx + line.b
                    y1 = line.m * maxx + line.b
                    x0 = (miny - line.b)/line.m
                    x1 = (maxy - line.b)/line.m

                    bpoints = [Point(x0,miny),Point(x1,maxy),Point(minx,y0),Point(maxx,y1)]

                    sorted_bpoints = sorted(bpoints, key = lambda x : boundingBox.distance(x))

                    clippedLine=sh.LineString(sorted_bpoints[:2])

                #adds to allTangents
                allTangents.append((line, clippedLine))

                #adds to valid, works bc alg proceeds clockwise, and extTangent[1] is always on the left
                if ithTangents.index(line) == 1:
                    validTangents.append((line, clippedLine))

    print('Finished Tangents')
    return validTangents, allTangents, [(minx, miny),(maxx,maxy)]





#Tangent functions
def isOverlap(c1: Circle, c2: Circle): #checks to see if two circles overlap
    radSum = c1.radius + c2.radius
    centerDist = c1.center.distance(c2.center)
    return centerDist + .00001 < radSum #floating point error???

def isTangentPossible(c1, c2, R):
    #checks to see if a circle with radius R can even be tangent to c1 and c2
    maxDistance = 2*R + c1.radius + c2.radius
    centerDist = c1.center.distance(c2.center)
    if centerDist > maxDistance:
        return False
    else:
        return True

def tangentPoints(circ1: Circle, circ2: Circle, newRad: float):
    #finds the two possible centers
    #needs circ1 at origin and circ2 on y axis
    #returns list of Points
    A=circ1.radius
    B=circ2.radius
    D=circ1.center.distance(circ2.center)
    k=newRad
    y = ((A+k)**2 + (D)**2 - (B+k)**2)/(2*(D))
    x1 = fsqroot((A + k)**2 - y**2)
    x2 = -1*x1
    return [Point(x1,y), Point(x2,y)]

def tangentPlacements(c1: Circle, c2: Circle, R: float): #finds the two possible center points
    if isTangentPossible(c1,c2,R) == False:
        return None
    else:
        #Translate
        trC1 = Circle(Point(0,0), c1.radius)
        trC2 = Circle(
            sh.affinity.translate(c2.center, -1*c1.center.x, -1*c1.center.y),
            c2.radius
            )

        #Rotate around origin until c2 on y axis
        if trC2.center.x == 0 and trC2.center.y > 0:
            angle = 0
        elif trC2.center.x == 0 and trC2.center.y < 0:
            angle=180
        elif trC2.center.x < 0:
            angle = math.degrees(math.atan2(trC2.center.x, trC2.center.y))
        elif trC2.center.x > 0:
            angle = 90 - math.degrees(math.atan2(trC2.center.y, trC2.center.x))

        rotC1 = trC1 #circle 1 doesn't change under rotation
        rotC2 = Circle(
            sh.affinity.rotate(trC2.center, angle, (0,0)),
            c2.radius
            )

        #Apply tangentPoints
        possibleCenters = tangentPoints(rotC1, rotC2, R) #The two possible centers

        #Inverse rotate results
        invRot=[] #the two centers are reverse rotated
        for p in possibleCenters:
            invRot.append(
                sh.affinity.rotate(p, -1*angle, (0,0))
                )

        #Inverse translate results
        invTrans=[] #the two centers are then reverse translated, giving the final result
        for p in invRot:
            invTrans.append(
                sh.affinity.translate(p, c1.center.x, c1.center.y)
                )

        return invTrans #list of Points

#Main Logic
#Part 1

#Part 2
def radSumClusterAlg(radii):

    radii.sort() #sorts the list of radii again just in case
    radii.reverse()

    maxc=[] #max cluster diagram, basically a list of circles
    runningSum = 0 #sum of pairwise distances between centers, updated every iteration
    runningSubsets = [] #set of two element subsets of maxC, updated every iteration

    for index, rk in enumerate(radii):
        possiblePlacements=[]

        if index == 0: #adds the first circle at the origin
            maxc.append(
                Circle(Point(0,0), rk)
                )
            continue

        elif index == 1: #rigs the code so the second circle is added on y axis, and skips to updating the running vars
            possiblePlacements.append(
                (Point(0, radii[0] + rk), radii[0] + rk)
                )

        else:
            for sub in runningSubsets: #runs tangentPlacements on every pair of circles in maxc
                centerPair = tangentPlacements(sub[0], sub[1], rk) #finds the pair of possible centers for a given subset

                if centerPair == None:
                    runningSubsets.remove(sub) #removes subset for computing time, works because radii only get smaller every iteration
                    continue

                for place in centerPair: #does the following for both possible placements
                    isValid = True #default value
                    placeCirc = Circle(place, rk) #defines a test circle for isOverlap()

                    for circ in maxc: #checks validity of placement
                        if isOverlap(placeCirc, circ) == True:
                            isValid = False
                            break

                    if isValid == True: #only allows a placement to be added to possiblePlacements if it's valid
                        pcdSum = runningSum
                        for circ in maxc: #creates the pairwise center distance sum for a given placement
                            pcdSum += place.distance(circ.center)

                        possiblePlacements.append(
                            (place, pcdSum) #adds the placement along with its associated pcdSum to the list of possible placements
                            )

        sortedPossibles = sorted(possiblePlacements, key=lambda x: x[1]) #sorts possiblePlacements by pcdSum, smallest first

        minp = sortedPossibles[0] #chooses the placement with the smallest pcdSum

        newCirc = Circle(minp[0], rk) #defines new circle with center minp and radius rk

        runningSum += minp[1] #updates the running pairwise distance sum by stealing the pcdSum from minp. Equiv to iterating over maxc again

        for circ in maxc: #adds all the new subsets associated with newCirc
            runningSubsets.append(
                [circ, newCirc]
                )

        maxc.append(newCirc) #adds newCirc to the max cluster diagram

    print('Finished Packing')
    return maxc

def randomClusterAlg(radii):

    random.shuffle(radii)

    maxc=[] #max cluster diagram, basically a list of circles
    runningSum = 0 #sum of pairwise distances between centers, updated every iteration
    runningSubsets = [] #set of two element subsets of maxC, updated every iteration

    for index, rk in enumerate(radii):
        possiblePlacements=[]

        if index == 0: #adds the first circle at the origin
            maxc.append(
                Circle(Point(0,0), rk)
                )
            continue

        elif index == 1: #rigs the code so the second circle is added on y axis, and skips to updating the running vars
            possiblePlacements.append(
                (Point(0, radii[0] + rk), radii[0] + rk)
                )

        else:
            for sub in runningSubsets: #runs tangentPlacements on every pair of circles in maxc
                centerPair = tangentPlacements(sub[0], sub[1], rk) #finds the pair of possible centers for a given subset

                if centerPair == None:
                    runningSubsets.remove(sub) #removes subset for computing time, works because radii only get smaller every iteration
                    continue

                for place in centerPair: #does the following for both possible placements
                    isValid = True #default value
                    placeCirc = Circle(place, rk) #defines a test circle for isOverlap()

                    for circ in maxc: #checks validity of placement
                        if isOverlap(placeCirc, circ) == True:
                            isValid = False
                            break

                    if isValid == True: #only allows a placement to be added to possiblePlacements if it's valid
                        pcdSum = runningSum
                        for circ in maxc: #creates the pairwise center distance sum for a given placement
                            pcdSum += place.distance(circ.center)

                        possiblePlacements.append(
                            (place, pcdSum) #adds the placement along with its associated pcdSum to the list of possible placements
                            )

        minp = random.choice(possiblePlacements) #chooses the placement with the smallest pcdSum

        newCirc = Circle(minp[0], rk) #defines new circle with center minp and radius rk

        runningSum += minp[1] #updates the running pairwise distance sum by stealing the pcdSum from minp. Equiv to iterating over maxc again

        for circ in maxc: #adds all the new subsets associated with newCirc
            runningSubsets.append(
                [circ, newCirc]
                )

        maxc.append(newCirc) #adds newCirc to the max cluster diagram

    print('Finished Packing')
    return maxc

main()
