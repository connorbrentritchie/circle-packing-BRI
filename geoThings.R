library(R6)

# Define a simple Point structure to mimic shapely.Point
Point <- function(x, y) {
  structure(list(x = x, y = y), class = "Point")
}


# this file has all the basic classes used in the rest of the program, mainly InfLine and Circle.
# Circle consists of a shapely Point and a radius.
# InfLine consists of a slope (m) and a y-intercept (b).
# VertLine is just an x-intercept.


Circle <- R6Class("Circle",
                  public = list(
                    center = NULL,
                    radius = NULL,
                    initialize = function(center, radius) {
                      self$center <- center
                      self$radius <- as.numeric(radius)
                    },
                    tupCenter = function() { # returns the center of the circle as a tuple
                      return(c(self$center$x, self$center$y))
                    },
                    data = function() {
                      return(list(c(self$center$x, self$center$y), self$radius))
                    },
                    getArea = function() {
                      return(pi * self$radius^2)
                    }
                  )
)

newCircle <- function(xcoord, ycoord, radius) {
  return(Circle$new(Point(xcoord, ycoord), radius))
}

InfLine <- R6Class("InfLine", # expressed as y=mx+b, short for infinite line
                   public = list(
                     m = NULL,
                     b = NULL,
                     initialize = function(slope, yInt) {
                       self$m <- slope
                       self$b <- yInt
                     }
                   )
)

VertLine <- R6Class("VertLine", # extTangents can give vertical lines, and InfLine can't represent these
                    public = list(
                      xInt = NULL,
                      initialize = function(xInt) {
                        self$xInt <- xInt
                      }
                    )
)

# these are here because they don't fit anywhere else, and every other file imports geoThings
fsqroot <- function(val) {
  if(val >= 0) {
    return(sqrt(val))
  } else {
    return(0)
  }
}

randomList <- function(length, min, max) {
  list <- c()
  for(i in 1:length) {
    list <- c(list, sample(min:max, 1))
  }
  return(list)
}

printCircleData <- function(circList, doTerm = TRUE) {
  print('\nCIRCLE DATA')
  testing <- file('Testing.txt', 'w')
  for(index in seq_along(circList)) {
    circ <- circList[[index]]
    if(doTerm) {
      cat('\nCircle number', index, ' ', sep = " ")
      cat('(testCluster index:', index - 1, ')', '\n', sep = " ")
      cat('\tCenter:', circ$tupCenter(), '\n')
      cat('\tRadius:', circ$radius, '\n')
    }
    
    cat('\nCircle number', index, ' ', sep = " ", file = testing)
    cat('(testCluster index:', index - 1, ')', '\n', sep = " ", file = testing)
    cat('\tCenter:', circ$tupCenter(), '\n', sep = " ", file = testing)
    cat('\tRadius:', circ$radius, '\n', sep = " ", file = testing)
  }
  close(testing)
}

if (sys.nframe() == 0) {
  print("hi command line :D")
}
