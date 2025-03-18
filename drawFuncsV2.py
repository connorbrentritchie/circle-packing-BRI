import matplotlib.pyplot as plt
from geoThings import Circle, InfLine, VertLine, fsqroot, randomList, printCircleData
from shapely import Point, Polygon, LineString

def main():
    setup(12,9)
    circ1 = Circle(Point(1,1),2)
    circ2 = Circle(Point(-2,2),3)
    drawCircles([circ1])
    pdraw(1)
    drawCircles([circ1,circ2])
    pdraw(2)

#Drawing
#New ones
def setup(width = 12, height = 9):
    fig, ax = plt.subplots()
    fig.set_figwidth(width)
    fig.set_figheight(height)

def pshow(isBlocking = True):
    ax = plt.gca()

    ax.grid(True, which='both')
    ax.axhline(y=0, color='k')
    ax.axvline(x=0, color='k')

    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)
    plt.axis('equal')  # To ensure the aspect ratio is maintained

    plt.show(block =  isBlocking)

def pdraw(time):
    fig, ax = plt.gcf(), plt.gca()

    ax.grid(True, which='both')
    ax.axhline(y=0, color='k')
    ax.axvline(x=0, color='k')

    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)
    plt.axis('equal')  # To ensure the aspect ratio is maintained

    plt.draw()
    plt.pause(time)
    plt.cla()
    plt.clf()

def drawPoints(pointList, pcolor = 'red', pmarker = 'o'): #list of Points
    xs = [p.x for p in pointList]
    ys = [p.y for p in pointList]
    plots = []
    for i in range(len(pointList)):
        plotPoint = plt.plot(xs[i],ys[i],color=pcolor,marker=pmarker)
        plots.append(plotPoint)
    return plots

def removePoints(pointList_p):
    for point_p in pointList_p:
        point_p[0].remove()

def drawCircles(circleList): #Circles
    fig = plt.gcf()
    ax = plt.gca()
    plots = []
    for index, circ in enumerate(circleList):
        #plots the circle
        plotCirc = plt.Circle(circ.tupCenter(), circ.radius, fill = False)
        ax.add_patch(plotCirc)

        #plots the center, labeled by index in circleList
        cx, cy = circ.tupCenter()
        plotCenter = plt.plot(cx,cy, color = 'b', marker = 'o')
        plotCenterAnn = plt.annotate(str(index+1),(cx,cy), textcoords = 'offset points', xytext = (7,7))

        plots.append([plotCirc,plotCenter,plotCenterAnn])

    return plots

def removeCircles(circleList_p): #usually an element of the thing returned by drawCircles
    for circle_p in circleList_p:
        circle_p[0].remove()
        circle_p[1][0].remove()
        circle_p[2].remove()


def drawLines(lineList): #InfLines or VertLines
    fig, ax = plt.gcf(), plt.gca()

    plots = []
    for line in lineList:
        if type(line) is VertLine:
            plotLine = plt.axvline(line.xInt)
        else:
            plotLine = plt.axline(
                (0,line.b),
                slope=line.m
                )
    return plots

def drawPolygon(polygon, polyColor = 'red'): #Polygon, string
    fig, ax = plt.gcf(), plt.gca()

    coords = list(polygon.exterior.coords) #for plotPoly
    coordPoints = [Point(p) for p in list(polygon.exterior.coords)] #for drawPoints

    plotVertices = drawPoints(coordPoints, polyColor, 'o')

    plotPoly = plt.Polygon(coords, color = polyColor, lw = 2, fill = False)
    ax.add_patch(plotPoly)

    return [plotPoly, plotVertices]

def drawSegments(segments):
    plots = []
    for seg in segments:
        x0 = list(seg.coords)[0][0]
        x1 = list(seg.coords)[1][0]
        y0 = list(seg.coords)[0][1]
        y1 = list(seg.coords)[1][1]
        seg_p = plt.plot([x0,x1],[y0,y1],color='C' + str(segments.index(seg)), marker='1')
        plots.append(seg_p)
    return plots


def drawBox(bounds):
    fig, ax = plt.gcf(), plt.gca()
    minx, miny, maxx, maxy = bounds

    rect = plt.Rectangle((minx,miny), maxx-minx, maxy-miny, fill = False)
    ax.add_patch(rect)

if __name__ == '__main__':
    main()
