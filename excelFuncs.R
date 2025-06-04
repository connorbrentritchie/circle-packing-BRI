
### This file contains the functions pertaining to working with the data from excel sheets 

# Load required libraries
library(openxlsx)       # For handling Excel workbooks (equivalent to openpyxl)
library(readxl)         # For reading Excel files (equivalent to pd.read_excel)
library(dplyr)          # For data manipulation and grouping
library(lubridate)      # For date processing

# Source external R files 
# These R files should contain definitions for maxClusterArea, actualClusterArea, newCircle, and convPoly functions
source("finalAlg.R")    # Should define maxClusterArea and actualClusterArea
source("geoThings.R")   # Should define newCircle
source("convPolyFuncs.R")  # Should define convPoly

# Set path to files
setwd("C:\\Users\\allie.heller\\OneDrive - Biodiversity Research Institute\\Desktop\\Kenya\\Kajiado Data\\")
filepath <- 
krcp_filepath <- "KRCPLivestockData_L1.xlsx"
pdtesting_filepath <- 
krcp_resultpath <- 

# Read excel sheets using readxl (sheet = 1 corresponds to first sheet, sheet = 2 to second)
pdkrcp <- readxl::read_excel(krcp_filepath, sheet = 2)

# testinggroups <- pdtesting %>% group_by(Block, Zone, Veggie)
#
# test1 <- function(){
#     results <- list()
#     # print("test group:\n", testinggroups.groups)
#     for(name in group_keys(testinggroups)$...){
#         # In R, grouping iteration would be more elaborate.
#         # This is a commented out test function.
#         # Implementation would require splitting the data frame by group.
#     }
#     return(results)
# }

# df %>% apply(function(x) f(x$col1, x$col2), 1)

getActualArea <- function(accuracyCol, xcoordCol, ycoordCol, radiusCol) {
  go <- function(n) {
    if (abs(n) > 150) {
      return(TRUE)
    } else {
      return(FALSE)
    }
  }
  
  if (any(sapply(accuracyCol, go)) || any(sapply(radiusCol, function(x) { x == 0 }))) {
    return(NULL)
  }
}

getAreasOfActualClusters <- function() {
  go <- function(n) {
    if (abs(n) > 150) {
      return(TRUE)
    } else {
      return(FALSE)
    }
  }
  
  results <- list()
  
  # Group pdkrcp by Date (converted to Date), Zone, and Grazing_Block without sorting
  # Assuming the column "Date" is of Date type or convertible to Date.
  pdkrcp$Date <- as.Date(pdkrcp$Date)
  # Create a grouping factor based on Date, Zone, and Grazing_Block
  group_factor <- interaction(pdkrcp$Date, pdkrcp$Zone, pdkrcp$Grazing_Block, drop=TRUE)
  krcp_groups <- split(pdkrcp, group_factor)
  
  cat("num of groups:", length(krcp_groups), "\n")
  groupNum <- 0
  for (group_name in names(krcp_groups)) {
    group <- krcp_groups[[group_name]]
    groupNum <- groupNum + 1
    cat("\n\n\n\n\n")
    cat(groupNum, "\n")
    
    if (any(sapply(group$GPS_Accuracy, go)) || any(sapply(group$fixed_radius, function(x) { as.numeric(x) == 0.0 }))) {
      group$actual_area <- NA
      results[[length(results) + 1]] <- group$actual_area
    } else {
      circleList <- list()
      for (i in 1:nrow(group)) {
        cat(as.list(group$POINT_X)[[i]], "\n")
        cat(as.list(group$POINT_Y)[[i]], "\n")
        cat(as.list(group$fixed_radius)[[i]], "\n")
        
        circleList[[length(circleList) + 1]] <- newCircle(
          group$POINT_X[i],
          group$POINT_Y[i],
          group$fixed_radius[i]
        )
      }
      
      # Try to compute actual_cluster area using actualClusterArea
      mcArea <- tryCatch({
        cat("doing area\n")
        actual_cluster <- actualClusterArea(circleList)
        cat("finished area\n")
        actual_cluster
      }, error = function(e) {
        cat("shit\n")
        0
      })
      group$actual_area <- mcArea
      results[[length(results) + 1]] <- group$actual_area
    }
    
    print(group[, c("Date", "Zone", "Grazing_Block", "GPS_Accuracy", "POINT_X", "POINT_Y", "fixed_radius", "actual_area")])
    cat("finished group", groupNum, "\n")
    
    # Update the group in the main dataframe
    idx <- which(group_factor == group_name)
    pdkrcp$actual_area[idx] <<- group$actual_area
  }
  
  cat("\n\n\n\n\nResults:")
  print(pdkrcp[, c("GPS_Accuracy", "POINT_X", "POINT_Y", "fixed_radius", "actual_area")])
  
  write.csv(pdkrcp, krcp_resultpath, row.names = FALSE)
}

