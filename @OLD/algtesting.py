import math
import shapely as sh
import matplotlib.pyplot as plt
import openpyxl as pxl


class Circle:
    def __init__(self, center: sh.Point, radius: float):
        self.center=center
        self.radius=float(radius)
    def tupCenter(self): #for drawing at the end
        return (self.center.x, self.center.y)

wb=pxl.load_workbook('Python testing.xlsx')
sheet=wb['Sheet1']

#Functions
def getRadiiTesting(): #for testing only
    column='A'
    index=1
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


def getRadii():
    column=str(input('Which column: '))
    index=int(input('Which start row: '))
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

def tangentPoints(circ1: Circle, circ2: Circle, newRad: float):
    #needs circ1 at origin and circ2 on y axis
    A=circ1.radius
    B=circ2.radius
    k=newRad
    y = ((A+k)**2 + (A+B)**2 - (B+k)**2)/(2*(A+B))
    x1 = math.sqrt((A + k)**2 - y**2)
    x2 = -1*x1
    print(y,x1,x2)
    return [sh.Point(x1,y), sh.Point(x2,y)]

#Main Logic

#Part 1
answer=getRadiiTesting()
radii=answer[0]
resultCell=answer[1]

radii.sort()
radii.reverse()
print(radii)

#Part 2
maxC=[] #cDiagram of maximum cluster
count=0
for Rk in radii:
    if count==0: #puts first and biggest circle at origin
        maxC.append(
            Circle(sh.Point(0,0), Rk)
            )
        count+=1
        print(count, Rk)
    elif count==1: #puts 2nd circle tangent to first on y axis
        maxC.append(
            Circle(sh.Point(0 , radii[0] + Rk), Rk)
            )
        count+=1
        print(count, Rk)
    else:
        pass


circle3=Circle(
    tangentPoints(maxC[0],maxC[1],radii[2])[1],
    radii[2]
)
maxC.append(circle3)

def drawC(diagram): #draws complete diagram
    #import matplotlib.pyplot as plt
    # Create a figure and axis
    fig, ax = plt.subplots()

    for k in range(len(diagram)):
        circ=plt.Circle(diagram[k].tupCenter(), diagram[k].radius, fill=False)
        ax.add_patch(circ)

    ax.grid(True, which='both')
    ax.axhline(y=0, color='k')
    ax.axvline(x=0, color='k')

    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)
    plt.axis('equal')  # To ensure the aspect ratio is maintained
    plt.show()
