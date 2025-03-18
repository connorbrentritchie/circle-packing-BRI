
#Overview
'''
code that retrieves the data and formats it as a list

code that produces max clustering

code that produces polygon from given set of circles with centers

code that calculates area of a polygon
'''

#Functions needed
'''
Scraping functions:
    since the data comes from excel spreadsheets, will need functions for that. Don't know if I need to write any myself

Basic functions
    function distance((Point,Point) --> float): find distance between two Points

Diagram functions
    function sumRadii(Diagram --> float):
        given diagram, compute sum of distances between each pair of radii

    ???function addCircle (diagram, Point --> Diagram):
        adds new circle (Point) to diagram

    function addBestPlacement(list(Circle), Diagram --> Diagram):
        takes the results of findAllPlacements and adds the best one to the diagram

    function findAllPlacements(Diagram, radius(float) --> list of Circles):
        given a Diagram D and a radius R, find all Points P such that the Circle (P,R) is tangent to at least two Circles in D.

    function tangentPlacements(Circle1, Circle2, radius --> list of Circles):
        given two (tangent circles) C1, C2 and a radius R, return a list of Circles with radius R that would be tangent to C1 and C2.

Polygon functions
    SOLVED function polyArea(Diagram --> float):
        computes area of a polygon.

    function makeCenterPoly(Diagram --> List(Points)):
        given a diagram, chooses all of the outermost circle centers.

    ???function makeOuterPoly(Diagram --> List(Points)):
        given a diagram, returns the vertices of the outer polygon.

Misc functions
    isOverlapping(Circle1, Circle2 --> Bool):
        checks to see if two circles would overlap.

    ???IsValidPlacement(Diagram, Circle --> Bool):
        Checks to see whether a particular circle placement is valid based on criteria.
'''


#Objects
#want to practice with OOP stuff before fully deciding
'''
Point: probably a tuple of floats, maybe could also contain radius data
    looks like can use shapely Point object

cDiagram: List of Circles

pDiagram: List of Points
    might not need separate object
    maybe can use Polygon from shapely

Circle: Point bundled with radius value.
'''


#Notes
'''
potential alternative to doing convex polygon of the actual circles:
    connect the centers of the circles and compute the area of that instead


also want to have something that takes the final circle Diagram and makes a picture. maybe desmos can do this?
'''

#Math things to consider/prove
'''
Definitions:
    D: diagram of circles
    P: circumscribed polygon defined by D
    Q: polygon defined by the centers of each circle in D

(Ques1) Given a a diagram D, when is P~Q?
    Almost never. Probably only when all circles are the same exact size.

(Ques2) If the area of Q is minimal for a given D, does that imply that the area of P is minimal for D as well?
    Man I don't know how tf to even start with this one.
'''


#unrelated math problems i just thought of
'''
Given a (convex) polygon and a minimum circle radius, how much of the polygon can be covered by circles of that radius or higher?

When does a convex polygon have a circumcircle and an incircle? (my guess is just regular ones do)
'''

