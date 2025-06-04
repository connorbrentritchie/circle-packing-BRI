library(sf)         # for spatial geometry operations equivalent to shapely
library(methods)    # for S3 class methods

#------------------------------#
# Dependencies from geoThings  #
#------------------------------#

# fsqroot function: returns square root of its argument
fsqroot <- function(x) {
  sqrt(x)
}

# Circle class constructor
Circle <- function(center, radius) {
  obj <- list(center = center, radius = radius)
  obj$tupCenter <- function() {
    c(center$x, center$y)
  }
  class(obj) <- "Circle"
  return(obj)
}

# getArea method for Circle, returns area of circle
getArea.Circle <- function(circ) {
  pi * circ$radius^2
}

# InfLine class constructor: represents an infinite line in slope-intercept form
InfLine <- function(m, b) {
  obj <- list(m = m, b = b)
  class(obj) <- "InfLine"
  return(obj)
}

# VertLine class constructor: represents a vertical line at x = xInt
VertLine <- function(xInt) {
  obj <- list(xInt = xInt)
  class(obj) <- "VertLine"
  return(obj)
}

#------------------------------#
# Dependencies from drawFuncsV2
#------------------------------#

# Setup drawing area (stub implementation using base R plotting)
setup <- function(width, height) {
  plot.new()
  plot.window(xlim = c(0, width), ylim = c(0, height))
}

# Show plot (stub implementation)
pshow <- function() {
  # In base R, the plot is updated automatically.
  invisible(NULL)
}

# pdraw stub (no operation)
pdraw <- function() {}

# Draw circles using base R graphics
drawCircles <- function(circleList) {
  for (circ in circleList) {
    symbols(circ$center$x, circ$center$y, circles = circ$radius, add = TRUE, inches = FALSE)
  }
}

# Draw points (expects list of numeric vectors of length 2)
drawPoints <- function(points) {
  for (p in points) {
    points(p[1], p[2])
  }
}

# Draw lines (InfLine and VertLine)
drawLines <- function(lines) {
  for (ln in lines) {
    if (inherits(ln, "VertLine")) {
      abline(v = ln$xInt)
    } else if (inherits(ln, "InfLine")) {
      abline(a = ln$b, b = ln$m)
    }
  }
}

# Draw segments: expects a list of sf LineString objects (as matrices of coordinates)
drawSegments <- function(segments) {
  for (seg in segments) {
    # Extract coordinates from the LineString (matrix)
    coords <- seg
    lines(coords, col = "blue")
  }
}

# Draw polygon: expects an sf polygon or a list of coordinate matrices
drawPolygon <- function(poly) {
  if (inherits(poly, "sfc_POLYGON") || inherits(poly, "POLYGON")) {
    coords <- st_coordinates(poly)[,1:2]
    polygon(coords, border = "red")
  } else if (inherits(poly, "sfc")) {
    coords <- st_coordinates(poly)[,1:2]
    polygon(coords, border = "red")
  } else if (is.list(poly)) {
    # if poly is a list of points (each a vector of length 2)
    coords <- do.call(rbind, poly)
    polygon(coords, border = "red")
  }
}

# Draw bounding box using base R graphics
drawBox <- function(bounds) {
  rect(bounds[1], bounds[2], bounds[3], bounds[4], border = "green")
}

#------------------------------#
# Documentation Comments
#------------------------------#
'
this file contains all the functions pertaining to drawing convex polygons around sets of circles. 
The main function is convPoly, which takes in a list of Circles, and returns the convex polygon of that set of circles.
'

#------------------------------#
# Main function
#------------------------------#
main <- function() {
  circ <- Circle(list(x = 0, y = 0), 5)
  radii <- c(88, 17, 13)
}

#------------------------------#
# Circle label finding function
#------------------------------#
circLabel <- function(circ, circleList) { #finds the label of a circle on the drawing
  # Uses identical to compare circle objects
  index <- which(sapply(circleList, function(x) identical(x, circ)))
  return(index[1] + 1)
}

#------------------------------#
# Convex polygon calculation functions
#------------------------------#

