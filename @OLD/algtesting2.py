import math
import shapely as sh
from shapely import Point
import matplotlib.pyplot as plt
import openpyxl as pxl
import random

import sys


class Circle:
    def __init__(self, center: sh.Point, radius: float):
        self.center=center
        self.radius=float(radius)
    def tupCenter(self): #for drawing at the end
        return (self.center.x, self.center.y)

#drawing functions
def drawComplete(diagram, poly): #draws list of circles
    # Create a figure and axis
    fig, ax = plt.subplots()
    fig.set_figwidth(25)
    fig.set_figheight(13)

    for k in range(len(diagram)): #
        circ=plt.Circle(diagram[k].tupCenter(), diagram[k].radius, fill=False)
        ax.add_patch(circ)

        dx=diagram[k].center.x
        dy=diagram[k].center.y

        plt.plot(dx, dy, 'bo')

        label=str(k+1)
        plt.annotate(label,
                    (dx, dy),
                    textcoords = "offset points",
                    xytext=(7,7),
                    ha='center')

    ax.grid(True, which='both')
    ax.axhline(y=0, color='k')
    ax.axvline(x=0, color='k')

    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)
    plt.axis('equal')  # To ensure the aspect ratio is maintained
    plt.show(block=True)

def drawCtesting(diagram, points, valids=[], subsets=[]): #draws list of circles, their centers, plus a list of points
    # Create a figure and axis
    fig, ax = plt.subplots()
    fig.set_figwidth(15)
    fig.set_figheight(10)

    for k in range(len(diagram)):
        circ=plt.Circle(diagram[k].tupCenter(), diagram[k].radius, fill=False)
        ax.add_patch(circ)

        dx=diagram[k].center.x
        dy=diagram[k].center.y

        plt.plot(dx, dy, 'bo')

        label=str(k+1)
        plt.annotate(label,
                    (dx, dy),
                    textcoords = "offset points",
                    xytext=(7,7),
                    ha='center')

    if subsets != []:
        for ps in subsets:
            subLabel = ps[1]
            p = ps[0]
            if p in valids:
                plt.plot(p.x,p.y,'go')
                plt.annotate(
                    str(subLabel),
                    (p.x,p.y),
                    textcoords = "offset points",
                    xytext=(7,7)
                    )
            else:
                plt.plot(p.x,p.y,'ro')

    else:
        for p in points:
            if p in valids:
                plt.plot(p.x,p.y,'go')
            else:
                plt.plot(p.x,p.y,'ro')


    ax.grid(True, which='both')
    ax.axhline(y=0, color='k')
    ax.axvline(x=0, color='k')

    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)
    plt.axis('equal')  # To ensure the aspect ratio is maintained
    plt.show(block=True)


#tangentPlacement functions
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

    try:
        x1 = math.sqrt((A + k)**2 - y**2)
    except:
        x1=0 #floating point error with square root, sometimes tries root of very small (e-13) number

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

#Excel functions
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

    radii.sort()
    radii.reverse()
    finalCell=column + str(index)
    return radii, finalCell

#Main Logic
#Part 1

answer=getRadii()
radii=answer[0]
resultCell=answer[1]

#radii=[9,8,6,4]

#Part 2
print(radii)
def maxClusterAlg(radii):
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

    return maxc


