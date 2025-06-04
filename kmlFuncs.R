
# Required libraries
library(readxl)
library(dplyr)
library(lubridate)
library(xml2)

# This file has all the functions for generating kmzs and kmls.

# utm uses lat lon
# kml.newpoint uses lon lat

# Constants
openpath <- "D:\\Work\\Excel Files\\KRCPLivestockdata Locations UTM Fixed Radii.xlsx"
kmzfolderpath <- "D:\\Work\\QGIS Stuff\\KRCP kmzs"
kmlsavepath <- "D:\\Work\\QGIS Stuff\\TestStuff\\"
housecoords <- c(42.068611, -111.786667)

main <- function() {
  krcp1 <- read_excel(openpath, sheet = 1)
  df_to_kmzs(krcp1)
}

# Helper function to generate circle coordinates (equivalent to polycircles.Polycircle)
generate_circle <- function(latitude, longitude, radius, number_of_vertices = 36) {
  # Convert radius from meters to degrees (approximation)
  # 1 degree latitude ≈ 111,111 meters
  # 1 degree longitude ≈ 111,111 * cos(latitude) meters
  lat_rad <- latitude * pi / 180
  radius_deg_lat <- radius / 111111
  radius_deg_lon <- radius / (111111 * cos(lat_rad))
  
  # Generate circle points
  angles <- seq(0, 2 * pi, length.out = number_of_vertices + 1)
  circle_lats <- latitude + radius_deg_lat * sin(angles)
  circle_lons <- longitude + radius_deg_lon * cos(angles)
  
  # Format as coordinate string for KML
  coords <- paste(circle_lons, circle_lats, "0", sep = ",", collapse = " ")
  return(coords)
}

# Helper function to create KML content
create_kml_content <- function(name, points_data, polygons_data) {
  # Create KML XML structure
  kml_content <- paste0(
    '<?xml version="1.0" encoding="UTF-8"?>\n',
    '<kml xmlns="http://www.opengis.net/kml/2.2">\n',
    '<Document>\n',
    '<name>', name, '</name>\n'
  )
  
  # Add points
  for (i in 1:nrow(points_data)) {
    kml_content <- paste0(kml_content,
                          '<Placemark>\n',
                          '<Point>\n',
                          '<coordinates>', points_data$E[i], ',', points_data$N[i], ',0</coordinates>\n',
                          '</Point>\n',
                          '</Placemark>\n'
    )
  }
  
  # Add polygons (circles)
  for (i in 1:nrow(polygons_data)) {
    circle_coords <- generate_circle(
      polygons_data$N[i], 
      polygons_data$E[i], 
      polygons_data$fixed_radius[i], 
      36
    )
    kml_content <- paste0(kml_content,
                          '<Placemark>\n',
                          '<Polygon>\n',
                          '<outerBoundaryIs>\n',
                          '<LinearRing>\n',
                          '<coordinates>', circle_coords, '</coordinates>\n',
                          '</LinearRing>\n',
                          '</outerBoundaryIs>\n',
                          '</Polygon>\n',
                          '</Placemark>\n'
    )
  }
  
  kml_content <- paste0(kml_content,
                        '</Document>\n',
                        '</kml>'
  )
  
  return(kml_content)
}

# inputs DataFrame, outputs nothing but saves kmzs
# for now have to manually smash them all together into one kmz with google earth, can fix later if needed
df_to_kmzs <- function(df) {
  df_groups <- groupbyCommunityBiweek(df)
  makeBiweekCommFolders(kmzfolderpath)
  
  # Get unique group combinations
  group_keys <- df_groups %>% 
    select(CommAbbreviation, Biweek) %>% 
    distinct()
  
  for (i in 1:nrow(group_keys)) {
    comm <- group_keys$CommAbbreviation[i]
    biweek <- group_keys$Biweek[i]
    
    # Filter data for this group
    group <- df_groups %>% 
      filter(CommAbbreviation == comm, Biweek == biweek)
    
    filename <- paste0(comm, '-', biweek, '.kml')
    filesavepath <- file.path(kmzfolderpath, comm, filename)
    
    document_name <- paste0(comm, '-', biweek)
    
    # Filter valid rows
    valid_rows <- group %>%
      filter(
        !is.na(fixed_radius) & 
          fixed_radius > 0 &
          N > -180.0 & N < 180.0 &
          E > -180.0 & E < 180.0
      )
    
    if (nrow(valid_rows) > 0) {
      # Create KML content
      kml_content <- create_kml_content(document_name, valid_rows, valid_rows)
      
      # Save KML file
      writeLines(kml_content, filesavepath)
    }
  }
}