extTangents <- function(circ1, circ2) { #calculates the two exterior tangents, notation from wikipedia page on tangent lines to circles
  #takes two circles, gives the ext tangents
  
  #gets both tangents
  tup1 <- circ1$tupCenter()
  x1 <- tup1[1]
  y1 <- tup1[2]
  r1 <- circ1$radius
  
  tup2 <- circ2$tupCenter()
  x2 <- tup2[1]
  y2 <- tup2[2]
  r2 <- circ2$radius
  
  dx <- x2 - x1
  dy <- y2 - y1
  dr <- r2 - r1
  
  D <- st_distance(st_sfc(st_point(c(x1, y1))), st_sfc(st_point(c(x2, y2))))
  D <- as.numeric(D)
  
  nx <- dx / D
  ny <- dy / D
  nr <- dr / D
  
  k1 <- 1  #these are for giving both tangent lines
  k2 <- -1
  
  a1 <- nr * nx - k1 * ny * fsqroot(1 - nr^2) #for ax+by+c=0 line expression
  b1 <- nr * ny + k1 * nx * fsqroot(1 - nr^2)
  c1 <- r1 - (a1 * x1 + b1 * y1)
  
  a2 <- nr * nx - k2 * ny * fsqroot(1 - nr^2)
  b2 <- nr * ny + k2 * nx * fsqroot(1 - nr^2)
  c2 <- r2 - (a2 * x2 + b2 * y2)
  
  # for InfLine or VertLine creation with error handling for vertical lines
  if (abs(b1) > .Machine$double.eps) {
    m1 <- -a1 / b1
    b_line1 <- -c1 / b1
    ext1 <- InfLine(m1, b_line1)
  } else { #in case of vertical line
    ext1 <- VertLine(c1)
  }
  
  if (abs(b2) > .Machine$double.eps) {
    m2 <- -a2 / b2
    b_line2 <- -c2 / b2
    ext2 <- InfLine(m2, b_line2)
  } else { #in case of vertical line
    ext2 <- VertLine(-c2)
  }
  
  exts <- list(ext1, ext2)
  return(exts)
}

centerHull <- function(circleList) { #finds convex hull of the centers of a list of circles
  points_matrix <- do.call(rbind, lapply(circleList, function(c) {
    c(t = c$tupCenter())
  }))
  multipoint <- st_multipoint(points_matrix)
  hull <- st_convex_hull(multipoint)
  return(hull)
}

configBounds <- function(circleList) {
  cHull <- centerHull(circleList)
  
  # Sorting circles by radius in decreasing order to get maximum radius
  sortedCircs <- circleList[order(sapply(circleList, function(x) x$radius), decreasing = TRUE)]
  maxRadius <- sortedCircs[[1]]$radius
  
  boundsVec <- st_bbox(cHull)
  aminx <- boundsVec["xmin"]
  aminy <- boundsVec["ymin"]
  amaxx <- boundsVec["xmax"]
  amaxy <- boundsVec["ymax"]
  
  minx <- aminx - 2 * maxRadius
  miny <- aminy - 2 * maxRadius
  maxx <- amaxx + 2 * maxRadius
  maxy <- amaxy + 2 * maxRadius
  
  bounds <- c(minx, miny, maxx, maxy)
  return(bounds)
}

lineToSegment <- function(line, bounds) { #converts InfLine or VertLine to shapely LineString, bounds defines box that LineString is contained in
  minx <- bounds[1]
  miny <- bounds[2]
  maxx <- bounds[3]
  maxy <- bounds[4]
  
  # create bounding box as an sf polygon
  boundingBox <- st_as_sfc(st_bbox(c(xmin = minx, ymin = miny, xmax = maxx, ymax = maxy)))
  
  if (inherits(line, "VertLine")) { #catches vertical lines
    coords <- matrix(c(line$xInt, miny,
                       line$xInt, maxy), ncol = 2, byrow = TRUE)
    segment <- st_linestring(coords)
    
  } else if (abs(line$m) < .Machine$double.eps) { #catches horizontal lines
    coords <- matrix(c(minx, line$b,
                       maxx, line$b), ncol = 2, byrow = TRUE)
    segment <- st_linestring(coords)
    
  } else {
    y0 <- line$m * minx + line$b
    y1 <- line$m * maxx + line$b
    x0 <- (miny - line$b) / line$m
    x1 <- (maxy - line$b) / line$m
    
    bpoints <- list(st_point(c(x0, miny)),
                    st_point(c(x1, maxy)),
                    st_point(c(minx, y0)),
                    st_point(c(maxx, y1)))
    
    # sort points by distance from boundingBox (using centroid of boundingBox)
    centroid <- st_centroid(boundingBox)
    distVals <- sapply(bpoints, function(pt) {
      as.numeric(st_distance(st_sfc(pt), centroid))
    })
    sorted_bpoints <- bpoints[order(distVals)]
    
    # take first two points and construct segment
    pt1 <- unlist(sorted_bpoints[[1]])
    pt2 <- unlist(sorted_bpoints[[2]])
    coords <- matrix(c(pt1, pt2), ncol = 2, byrow = TRUE)
    segment <- st_linestring(coords)
  }
  
  return(segment)
}

