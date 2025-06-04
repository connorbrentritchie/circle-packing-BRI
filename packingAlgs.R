
# Required libraries
library(pracma)    # for mathematical functions like sqrt
library(ggplot2)   # for plotting (matplotlib equivalent)

# Import custom modules (these would need to be implemented in R)
# source("convPolyFuncs.R")  # for convPoly function
# source("geoThings.R")      # for Circle, InfLine, VertLine, fsqroot, randomList, printCircleData
# source("drawFuncsV2.R")    # for setup, pshow, pdraw, drawCircles, drawPoints, drawLines, drawSegments, drawPolygon, removeCircles, removePoints

# Point class implementation for R
Point <- function(x, y) {
  structure(list(x = x, y = y), class = "Point")
}

# Distance method for Point objects
distance.Point <- function(p1, p2) {
  sqrt((p1$x - p2$x)^2 + (p1$y - p2$y)^2)
}

# Affinity transformations (shapely equivalent)
translate_point <- function(point, xoff, yoff) {
  Point(point$x + xoff, point$y + yoff)
}

rotate_point <- function(point, angle_degrees, origin = c(0, 0)) {
  angle_rad <- angle_degrees * pi / 180
  cos_a <- cos(angle_rad)
  sin_a <- sin(angle_rad)
  
  # Translate to origin
  x <- point$x - origin[1]
  y <- point$y - origin[2]
  
  # Rotate
  x_new <- x * cos_a - y * sin_a
  y_new <- x * sin_a + y * cos_a
  
  # Translate back
  Point(x_new + origin[1], y_new + origin[2])
}

# This file has all the maximum packing algorithms.
# The main two are radSumAlg and polyAreaAlg.
#     polyAreaAlg is the true greedy algorithm and is ridiculously slow for anything over about 15 circles.
#     radSumAlg minimizes the pairwise sum of distances between circle centers, which is much faster than and just about as accurate as polyAreaAlg for over 15 circles.

main <- function() {
  # 50 1850 2950
  radii <- c(50, 1850, 2950)
  testc <- radSumAlg(radii)
  testd <- convPoly(testc)
  
  setup()
  drawCircles(testc)
  drawPolygon(testd)
  pshow()
}

isOverlap <- function(c1, c2) { # checks to see if two circles overlap
  radSum <- c1$radius + c2$radius
  centerDist <- distance.Point(c1$center, c2$center)
  return(centerDist + 0.000001 < radSum) # floating point error???
}

isTangentPossible <- function(c1, c2, R) {
  # checks to see if a circle with radius R can even be tangent to c1 and c2
  maxDistance <- 2 * R + c1$radius + c2$radius
  centerDist <- distance.Point(c1$center, c2$center)
  if (centerDist > maxDistance) {
    return(FALSE)
  } else {
    return(TRUE)
  }
}

tangentPoints <- function(circ1, circ2, newRad) {
  # finds the two possible centers
  # needs circ1 at origin and circ2 on y axis
  # returns list of Points
  A <- circ1$radius
  B <- circ2$radius
  D <- distance.Point(circ1$center, circ2$center)
  k <- newRad
  y <- ((A + k)^2 + (D)^2 - (B + k)^2) / (2 * (D))
  x1 <- fsqroot((A + k)^2 - y^2)
  x2 <- -1 * x1
  return(list(Point(x1, y), Point(x2, y)))
}