def maxClusterAlgTesting(radii, doPause: bool, doStats: bool):
    maxc=[] #max cluster diagram, basically a list of circles
    runningSum = 0 #sum of pairwise distances between centers, updated every iteration
    runningSubsets = [] #set of two element subsets of maxC, updated every iteration

    subsetCount=0
    pcdSumCount=0

    points=[]

    if doPause == True:
        stopIndex = int(input('Stop at '))
    else:
        stopIndex = len(radii) + 10

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
            testingWithSubsets=[] #every placement for a given rk, valid or not
            testing = [x[0] for x in testingWithSubsets]
            testingSubsets = [x[1] for x in testingWithSubsets]
            allSubsetIndexes=[]

            for sub in runningSubsets: #runs tangentPlacements on every pair of circles in maxc
                subsetCount+=1
                centerPair = tangentPlacements(sub[0], sub[1], rk) #finds the pair of possible centers for a given subset

                if index == stopIndex:
                    allSubsetIndexes.append(
                        [maxc.index(sub[0])+1, maxc.index(sub[1])+1]
                        )

                if centerPair == None:
                    runningSubsets.remove(sub) #removes subset for computing time, works because radii only get smaller every iteration
                    #print('got em', index, rk, sub[0].center, sub[1].center)

                    print('\nNONE CENTERPAIR:', index, end='. ')
                    print('first circle:', maxc.index(sub[0])+1, end='. ')
                    print('second circle:', maxc.index(sub[1])+1)

                    continue

                for place in centerPair: #does the following for both possible placements

                    testingWithSubsets.append(
                        [place,[maxc.index(sub[0])+1, maxc.index(sub[1])+1]]
                        )

                    if index == stopIndex:
                        print('\nindex:', index, end='. ')
                        print('first circle:', maxc.index(sub[0])+1, end='. ')
                        print('second circle:', maxc.index(sub[1])+1)

                    isValid = True #default value
                    placeCirc = Circle(place, rk) #defines a test circle for isOverlap()
                    for circ in maxc: #checks validity of placement
                        if isOverlap(placeCirc, circ) == True:
                            isValid = False
                            break

                    if isValid == True: #only allows a placement to be added to possiblePlacements if it's valid
                        pcdSum = runningSum
                        for circ in maxc: #creates the pairwise center distance sum for a given placement
                            pcdSumCount+=1
                            pcdSum += place.distance(circ.center)

                        possiblePlacements.append(
                            (place, pcdSum) #adds the placement along with its associated pcdSum to the list of possible placements
                            )

            if index == stopIndex:
                print('subset indexes:', allSubsetIndexes)

                valids=[p[0] for p in possiblePlacements]

                print('\ntesting with subsets:', testingWithSubsets)
                drawCtesting(maxc, testing, valids, testingWithSubsets)



        print('pPlace length', index, rk, len(possiblePlacements))
        sortedPossibles = sorted(possiblePlacements, key=lambda x: x[1]) #sorts possiblePlacements by pcdSum, smallest first
        try:
            minp = sortedPossibles[0] #chooses the placement with the smallest pcdSum
        except:
            print('E R R O R', index, rk, possiblePlacements)
            sys.exit(1)

        newCirc = Circle(minp[0], rk) #defines new circle with center minp and radius rk

        runningSum += minp[1] #updates the running pairwise distance sum by stealing the pcdSum from minp. Equiv to iterating over maxc again

        for circ in maxc: #adds all the new subsets associated with newCirc
            runningSubsets.append(
                [circ, newCirc]
                )

        maxc.append(newCirc) #adds newCirc to the max cluster diagram
        #drawC(maxc)

    if doStats == True:
        print('total possible subsets ', math.comb(len(radii),2))
        print('runningSubsets length ', len(runningSubsets))

        print('subsetCount', subsetCount)
        print('pcdSumCount', pcdSumCount)

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
            if possiblePlacements==[]:
                print('empty possibles')
                drawC(maxc)

        sortedPossibles = sorted(possiblePlacements, key=lambda x: x[1]) #sorts possiblePlacements by pcdSum, smallest first

        minp = random.choice(sortedPossibles) #chooses the placement with the smallest pcdSum

        newCirc = Circle(minp[0], rk) #defines new circle with center minp and radius rk

        runningSum += minp[1] #updates the running pairwise distance sum by stealing the pcdSum from minp. Equiv to iterating over maxc again

        for circ in maxc: #adds all the new subsets associated with newCirc
            runningSubsets.append(
                [circ, newCirc]
                )

        maxc.append(newCirc) #adds newCirc to the max cluster diagram

    return maxc