isIntersecting <- function(seg, circ) { #if seg is tangent to circ, returns false
  # convert circle center to sf point
  pt <- st_sfc(st_point(c(circ$center$x, circ$center$y)))
  # st_distance returns a matrix, add a small epsilon
  return(as.numeric(st_distance(seg, pt)) + 0.00000001 < circ$radius)
}

isValidTangent <- function(tanSeg, circleList) {
  cHull <- centerHull(circleList)
  
  #cond1 checks that tanSeg DOESN'T intersect centerHull
  cond1 <- !st_intersects(st_sfc(tanSeg), cHull, sparse = FALSE)[1,1]
  
  #cond2 checks that tanSeg DOESN'T intersect with any circle in circleList
  cond2 <- TRUE #starts as TRUE, set to FALSE if intersection detected
  for (circ in circleList) {
    if (isIntersecting(tanSeg, circ)) {
      cond2 <- FALSE
      break
    }
  }
  
  if (cond1 && cond2) { #if both conditions are met, tanSeg is valid
    return(TRUE)
  } else {
    return(FALSE)
  }
}

# largestOuterCirc :: [Circle] -> Circle
#gets circle of largest radius on the center hull
largestOuterCirc <- function(circleList) {
  cHull <- centerHull(circleList)
  # gets vertices of the convex hull; st_coordinates returns matrix, take unique rows
  vertices <- unique(st_coordinates(cHull)[,1:2, drop=FALSE])
  
  # get list of centers for circles
  centerList <- lapply(circleList, function(c) {
    st_sfc(st_point(c(c$center$x, c$center$y)))
  })
  
  outerCircs <- list()
  for (v in 1:nrow(vertices)) {
    pt <- st_point(vertices[v,])
    # find the circle whose center matches this point
    found <- FALSE
    for (i in seq_along(circleList)) {
      center_pt <- st_point(c(circleList[[i]]$center$x, circleList[[i]]$center$y))
      if (isTRUE(all.equal(as.numeric(pt), as.numeric(center_pt), tolerance = 1e-10))) {
        outerCircs[[length(outerCircs) + 1]] <- circleList[[i]]
        found <- TRUE
        break
      }
    }
    if (!found) {
      # do nothing if not found
    }
  }
  # sort outerCircs by radius decreasing and return the first one
  outerCircs <- outerCircs[order(sapply(outerCircs, function(x) x$radius), decreasing = TRUE)]
  return(outerCircs[[1]])
}