tangentPlacements <- function(c1, c2, R) { # finds the two possible center points
  if (isTangentPossible(c1, c2, R) == FALSE) {
    return(NULL)
  } else {
    # Translate
    trC1 <- Circle(Point(0, 0), c1$radius)
    trC2 <- Circle(
      translate_point(c2$center, -1 * c1$center$x, -1 * c1$center$y),
      c2$radius
    )
    
    # Rotate around origin until c2 on y axis
    if (trC2$center$x == 0 && trC2$center$y > 0) {
      angle <- 0
    } else if (trC2$center$x == 0 && trC2$center$y < 0) {
      angle <- 180
    } else if (trC2$center$x < 0) {
      angle <- atan2(trC2$center$x, trC2$center$y) * 180 / pi
    } else if (trC2$center$x > 0) {
      angle <- 90 - atan2(trC2$center$y, trC2$center$x) * 180 / pi
    } else {
      stop("Impossible angle detected")
    }
    
    rotC1 <- trC1 # circle 1 doesn't change under rotation
    rotC2 <- Circle(
      rotate_point(trC2$center, angle, c(0, 0)),
      c2$radius
    )
    
    # Apply tangentPoints
    possibleCenters <- tangentPoints(rotC1, rotC2, R) # The two possible centers
    
    # Inverse rotate results
    invRot <- list() # the two centers are reverse rotated
    for (i in seq_along(possibleCenters)) {
      p <- possibleCenters[[i]]
      invRot[[i]] <- rotate_point(p, -1 * angle, c(0, 0))
    }
    
    # Inverse translate results
    invTrans <- list() # the two centers are then reverse translated, giving the final result
    for (i in seq_along(invRot)) {
      p <- invRot[[i]]
      invTrans[[i]] <- translate_point(p, c1$center$x, c1$center$y)
    }
    
    return(invTrans) # list of Points
  }
}

polyAreaAlg <- function(radii) {
  
  radii <- sort(radii) # sorts the list of radii again just in case
  radii <- rev(radii)
  
  maxc <- list() # max cluster diagram, basically a list of circles
  runningSubsets <- list() # set of two element subsets of maxC, updated every iteration
  
  for (index in seq_along(radii)) {
    rk <- radii[index]
    possiblePlacements <- list()
    
    if (index == 1) { # adds the first circle at the origin
      maxc[[length(maxc) + 1]] <- Circle(Point(0, 0), rk)
      next
    } else if (index == 2) { # rigs the code so the second circle is added tangent to the first circle, and skips to updating the running vars
      if (radii[1] == rk) { # designed to avoid vertical lines
        x <- radii[1] / 2
      } else {
        x <- (radii[1] - rk) / 2
      }
      R <- radii[1] + rk
      y <- fsqroot(R^2 - x^2)
      possiblePlacements[[length(possiblePlacements) + 1]] <- list(Point(x, y), R)
    } else {
      count <- 1
      
      # Create a copy of runningSubsets to iterate over
      subsetsToProcess <- runningSubsets
      
      for (i in seq_along(subsetsToProcess)) { # runs tangentPlacements on every pair of circles in maxc
        sub <- subsetsToProcess[[i]]
        
        centerPair <- tangentPlacements(sub[[1]], sub[[2]], rk) # finds the pair of possible centers for a given subset
        if (is.null(centerPair)) {
          # Remove subset for computing time, works because radii only get smaller every iteration
          runningSubsets <- runningSubsets[runningSubsets != list(sub)]
          next
        }
        
        for (j in seq_along(centerPair)) { # does the following for both possible placements
          place <- centerPair[[j]]
          isValid <- TRUE # default value
          placeCirc <- Circle(place, rk) # defines a test circle for isOverlap()
          
          for (k in seq_along(maxc)) { # checks validity of placement
            circ <- maxc[[k]]
            if (isOverlap(placeCirc, circ) == TRUE) {
              isValid <- FALSE
              break
            }
          }
          
          if (isValid == TRUE) { # only allows a placement to be added to possiblePlacements if it's valid
            testConfig <- c(maxc, list(placeCirc))
            testConvPoly <- convPoly(testConfig)
            
            count <- count + 1
            
            possiblePlacements[[length(possiblePlacements) + 1]] <- list(place, testConvPoly$area) # adds the placement along with its associated pcdSum to the list of possible placements
          }
        }
      }
    }
    
    sortedPossibles <- possiblePlacements[order(sapply(possiblePlacements, function(x) x[[2]]))] # sorts possiblePlacements by polygon area
    
    minp <- sortedPossibles[[1]] # chooses the placement with the smallest pcdSum
    
    newCirc <- Circle(minp[[1]], rk) # defines new circle with center minp and radius rk
    
    for (i in seq_along(maxc)) { # adds all the new subsets associated with newCirc
      circ <- maxc[[i]]
      runningSubsets[[length(runningSubsets) + 1]] <- list(circ, newCirc)
    }
    
    maxc[[length(maxc) + 1]] <- newCirc # adds newCirc to the max cluster diagram
  }
  return(maxc)
}

