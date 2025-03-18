import math
import shapely as sh

class Circle:
    def __init__(self, center: sh.Point, radius: float):
        self.center=center
        self.radius=float(radius)
    def tupCenter(self): #for drawing at the end
        return (self.center.x, self.center.y)

def isOverlap(c1: Circle, c2: Circle): #checks to see if two circles overlap
    radSum = c1.radius + c2.radius
    centerDist = c1.center.distance(c2.center)
    return centerDist < radSum

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
    x1 = math.sqrt((A + k)**2 - y**2)
    x2 = -1*x1
    return [sh.Point(x1,y), sh.Point(x2,y)]

'''
tangentPlacements plan
    takes two circles and a radius, produces the two possible points or None
    check to see if tangent is possible
        if not, return None
        if yes continue
    Transform (take two circles and put at the origin and y axis)
        Translate
        Rotate around origin
            find angle between c2.center and x axis
            rotate counterclockwise by (90-angle) degrees
    Apply tangentPoints
    Apply inverse transforms to result of tangentPoints
        reverse rotate
        reverse translate
    Format result

'''

def tangentPlacements(c1: Circle, c2: Circle, R):
    if isTangentPossible(c1,c2,R) == False:
        return None
    else:
        #Translate
        trC1 = Circle(sh.Point(0,0), c1.radius)
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

        print(angle)
        rotC1 = trC1
        rotC2 = Circle(
            sh.affinity.rotate(trC2.center, angle, (0,0)),
            c2.radius
            )

        #Apply tangentPoints
        results = tangentPoints(rotC1, rotC2, R) #The two possible centers
        resCirc = Circle(results[0],R)

        #Inverse rotate results
        invRotRes=[] #the two centers unrotated
        for p in results:
            invRotRes.append(
                sh.affinity.rotate(p, -1*angle, (0,0))
                )

        invRotResCirc1 = Circle(invRotRes[0], R)
        invRotResCirc2 = Circle(invRotRes[1], R)

        #Inverse translate results
        invTransRes=[] #the two centers unrotated and then untranslated
        for p in invRotRes:
            invTransRes.append(
                sh.affinity.translate(p, c1.center.x, c1.center.y)
                )

        invTransResCirc1 = Circle(invTransRes[0],R)
        invTransResCirc2 = Circle(invTransRes[1],R)

    return invTransRes,[rotC1,rotC2], [rotC1,rotC2,resCirc], [trC1,trC2,invRotResCirc1, invRotResCirc2], [c1,c2,invTransResCirc1,invTransResCirc2]


test1 = Circle(sh.Point(4,9), 4)
test2 = Circle(sh.Point(-1,5), 2)

rad=float(input('Enter radius '))
results = tangentPlacements(test1,test2,rad)[0]
list = tangentPlacements(test1,test2,rad)[4]

#Everything else
def drawSteps(N): #draws first N steps
    # Create a figure and axis
    fig, ax = plt.subplots()

    for k in range(N):
        circ=plt.Circle(maxC[k].tupCenter(), maxC[k].radius, fill=False)
        ax.add_patch(circ)

    ax.grid(True, which='both')
    ax.axhline(y=0, color='k')
    ax.axvline(x=0, color='k')

    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)
    plt.axis('equal')  # To ensure the aspect ratio is maintained
    plt.show()

def drawC(diagram): #draws complete diagram
    import matplotlib.pyplot as plt
    # Create a figure and axis
    fig, ax = plt.subplots()

    for k in range(len(diagram)):
        circ=plt.Circle(diagram[k].tupCenter(), diagram[k].radius, fill=False)
        ax.add_patch(circ)

    plt.plot(diagram[0].center.x,diagram[0].center.y,'ro')
    plt.plot(diagram[1].center.x,diagram[1].center.y,'ro')
    plt.plot(results[0].x,results[0].y, 'bo')
    plt.plot(results[1].x, results[1].y, 'bo')

    ax.grid(True, which='both')
    ax.axhline(y=0, color='k')
    ax.axvline(x=0, color='k')

    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)
    plt.axis('equal')  # To ensure the aspect ratio is maintained
    plt.show()

drawC(list)
'''
#show x,y axes in plot
ax.axhline(y=0, color='k')
ax.axvline(x=0, color='k')

#show grid
ax.grid(True, which='both')
'''