# allValidTangents :: [Circle] -> Bool -> [(InfLine, LineString)]
allValidTangents <- function(circleList, testDraw = FALSE) { #takes a list of circles and returns all of the valid exterior tangents
  #setup
  cHull <- centerHull(circleList)
  bounds <- configBounds(circleList)
  validTans <- list() #list of all valid tangents
  if (testDraw == TRUE) {
    setup(12, 9)
  }
  
  #actually finds the valid tangents
  #sets everything up for while loop
  startCirc <- largestOuterCirc(circleList)
  currentCirc <- startCirc #starts the while loop on startCirc
  prevCircs <- list(startCirc) #so prevCircs isn't empty the first time the while loop checks it
  
  #logic that actually finds and adds all the valid tangents
  done <- FALSE #initializes done
  count <- 1
  while (done == FALSE) {
    potentials <- list() #the list of all potential valid tangents
    
    #Finds all potential tangents
    #ignores currentCirc since cant have tangent from circle to itself, breaks extTangents
    #ignores previous circle since we just got a tangent from there, would risk infinite loop
    for (circ in circleList[sapply(circleList, function(c) { !identical(c, currentCirc) && !identical(c, prevCircs[[length(prevCircs)]]) })]) {
      tans <- extTangents(currentCirc, circ)
      for (tan in tans) { #since extTangents returns a pair of lines
        tanSeg <- lineToSegment(tan, bounds)
        
        #checks that the current tan isn't the same slope as the previous one
        sameSlope <- FALSE #default value
        if (length(validTans) != 0) { #only possible if there even is a previous tangent
          prevTan <- validTans[[length(validTans)]][[1]]  #gets the previous tangent line
          anyVerts <- inherits(tan, "VertLine") || inherits(prevTan, "VertLine")
          if (anyVerts) {
            if (inherits(tan, "VertLine") && inherits(prevTan, "VertLine")) {
              if (isTRUE(all.equal(tan$xInt, prevTan$xInt, tolerance = 1e-10))) {
                sameSlope <- TRUE
              }
            }
          }
          if (!anyVerts && isTRUE(all.equal(tan$m, prevTan$m, tolerance = 1e-10))) {
            sameSlope <- TRUE
          }
        }
        
        if (isValidTangent(tanSeg, circleList) && !sameSlope) { #add to potentials if valid, does nothing if not
          potentials[[length(potentials) + 1]] <- list(c(tan, tanSeg), circ)
        }
      }
    }
    
    #choose which tan to add to validTans, updates currentCirc and prevCircs
    if (length(potentials) != 0) { #potentials always supposed to have at least one thing in it
      #sorts potentials by how far the other circle is from currentCirc
      sortedIndices <- order(sapply(potentials, function(x) {
        as.numeric(st_distance(
          st_sfc(st_point(c(x[[2]]$center$x, x[[2]]$center$y))),
          st_sfc(st_point(currentCirc$tupCenter()))
        ))
      }), decreasing = TRUE)
      sortedPotentials <- potentials[sortedIndices]
      
      bestTan <- sortedPotentials[[1]][[1]]
      bestCirc <- sortedPotentials[[1]][[2]]
      
      validTans[[length(validTans) + 1]] <- bestTan
      prevCircs[[length(prevCircs) + 1]] <- currentCirc
      currentCirc <- bestCirc
      
      if (identical(currentCirc, startCirc)) { #ends the while loop if the currentCircle is the starting circle, since we've gone all the way around
        done <- TRUE
      }
    } else { #not supposed to happen
      break
    }
    
    if (testDraw == TRUE) {
      drawCircles(circleList)
      drawPolygon(cHull)
      # Extract segments from validTans list for drawing
      segs <- lapply(validTans, function(x) x[[2]])
      drawSegments(segs)
      pshow()
    }
    
    count <- count + 1
    if (count > length(circleList)) {
      stop("Too many circles")
    }
  }
  
  return(validTans)
}

findIntPoint <- function(line1, line2) { #takes two InfLines and finds the intersection
  if (inherits(line1, "VertLine")) {
    result <- st_point(c(line1$xInt, line2$m * line1$xInt + line2$b))
  } else if (inherits(line2, "VertLine")) {
    result <- st_point(c(line2$xInt, line1$m * line2$xInt + line1$b))
  } else {
    a <- line1$m
    b <- line2$m
    c_val <- line1$b
    d <- line2$b
    x_int <- (d - c_val) / (a - b)
    result <- st_point(c(x_int, a * x_int + c_val))
  }
  return(result)
}