radSumAlg <- function(radii) {
  
  radii <- sort(radii) # sorts the list of radii again just in case
  radii <- rev(radii)
  
  maxc <- list() # max cluster diagram, basically a list of circles
  runningSum <- 0 # sum of pairwise distances between centers, updated every iteration
  runningSubsets <- list() # set of two element subsets of maxC, updated every iteration
  
  for (index in seq_along(radii)) {
    rk <- radii[index]
    possiblePlacements <- list()
    
    if (index == 1) { # adds the first circle at the origin
      maxc[[length(maxc) + 1]] <- Circle(Point(0, 0), rk)
      next
    } else if (index == 2) { # rigs the code so the second circle is added tangent to the first circle, and skips to updating the running vars
      if (radii[1] == rk) { # designed to avoid vertical lines
        x <- radii[1] / 2
      } else {
        x <- (radii[1] - rk) / 2
      }
      R <- radii[1] + rk
      y <- fsqroot(R^2 - x^2)
      possiblePlacements[[length(possiblePlacements) + 1]] <- list(Point(x, y), R)
    } else {
      # Create a copy of runningSubsets to iterate over
      subsetsToProcess <- runningSubsets
      
      for (i in seq_along(subsetsToProcess)) { # runs tangentPlacements on every pair of circles in maxc
        sub <- subsetsToProcess[[i]]
        
        centerPair <- tangentPlacements(sub[[1]], sub[[2]], rk) # finds the pair of possible centers for a given subset
        if (is.null(centerPair)) {
          # Remove subset for computing time, works because radii only get smaller every iteration
          runningSubsets <- runningSubsets[runningSubsets != list(sub)]
          next
        }
        
        for (j in seq_along(centerPair)) { # does the following for both possible placements
          place <- centerPair[[j]]
          isValid <- TRUE # default value
          placeCirc <- Circle(place, rk) # defines a test circle for isOverlap()
          
          for (k in seq_along(maxc)) { # checks validity of placement
            circ <- maxc[[k]]
            if (isOverlap(placeCirc, circ) == TRUE) {
              isValid <- FALSE
              break
            }
          }
          
          if (isValid == TRUE) { # only allows a placement to be added to possiblePlacements if it's valid
            pcdSum <- runningSum
            for (k in seq_along(maxc)) { # creates the pairwise center distance sum for a given placement
              circ <- maxc[[k]]
              pcdSum <- pcdSum + distance.Point(place, circ$center)
            }
            
            possiblePlacements[[length(possiblePlacements) + 1]] <- list(place, pcdSum) # adds the placement along with its associated pcdSum to the list of possible placements
          }
        }
      }
    }
    
    sortedPossibles <- possiblePlacements[order(sapply(possiblePlacements, function(x) x[[2]]))] # sorts possiblePlacements by pcdSum, smallest first
    
    minp <- sortedPossibles[[1]] # chooses the placement with the smallest pcdSum
    
    newCirc <- Circle(minp[[1]], rk) # defines new circle with center minp and radius rk
    
    runningSum <- runningSum + minp[[2]] # updates the running pairwise distance sum by stealing the pcdSum from minp. Equiv to iterating over maxc again
    
    for (i in seq_along(maxc)) { # adds all the new subsets associated with newCirc
      circ <- maxc[[i]]
      runningSubsets[[length(runningSubsets) + 1]] <- list(circ, newCirc)
    }
    
    maxc[[length(maxc) + 1]] <- newCirc # adds newCirc to the max cluster diagram
  }
  return(maxc)
}

