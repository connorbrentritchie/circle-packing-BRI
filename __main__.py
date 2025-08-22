import pandas as pd
import simplekml as skml
from polycircles import polycircles
import utm
from packingAlgs import radSumAlg
from drawFuncsV2 import setup, pshow, drawCircles, drawPolygon
from convPolyFuncs import convPoly, centerHull
from geoThings import newCircle

from pathlib import Path

source_folder = r"C:\Users\conno\Documents\Work\Excel Files\KRCP Livestockdata (2024 only).xlsx"
krcp = pd.read_excel(source_folder)

#takes in full community name ("eselenkei_group_ranch"), outputs 3-letter abbreviation ("ESL")
def comm_to_abbr(comm):
    match comm:
        case "eselenkei_group_ranch":
            return "ESL"
        case "mailua_group_ranch":
            return "RME"
        case "ol_keri":
            return "OLK"
        case "olgulului_group_ranch":
            return "OLG"
        case "olkiramatian":
            return "OMN"
        case "shompole":
            return "SHO"
        case "shompole_group_ranch":
            return "SHO"
        case "oldonyo_nyokie":
            return "OLN"
        case otherThing:
            print(otherThing)
            raise NameError("FAIL: unrecognized comm")

#converts date to string representing the biweek. 'E' is 'Early', and 'L' is 'Late'.
def date_to_biweek(date):
    result = ""
    if date.day <= 15:
        result = "E"
    else:
        result = "L"

    match date.month:
        case 1:
            result += 'Jan'
        case 2:
            result += 'Feb'
        case 3:
            result += 'Mar'
        case 4:
            result += 'Apr'
        case 5:
            result += 'May'
        case 6:
            result += 'Jun'
        case 7:
            result += 'Jul'
        case 8:
            result += 'Aug'
        case 9:
            result += 'Sep'
        case 10:
            result += 'Oct'
        case 11:
            result += 'Nov'
        case 12:
            result += 'Dec'
    return result


def gen_kmzs():
    save_folder = Path.cwd().parent
    if not save_folder.joinpath("Footprint-kmzs").exists():
        Path.mkdir(save_folder.joinpath("Footprint-kmzs"))
    footprints_save_folder = save_folder.joinpath("Footprint-kmzs")
    if not save_folder.joinpath("Livestock-Location-kmzs").exists():
        Path.mkdir(save_folder.joinpath("Livestock-Location-kmzs"))
    locations_save_folder = save_folder.joinpath("Livestock-Location-kmzs")
    print(locations_save_folder)

    for tup_name, community in krcp.groupby(["Community"]):
        name = comm_to_abbr(tup_name[0])
        print(name)
        
        community["CommAbbr"] = community["Community"].apply(comm_to_abbr)
        community["Biweek"] = community["Date"].apply(date_to_biweek)

        locations_kml = skml.Kml()
        locations_kml.document.name = name + " Livestock Locations"
        footprints_kml = skml.Kml()
        footprints_kml.document.name = name + " Footprints"

        for (zone, bwk), group in community.groupby(["Zone","Biweek"]):
            locations_folder = locations_kml.newfolder(name = bwk + "-" + zone)

            #for making the footprint
            Z_NUM = 37
            Z_LETTER = 'M'
            circList = [] 

            for _, row in group.iterrows():
                isValidRow = (
                    row["radius"] is not None and 
                    row["radius"] > 0 and
                    -180.0 < row["N"] < 180.0 and
                    -180.0 < row["E"] < 180.0
                )

                if isValidRow:
                    #adding the circle to circList to make the footprint
                    x, y, _, _ = utm.from_latlon(row["N"], row["E"])
                    circList.append(newCircle(x,y,row["radius"]))

                    #the center of the circle
                    locations_folder.newpoint(
                        name = bwk + '-' + zone,
                        coords = [(row["E"], row["N"])]
                    )

                    #the circle
                    circle = polycircles.Polycircle(
                        latitude = row["N"],
                        longitude = row["E"],
                        radius = row["radius"],
                        number_of_vertices = 36
                    )
                    locations_folder.newpolygon(
                        name = bwk + '-' + zone,
                        outerboundaryis = circle.to_kml()
                    )
            
            if circList != []:
                try:
                    footprint = convPoly(circList)
                    vertices = [utm.to_latlon(vertex[0], vertex[1], Z_NUM, Z_LETTER)[::-1] for vertex in footprint.exterior.coords]
                    footprints_kml.newpolygon(name = bwk + '-' + zone, outerboundaryis = vertices)
                except:
                    continue
        
        locations_kml.savekmz(locations_save_folder.joinpath(name + "-Locations.kmz").as_uri()[8:])
        footprints_kml.savekmz(footprints_save_folder.joinpath(name + "-Footprints.kmz").as_uri()[8:])

gen_kmzs()

def compute_footprint_area():
    save_folder = Path(source_folder).parent
    krcp["Biweek"] = krcp["Date"].apply(date_to_biweek)

    results = []
    for _, group in krcp.groupby(["Biweek","Zone"]):
        circlist = []

        for _, row in group.iterrows():
            isValidRow = (
                row["radius"] is not None and 
                row["radius"] > 0 and
                -180.0 < row["N"] < 180.0 and
                -180.0 < row["E"] < 180.0
            )
            if isValidRow:
                circlist.append(newCircle(row["POINT_X"], row["POINT_Y"], row["radius"]))
        
        if len(circlist) == 0:
            group["Footprint Area"] = 0
        else:
            group["Footprint Area"] = convPoly(circlist).area
        results.append(group["Footprint Area"])

    krcp["Footprint Area"] = pd.concat(results)
    krcp.drop(columns = ["Biweek"])

    krcp.to_csv(r"C:\Users\conno\Documents\Work\Excel Files\Results.csv")

compute_footprint_area()