#Part 3
def drawComplete(diagram, poly, label):
    # Create a figure and axis
    fig, ax = plt.subplots()
    fig.set_figwidth(25)
    fig.set_figheight(13)
    fig.suptitle(label)

    #circles
    for k in range(len(diagram)):
        circ=plt.Circle(diagram[k].tupCenter(), diagram[k].radius, fill=False)
        ax.add_patch(circ)

        dx=diagram[k].center.x
        dy=diagram[k].center.y

        plt.plot(dx, dy, 'bo')

        label=str(k+1)
        plt.annotate(label,
                    (dx, dy),
                    textcoords = "offset points",
                    xytext=(7,7),
                    ha='center')

    #polygon
    vertices = list(poly.exterior.coords) #list of tuples
    for k in range(len(vertices)):
        if k == 0:
            plt.plot(vertices[k][0],vertices[k][1],'bo')
        else:
            xs=[vertices[k-1][0], vertices[k][0]]
            ys=[vertices[k-1][1], vertices[k][1]]
            plt.plot(xs, ys, 'bo-')

    ax.grid(True, which='both')
    ax.axhline(y=0, color='k')
    ax.axvline(x=0, color='k')

    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)
    plt.axis('equal')  # To ensure the aspect ratio is maintained
    plt.show(block=False)


def takeCenters(circles): #takes a list of circles and returns the list of centers as a MultiPoint
    return sh.MultiPoint([c.tupCenter() for c in circles])


#drawComplete(randCluster, randCenterConvHull)

def minTesting(N):
    maxC = maxClusterAlg(radii)
    maxConvHull = takeCenters(maxC).convex_hull
    minArea = maxConvHull.area
    print('minimum area:', minArea)

    counterFound=False
    counterCircles=None
    counterPoly=None
    counterArea=None

    randDiagrams=[]
    for i in range(N):
        randC=randomClusterAlg(radii)
        randConvHull=takeCenters(randC).convex_hull
        randArea=randConvHull.area

        randDiagrams.append([randArea, randC, randConvHull])
        print('random area:', i+1, randArea)

        if randArea < minArea:
            counterFound=True
            counterCircles=randC
            counterPoly=randConvHull
            counterArea=randArea

            break

    if counterFound == True:
        counterAreaPercent = counterArea/minArea

        print('\nCounterexample found:', minArea, counterArea)
        print('counterArea over minArea percent:',counterArea/minArea*100)
        drawComplete(maxC, maxConvHull, 'Max Cluster')
        drawComplete(counterCircles, counterPoly, 'Counterexample')

        return counterAreaPercent

    else:
        sortedRandDiagrams=sorted(randDiagrams, key=lambda x: x[0])
        print('No counterexample found')
        print('Smallest randArea:', sortedRandDiagrams[0][0])

        drawComplete(maxC, maxConvHull, 'Max Cluster')
        drawComplete(sortedRandDiagrams[0][1], sortedRandDiagrams[0][2], 'Smallest Random Cluster')

        return None

def minTestingNoDraw(N):
    maxC = maxClusterAlg(radii)
    maxConvHull = takeCenters(maxC).convex_hull
    minArea = maxConvHull.area
    print('minimum area:', minArea)

    counterFound=False
    counterCircles=None
    counterPoly=None
    counterArea=None

    randDiagrams=[]
    for i in range(N):
        randC=randomClusterAlg(radii)
        randConvHull=takeCenters(randC).convex_hull
        randArea=randConvHull.area

        randDiagrams.append([randArea, randC, randConvHull])

        if randArea < minArea:
            counterFound=True
            counterCircles=randC
            counterPoly=randConvHull
            counterArea=randArea

            break

    if counterFound == True:
        counterAreaPercent = counterArea/minArea

        print('\nCounterexample found:', minArea, counterArea)
        print('counterArea over minArea percent:',counterArea/minArea*100)

        return counterAreaPercent

    else:
        sortedRandDiagrams=sorted(randDiagrams, key=lambda x: x[0])
        print('No counterexample found')
        print('Smallest randArea:', sortedRandDiagrams[0][0])

        return None


def avgCounterPercent(iterations, minTestingIterations):
    percents = []
    for i in range(iterations):
        percents.append(
            minTestingNoDraw(minTestingIterations)
            )

    filteredPercents = list(filter(lambda a: a != None, percents))
    print(filteredPercents)

    return sum(filteredPercents)/len(filteredPercents)

#minTesting(int(input('Enter number of iterations for minTesting: ')))

print(avgCounterPercent(100,20))
