from shapely import Point
import shapely as sh
import math
import random
import matplotlib.pyplot as plt

from convPolyFuncs import convPoly
from geoThings import Circle, InfLine, VertLine, fsqroot, randomList, printCircleData
from drawFuncsV2 import setup, pshow, pdraw, drawCircles, drawPoints, drawLines, drawSegments, drawPolygon, removeCircles, removePoints

'''
this file has all the maximum packing algorithms.
The main two are radSumAlg and polyAreaAlg.
    polyAreaAlg is the true greedy algorithm and is ridiculously slow for anything over about 15 circles.
    radSumAlg minimizes the pairwise sum of distances between circle centers, which is much faster than and just about as accurate as polyAreaAlg for over 15 circles.
'''



def main():
    #50 1850 2950
    radii = [50,1850,2950]
    testc = radSumAlg(radii)
    testd = convPoly(testc)


    setup()
    drawCircles(testc)
    drawPolygon(testd)
    pshow()

def isOverlap(c1: Circle, c2: Circle): #checks to see if two circles overlap
    radSum = c1.radius + c2.radius
    centerDist = c1.center.distance(c2.center)
    return centerDist + .000001 < radSum #floating point error???

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
        else:
            raise NameError("Impossible angle detected")

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


def polyAreaAlg(radii):

    radii.sort() #sorts the list of radii again just in case
    radii.reverse()

    maxc=[] #max cluster diagram, basically a list of circles
    runningSubsets = [] #set of two element subsets of maxC, updated every iteration

    for index, rk in enumerate(radii):
        possiblePlacements=[]

        if index == 0: #adds the first circle at the origin
            maxc.append(
                Circle(Point(0,0), rk)
                )
            continue

        elif index == 1: #rigs the code so the second circle is added tangent to the first circle, and skips to updating the running vars
            if radii[0] == rk: #designed to avoid vertical lines
                x = radii[0]/2
            else:
                x = (radii[0]-rk)/2
            R = radii[0] + rk
            y = fsqroot(R**2-x**2)
            possiblePlacements.append(
                (Point(x,y), R)
                )

        else:
            count = 1
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
                        testConfig = maxc + [placeCirc]
                        testConvPoly = convPoly(testConfig)

                        count+=1

                        possiblePlacements.append(
                            (place, testConvPoly.area) #adds the placement along with its associated pcdSum to the list of possible placements
                            )

        sortedPossibles = sorted(possiblePlacements, key=lambda x: x[1]) #sorts possiblePlacements by polygon area

        minp = sortedPossibles[0] #chooses the placement with the smallest pcdSum

        newCirc = Circle(minp[0], rk) #defines new circle with center minp and radius rk

        for circ in maxc: #adds all the new subsets associated with newCirc
            runningSubsets.append(
                [circ, newCirc]
                )

        maxc.append(newCirc) #adds newCirc to the max cluster diagram
    return maxc




def radSumAlg(radii):

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

        elif index == 1: #rigs the code so the second circle is added tangent to the first circle, and skips to updating the running vars
            if radii[0] == rk: #designed to avoid vertical lines
                x = radii[0]/2
            else:
                x = (radii[0]-rk)/2
            R = radii[0] + rk
            y = fsqroot(R**2-x**2)
            possiblePlacements.append(
                (Point(x,y), R)
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



def randomAlg(radii):

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

        elif index == 1: #rigs the code so the second circle is added tangent to first one, and skips to updating the running vars
            if radii[0] == rk:
                x = radii[0]
            else:
                x = (radii[0]-rk)/2
            R = radii[0] + rk
            y = fsqroot(R**2-x**2)
            possiblePlacements.append(
                (Point(x,y), R)
                )

        else:
            for sub in runningSubsets: #runs tangentPlacements on every pair of circles in maxc
                centerPair = tangentPlacements(sub[0], sub[1], rk) #finds the pair of possible centers for a given subset

                if centerPair == None:
                    #runningSubsets.remove(sub) #removes subset for computing time, works because radii only get smaller every iteration
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

    return maxc





#NOT DONE YET
def radSumAlgPresentation(radii, speed): #draws each step of the alg

    radii.sort() #sorts the list of radii again just in case
    radii.reverse()

    maxc=[] #max cluster diagram, basically a list of circles
    runningSum = 0 #sum of pairwise distances between centers, updated every iteration
    runningSubsets = [] #set of two element subsets of maxC, updated every iteration

    for index, rk in enumerate(radii):
        fig = plt.gcf()
        plt.suptitle('Cycle '+str(index+1))

        possiblePlacements=[]

        if index == 0: #adds the first circle at the origin
            maxc.append(
                Circle(Point(0,0), rk)
                )
            drawCircles(maxc)
            pdraw(speed+3)
            continue

        elif index == 1: #rigs the code so the second circle is added on y axis, and skips to updating the running vars
            possiblePlacements.append(
                (Point(0, radii[0] + rk), radii[0] + rk)
                )

        else:
            allPlacements = []
            validPlacements = []
            for sub in runningSubsets: #runs tangentPlacements on every pair of circles in maxc

                centerPair = tangentPlacements(sub[0], sub[1], rk) #finds the pair of possible centers for a given subset
                if centerPair == None:
                    runningSubsets.remove(sub) #removes subset for computing time, works because radii only get smaller every iteration
                    continue

                for place in centerPair: #does the following for both possible placements
                    isValid = True #default value
                    placeCirc = Circle(place, rk) #defines a test circle for isOverlap()
                    allPlacements.append(place)

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
                        validPlacements.append(place)

                fig =plt.gcf()
                plt.title('Subset: ' + str([maxc.index(sub[0])+1,maxc.index(sub[1])+1]))
                allPlacements_p = drawPoints([Point(p) for p in allPlacements], 'red','o')
                maxc_p = drawCircles(maxc)
                pdraw(speed/1.5)
                removePoints(allPlacements_p)
                removeCircles(maxc_p)

            allPlacements_p = drawPoints([Point(p) for p in allPlacements], 'red','o')
            maxc_p = drawCircles(maxc)
            pdraw(speed)
            removePoints(allPlacements_p)
            removeCircles(maxc_p)


            validPlacements_p = drawPoints([Point(p) for p in validPlacements],'y','o')
            maxc_p = drawCircles(maxc)
            pdraw(speed)
            removePoints(validPlacements_p)
            removeCircles(maxc_p)

        sortedPossibles = sorted(possiblePlacements, key=lambda x: x[1]) #sorts possiblePlacements by pcdSum, smallest first

        minp = sortedPossibles[0] #chooses the placement with the smallest pcdSum
        minp_p = drawPoints([minp[0]], 'green','o')
        maxc_p = drawCircles(maxc)
        pdraw(speed)
        removePoints(minp_p)
        removeCircles(maxc_p)

        newCirc = Circle(minp[0], rk) #defines new circle with center minp and radius rk

        runningSum += minp[1] #updates the running pairwise distance sum by stealing the pcdSum from minp. Equiv to iterating over maxc again

        for circ in maxc: #adds all the new subsets associated with newCirc
            runningSubsets.append(
                [circ, newCirc]
                )

        maxc.append(newCirc) #adds newCirc to the max cluster diagram
        maxc_p = drawCircles(maxc)
        pdraw(speed)
        removeCircles(maxc_p)

    return maxc


if __name__ == '__main__':
    main()