getAreasOfActualClusters()

applyMaxClusterArea <- function() {
  '
    iterate over radius column
    for each cell, associate to it
        1. the date, block, and zone cells in the same row
        2. the result cell in the "maximum cluster area" column
    '
  
  # openxlsx loading
  kaj <- loadWorkbook(filepath)
  sheet_names <- names(kaj)
  kaj1 <- read.xlsx(kaj, sheet = sheet_names[1], colNames = FALSE)
  
  # Helper function to create "cell" objects with value and row properties
  createCellsVector <- function(colVector) {
    cells <- list()
    for (i in seq_along(colVector)) {
      cells[[i]] <- list(value = colVector[i], row = i)
    }
    return(cells)
  }
  
  # For each column, makes a dictionary entry of the value of the 1st row, and the rest of the cells
  getCols <- function(sheet_df) {
    cols <- list()
    for (j in 1:ncol(sheet_df)) {
      colVector <- sheet_df[[j]]
      cells <- createCellsVector(colVector)
      title <- cells[[1]]$value  # whatever type, probably a string
      # Store the non-first elements of the column, skipping the title
      cols[[as.character(title)]] <- cells[-1]
    }
    return(cols)
  }
  
  columns <- getCols(kaj1)
  
  assocCells <- function(colName, dataCols, resultCol) {
    # string, [string], string
    results <- list()
    # Iterate over each cell in the specified column
    for (cell in columns[[colName]]) {
      rowNum <- cell$row - 1  # In our cells, header was removed so row index aligns (original row - 2 in Python becomes -1 here)
      dataList <- c()
      for (name in dataCols) {
        # Get the value from the corresponding cell from each specified column
        dataList <- c(dataList, columns[[name]][[rowNum]]$value)
      }
      results[[length(results) + 1]] <- list(cell, dataList, columns[[resultCol]][[rowNum]])
    }
    return(results)
  }
  
  stuff <- assocCells("fixed radius", c("Date", "Zone", "Grazing Block"), "max cluster area")
  
  # Group rows using grouping by the second element of each list (dataList)
  # We use the concatenated string of the dataList as key
  group_keys <- sapply(stuff, function(c) { paste(c[[2]], collapse = ",") })
  groupedRows <- split(stuff, group_keys)
  groupedRows <- lapply(groupedRows, function(x) { x })  # convert to list of groups
  
  cat("There are", length(groupedRows), "groups\n")
  
  doit <- function() {
    for (g in groupedRows) {
      tryCatch({
        radii <- sapply(g, function(el) { el[[1]]$value })
        if (any(sapply(radii, is.null)) || any(sapply(radii, function(x) { is.na(x) }))) {
          mcArea <- NULL
        } else if (any(radii == 0)) {
          nonzeroRadii <- radii[radii != 0]
          if (length(nonzeroRadii) == 0) {
            mcArea <- NULL
          } else {
            mcArea <- maxClusterArea(nonzeroRadii)
          }
        } else {
          mcArea <- maxClusterArea(radii)
        }
        
        # For each cell in the result column, assign the computed mcArea
        for (el in g) {
          el[[3]]$value <- mcArea
        }
        
        cat("Finished group\n")
      }, error = function(e) {
        print(g)
        quit(status = 0)
      })
    }
    cat("Finished all the groups\n")
  }
  
  saveit <- function() {
    resultpath <- "D:\\Work\\Excel Files\\Kajiado Data Results.xlsx"
    saveWorkbook(kaj, resultpath, overwrite = TRUE)
  }
  
  doit()
  saveit()
}

applyMaxClusterArea()