randomAlg <- function(radii) {
  
  radii <- sample(radii) # shuffle the radii
  
  maxc <- list() # max cluster diagram, basically a list of circles
  runningSum <- 0 # sum of pairwise distances between centers, updated every iteration
  runningSubsets <- list() # set of two element subsets of maxC, updated every iteration
  
  for (index in seq_along(radii)) {
    rk <- radii[index]
    possiblePlacements <- list()
    
    if (index == 1) { # adds the first circle at the origin
      maxc[[length(maxc) + 1]] <- Circle(Point(0, 0), rk)
      next
    } else if (index == 2) { # rigs the code so the second circle is added tangent to first one, and skips to updating the running vars
      if (radii[1] == rk) {
        x <- radii[1]
      } else {
        x <- (radii[1] - rk) / 2
      }
      R <- radii[1] + rk
      y <- fsqroot(R^2 - x^2)
      possiblePlacements[[length(possiblePlacements) + 1]] <- list(Point(x, y), R)
    } else {
      for (i in seq_along(runningSubsets)) { # runs tangentPlacements on every pair of circles in maxc
        sub <- runningSubsets[[i]]
        centerPair <- tangentPlacements(sub[[1]], sub[[2]], rk) # finds the pair of possible centers for a given subset
        
        if (is.null(centerPair)) {
          # runningSubsets.remove(sub) # removes subset for computing time, works because radii only get smaller every iteration
          next
        }
        
        for (j in seq_along(centerPair)) { # does the following for both possible placements
          place <- centerPair[[j]]
          isValid <- TRUE # default value
          placeCirc <- Circle(place, rk) # defines a test circle for isOverlap()
          
          for (k in seq_along(maxc)) { # checks validity of placement
            circ <- maxc[[k]]
            if (isOverlap(placeCirc, circ) == TRUE) {
              isValid <- FALSE
              break
            }
          }
          
          if (isValid == TRUE) { # only allows a placement to be added to possiblePlacements if it's valid
            pcdSum <- runningSum
            for (k in seq_along(maxc)) { # creates the pairwise center distance sum for a given placement
              circ <- maxc[[k]]
              pcdSum <- pcdSum + distance.Point(place, circ$center)
            }
            
            possiblePlacements[[length(possiblePlacements) + 1]] <- list(place, pcdSum) # adds the placement along with its associated pcdSum to the list of possible placements
          }
        }
      }
    }
    
    minp <- sample(possiblePlacements, 1)[[1]] # chooses a random placement
    
    newCirc <- Circle(minp[[1]], rk) # defines new circle with center minp and radius rk
    
    runningSum <- runningSum + minp[[2]] # updates the running pairwise distance sum by stealing the pcdSum from minp. Equiv to iterating over maxc again
    
    for (i in seq_along(maxc)) { # adds all the new subsets associated with newCirc
      circ <- maxc[[i]]
      runningSubsets[[length(runningSubsets) + 1]] <- list(circ, newCirc)
    }
    
    maxc[[length(maxc) + 1]] <- newCirc # adds newCirc to the max cluster diagram
  }
  
  return(maxc)
}

