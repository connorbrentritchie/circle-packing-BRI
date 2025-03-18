#key: $$$ to do, ??? figure out if really needed

#Overall Plan
'''
given data:
    list of radii of circles

answer option 1: area of minimum convex polygon that contains all circles
answer option 2: area of convex polygon defined by centers of circles

TENTATIVE ALGORITHM

get circle data

sort from biggest radius to smallest

iteratively make optimal diagram with findAllPlacements

create 'polygon' diagram subset with makeCenterPoly or makeOuterPoly
    Two options here, could make the center polygon (easier) or outer polygon (more accurate??)

calculate area with polyArea, and return that value
'''


#Functions needed
'''
Scraping functions:
    since the data comes from excel spreadsheets, will need functions for that. Don't know if I need to write any myself

Basic functions
    function distance((Point,Point) --> float): find distance between two Points
       handled by shapely .distance

Diagram functions
    function sumRadii(Diagram --> float): given diagram, compute sum of distances between each pair of radii
        total=0
        for i!=j in diagram:
            total+=distance(i,j)
        return total

    ???function addCircle (diagram, Point --> Diagram): adds new circle (Point) to diagram
        probably something like diagram.append(newPoint)
        seems very short, might be able to integrate this into a different function

    function addBestPlacement(list(Circle), Diagram --> Diagram): takes the results of findAllPlacements and adds the best one to the diagram

    function findAllPlacements(Diagram, radius(float) --> list of Circles):given a Diagram D and a radius R, find all Points P such that the Circle (P,R) is tangent to at least two Circles in D.
        This is going to be the hardest part.

        Overview:
            make a list of all possible placements with tangentPlacements, somehow storing number of tangent points for each placement
            remove any invalid placements
            return a list of all remaining valid placements
                these should all be valid placements, and have the maximum possible number of tangent points.

    function tangentPlacements(Circle1, Circle2, radius --> list of Circles): given two (tangent circles) C1, C2 and a radius R, return a list of Circles with radius R that would be tangent to C1 and C2.
        maybe to make math easier, transform so Circles are on y-axis.
        looks like shapely has transforms in it.

        Transform:
            translate bigger circle to (0,0)
            rotate around (0,0) so other circle is above the first one

        Compute:
            hyperbola something or other
            get (x1,y1),(x2,y2)

        Inverse transform:

Polygon functions
    function polyArea(Diagram --> float): computes area of a polygon.
        use shapely library
        needs the points to come in clockwise order on the plane

    function makeCenterPoly(Diagram --> List(Points)): given a diagram, chooses all of the outermost circle centers.
        really don't know how to implement this one yet.

    ???function makeOuterPoly(Diagram --> List(Points)): given a diagram, returns the vertices of the outer polygon.
        probably needs the logic from makeCenterPoly, plus a bunch of difficult math on top of that. Hopefully I don't need to make this one.

Misc functions
    isOverlapping(Circle1, Circle2 --> Bool): checks to see if two circles would overlap.
        work out math later

    ???IsValidPlacement(Diagram, Circle --> Bool): Checks to see whether a particular circle placement is valid based on criteria.
        isOverlapping
        maybe other stuff

'''


#Objects
#want to practice with OOP stuff before fully deciding
'''
Point: probably a tuple of floats, maybe could also contain radius data
    looks like can use shapely Point object

Diagram:
    Option 1: maybe dictionary with Points and Radius, hopefully can get outer convex polygon from that
    Option 2: just a list of Points. Easily allows computation of convex polygon defined by those Points.
    Option 3: if Circle ends up being an object, just a list of Circle objects.

???Circle: could be a Point with a radius value. Don't know if it's worth having separate Point and Circle objects, but could be useful
    center: Point
    radius: Float
    packaged as a dictionary? learn a little about Python OOP to see
'''


#Notes
'''
potential alternative to doing convex polygon of the actual circles:
    connect the centers of the circles and compute the area of that instead
    allows the diagram object to just be a list of points instead of having to figure out some way to represent the actual circles

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

