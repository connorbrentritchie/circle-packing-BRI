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
    def tupCenter(self): #for drawing at the end
        return (self.center.x, self.center.y)

#Drawing
def drawC(diagram): #draws list of circles
    # Create a figure and axis
    fig, ax = plt.subplots()
    fig.set_figwidth(25)
    fig.set_figheight(13)

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
    try:
        x1 = math.sqrt((A + k)**2 - y**2)
    except:
        x1=0 #floating point error with square root, sometimes tries root of very small (e-13) number
        print('neg', (A + k)**2 - y**2, circ1.center, circ2.center)
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
answer=getRadii()
radii=answer[0]
resultCell=answer[1]

radii.sort()
radii.reverse()

#Part 2


#Part 5