# NOT DONE YET
radSumAlgPresentation <- function(radii, speed) { # draws each step of the alg
  
  radii <- sort(radii) # sorts the list of radii again just in case
  radii <- rev(radii)
  
  maxc <- list() # max cluster diagram, basically a list of circles
  runningSum <- 0 # sum of pairwise distances between centers, updated every iteration
  runningSubsets <- list() # set of two element subsets of maxC, updated every iteration
  
  for (index in seq_along(radii)) {
    rk <- radii[index]
    # fig <- current plot (R equivalent would be getting current graphics device)
    title(paste('Cycle', index))
    
    possiblePlacements <- list()
    
    if (index == 1) { # adds the first circle at the origin
      maxc[[length(maxc) + 1]] <- Circle(Point(0, 0), rk)
      drawCircles(maxc)
      pdraw(speed + 3)
      next
    } else if (index == 2) { # rigs the code so the second circle is added on y axis, and skips to updating the running vars
      possiblePlacements[[length(possiblePlacements) + 1]] <- list(Point(0, radii[1] + rk), radii[1] + rk)
    } else {
      allPlacements <- list()
      validPlacements <- list()
      
      # Create a copy of runningSubsets to iterate over
      subsetsToProcess <- runningSubsets
      
      for (i in seq_along(subsetsToProcess)) { # runs tangentPlacements on every pair of circles in maxc
        sub <- subsetsToProcess[[i]]
        
        centerPair <- tangentPlacements(sub[[1]], sub[[2]], rk) # finds the pair of possible centers for a given subset
        if (is.null(centerPair)) {
          # Remove subset for computing time, works because radii only get smaller every iteration
          runningSubsets <- runningSubsets[runningSubsets != list(sub)]
          next
        }
        
        for (j in seq_along(centerPair)) { # does the following for both possible placements
          place <- centerPair[[j]]
          isValid <- TRUE # default value
          placeCirc <- Circle(place, rk) # defines a test circle for isOverlap()
          allPlacements[[length(allPlacements) + 1]] <- place
          
          for (k in seq_along(maxc)) { # checks validity of placement
            circ <- maxc[[k]]
            if (isOverlap(placeCirc, circ) == TRUE) {
              isValid <- FALSE
              break
            }
          }
          
          if (isValid == TRUE) { # only allows a placement to be added to possiblePlacements if it's valid
            pcdSum <- runningSum
            for (k in seq_along(maxc)) { # creates the pairwise center distance sum for a given placement
              circ <- maxc[[k]]
              pcdSum <- pcdSum + distance.Point(place, circ$center)
            }
            
            possiblePlacements[[length(possiblePlacements) + 1]] <- list(place, pcdSum) # adds the placement along with its associated pcdSum to the list of possible placements
            validPlacements[[length(validPlacements) + 1]] <- place
          }
        }
        
        # fig <- current plot
        # Find indices for subset display
        sub1_index <- which(sapply(maxc, function(x) identical(x, sub[[1]])))
        sub2_index <- which(sapply(maxc, function(x) identical(x, sub[[2]])))
        title(paste('Subset:', paste(c(sub1_index, sub2_index), collapse = ",")))
        
        allPlacements_p <- drawPoints(allPlacements, 'red', 'o')
        maxc_p <- drawCircles(maxc)
        pdraw(speed / 1.5)
        removePoints(allPlacements_p)
        removeCircles(maxc_p)
      }
      
      allPlacements_p <- drawPoints(allPlacements, 'red', 'o')
      maxc_p <- drawCircles(maxc)
      pdraw(speed)
      removePoints(allPlacements_p)
      removeCircles(maxc_p)
      
      validPlacements_p <- drawPoints(validPlacements, 'y', 'o')
      maxc_p <- drawCircles(maxc)
      pdraw(speed)
      removePoints(validPlacements_p)
      removeCircles(maxc_p)
    }
    
    sortedPossibles <- possiblePlacements[order(sapply(possiblePlacements, function(x) x[[2]]))] # sorts possiblePlacements by pcdSum, smallest first
    
    minp <- sortedPossibles[[1]] # chooses the placement with the smallest pcdSum
    minp_p <- drawPoints(list(minp[[1]]), 'green', 'o')
    maxc_p <- drawCircles(maxc)
    pdraw(speed)
    removePoints(minp_p)
    removeCircles(maxc_p)
    
    newCirc <- Circle(minp[[1]], rk) # defines new circle with center minp and radius rk
    
    runningSum <- runningSum + minp[[2]] # updates the running pairwise distance sum by stealing the pcdSum from minp. Equiv to iterating over maxc again
    
    for (i in seq_along(maxc)) { # adds all the new subsets associated with newCirc
      circ <- maxc[[i]]
      runningSubsets[[length(runningSubsets) + 1]] <- list(circ, newCirc)
    }
    
    maxc[[length(maxc) + 1]] <- newCirc # adds newCirc to the max cluster diagram
    maxc_p <- drawCircles(maxc)
    pdraw(speed)
    removeCircles(maxc_p)
  }
  
  return(maxc)
}

# Execute main function when script is run directly
if (sys.nframe() == 0) {
  main()
}