# inputs dataframe, outputs a processed dataframe with grouping columns
# ignores 2023 dates and oldonyo_nyokie community
groupbyCommunityBiweek <- function(inputdf) {
  
  # inputs date, outputs string
  date_to_biweek <- function(date) {
    result <- ""
    if (day(date) <= 15) {
      result <- "E"
    } else {
      result <- "L"
    }
    
    month_val <- month(date)
    if (month_val == 1) {
      result <- paste0(result, 'Jan')
    } else if (month_val == 2) {
      result <- paste0(result, 'Feb')
    } else if (month_val == 3) {
      result <- paste0(result, 'Mar')
    } else if (month_val == 4) {
      result <- paste0(result, 'Apr')
    } else if (month_val == 5) {
      result <- paste0(result, 'May')
    } else if (month_val == 6) {
      result <- paste0(result, 'Jun')
    } else if (month_val == 7) {
      result <- paste0(result, 'Jul')
    } else if (month_val == 8) {
      result <- paste0(result, 'Aug')
    } else if (month_val == 9) {
      result <- paste0(result, 'Sep')
    } else if (month_val == 10) {
      result <- paste0(result, 'Oct')
    } else if (month_val == 11) {
      result <- paste0(result, 'Nov')
    } else if (month_val == 12) {
      result <- paste0(result, 'Dec')
    }
    return(result)
  }
  
  # takes in full community name ("eselenkei_group_ranch"), outputs 3-letter abbreviation ("ESL")
  comm_to_abbr <- function(comm) {
    if (comm == "eselenkei_group_ranch") {
      return("ESL")
    } else if (comm == "mailua_group_ranch") {
      return("RME")
    } else if (comm == "ol_keri") {
      return("OLK")
    } else if (comm == "olgulului_group_ranch") {
      return("OLG")
    } else if (comm == "olkiramatian") {
      return("OMN")
    } else if (comm == "shompole") {
      return("SHO")
    } else if (comm == "shompole_group_ranch") {
      return("SHO")
    } else {
      print(comm)
      stop("FAIL: unrecognized comm")
    }
  }
  
  # Ensure Date column is properly formatted
  if (!inherits(inputdf$Date, "Date")) {
    inputdf$Date <- as.Date(inputdf$Date)
  }
  
  # filters 2023 dates and oldonyo_nyokie
  inputdf <- inputdf %>%
    filter(
      year(Date) == 2024 &
        Community != "oldonyo_nyokie" &
        Community != "ol_donyo_nyokie"
    )
  
  # Add grouping columns
  inputdf <- inputdf %>%
    mutate(
      Biweek = sapply(Date, date_to_biweek),
      CommAbbreviation = sapply(Community, comm_to_abbr)
    )
  
  return(inputdf)
}

# makes the six subfolders in the root folder
makeBiweekCommFolders <- function(rootFolder) {
  # Create directories if they don't exist
  dir.create(file.path(rootFolder, "ESL"), showWarnings = FALSE, recursive = TRUE)
  dir.create(file.path(rootFolder, "RME"), showWarnings = FALSE, recursive = TRUE)
  dir.create(file.path(rootFolder, "OLK"), showWarnings = FALSE, recursive = TRUE)
  dir.create(file.path(rootFolder, "OLG"), showWarnings = FALSE, recursive = TRUE)
  dir.create(file.path(rootFolder, "OMN"), showWarnings = FALSE, recursive = TRUE)
  dir.create(file.path(rootFolder, "SHO"), showWarnings = FALSE, recursive = TRUE)
}

# Run main function if this script is executed directly
if (sys.nframe() == 0) {
  main()
}