convPoly <- function(circleList) {
  #separate logic for 1, 2, and 3+ circles
  if (length(circleList) == 1) { #throws an error, should be handled by maxClusterArea
    stop("Can't make polygon from one circle, should have been handled by maxClusterArea")
  }
  
  if (length(circleList) == 2) { #defines a trapezoid type thing
    sortedCircs <- circleList[order(sapply(circleList, function(x) { x$tupCenter() }))]
    c1 <- sortedCircs[[1]]
    c2 <- sortedCircs[[2]]
    tans_pair <- extTangents(c1, c2)
    tan1 <- tans_pair[[1]]
    tan3 <- tans_pair[[2]]
    
    centerSeg <- st_linestring(rbind(c(c1$tupCenter()), c(c2$tupCenter())))
    slope <- (c2$center$y - c1$center$y) / (c2$center$x - c1$center$x)
    perpSlope <- -1 / slope
    
    angle1 <-  atan(slope)
    angle2 <- angle1 + pi
    
    newx1 <- c1$radius * cos(angle2) + c1$center$x
    newy1 <- c1$radius * sin(angle2) + c1$center$y
    
    newx2 <- c2$radius * cos(angle1) + c2$center$x
    newy2 <- c2$radius * sin(angle1) + c2$center$y
    
    tan2 <- InfLine(perpSlope, newy1 - perpSlope * newx1)
    tan4 <- InfLine(perpSlope, newy2 - perpSlope * newx2)
    
    tans <- list(tan1, tan2, tan3, tan4)
    
    intPoints <- list()
    for (index in seq_along(tans)) {
      tN <- tans[[index]]
      tNp1 <- tans[[(index %% length(tans)) + 1]]
      intPoints[[length(intPoints) + 1]] <- findIntPoint(tN, tNp1)
    }
    # Create polygon from intersection points, ensure closure by adding first point at end
    coords <- do.call(rbind, lapply(intPoints, function(pt) { unlist(pt) }))
    coords <- rbind(coords, coords[1,])
    resultConvPoly <- st_polygon(list(coords))
    
    return(resultConvPoly)
    
  } else {
    # Use tryCatch to handle errors as described in the comment
    res <- tryCatch({
      #default algorithm
      tangentTuples <- allValidTangents(circleList)
      exteriorTangents <- lapply(tangentTuples, function(x) { x[[1]] })
      
      intPoints <- list()
      for (index in seq_along(exteriorTangents)) {
        tN <- exteriorTangents[[index]]
        tNp1 <- exteriorTangents[[ (index %% length(exteriorTangents)) + 1 ]]
        intPoints[[length(intPoints) + 1]] <- findIntPoint(tN, tNp1)
      }
      coords <- do.call(rbind, lapply(intPoints, function(pt) { unlist(pt) }))
      coords <- rbind(coords, coords[1,])
      resultConvPoly <- st_polygon(list(coords))
      
      #checks to see if the polygon is actually valid. If not, takes first and last tangent and adds a tangent to the first circle and redoes finding the intersection points to hopefully complete the polygon.
      if (!checkPolygon(circleList, resultConvPoly)) {
        #adds a horizontal line on the starting Circle
        startCirc <- largestOuterCirc(circleList)
        newTangent1 <- InfLine(0.0, startCirc$center$y - startCirc$radius)
        newTangent2 <- InfLine(0.0, startCirc$center$y + startCirc$radius)
        bounds <- configBounds(circleList)
        
        newTanSeg1 <- lineToSegment(newTangent1, bounds)
        newTanSeg2 <- lineToSegment(newTangent2, bounds)
        
        if (isValidTangent(newTanSeg1, circleList)) {
          exteriorTangents[[length(exteriorTangents) + 1]] <- newTangent1
        } else if (isValidTangent(newTanSeg2, circleList)) {
          exteriorTangents[[length(exteriorTangents) + 1]] <- newTangent2
        } else {
          stop("Adding horizontal tangent failed (from checkPolygon fail)\n radii: ", paste(sapply(circleList, function(c) c$radius), collapse = ","))
        }
        
        intPoints <- list()
        for (index in seq_along(exteriorTangents)) {
          tN <- exteriorTangents[[index]]
          tNp1 <- exteriorTangents[[ (index %% length(exteriorTangents)) + 1 ]]
          intPoints[[length(intPoints) + 1]] <- findIntPoint(tN, tNp1)
        }
        coords <- do.call(rbind, lapply(intPoints, function(pt) { unlist(pt) }))
        coords <- rbind(coords, coords[1,])
        resultConvPoly <- st_polygon(list(coords))
      }
      
      return(resultConvPoly)
      
    }, error = function(e) {
      #sometimes breaks as described above, just does the correct alg with the first two circles in the list
      convPoly(circleList[1:2])
    })
    
    return(res)
  }
}

checkPolygon <- function(circleList, polygon) {
  #checks if all the circles are inside the polygon, and the area of the polygon is bigger than the sum of all the circles' area
  cHull <- centerHull(circleList)
  cond1 <- st_covers(polygon, cHull, sparse = FALSE)[1,1]
  
  totalArea <- sum(sapply(circleList, function(c) getArea.Circle(c)))
  cond2 <- st_area(polygon) > totalArea
  
  return(cond1 & cond2)
}

if (sys.nframe() == 0) {
  main()
}

