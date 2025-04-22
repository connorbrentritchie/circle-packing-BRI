import pandas as pd
from polycircles import polycircles
import simplekml as skml

from os import mkdir

'''
this file has all the functions for generating kmzs and kmls.
'''




'''
utm uses lat lon
kml.newpoint uses lon lat
'''

#Constants
openpath = "D:\\Work\\Excel Files\\KRCPLivestockdata Locations UTM Fixed Radii.xlsx"
kmzfolderpath = "D:\\Work\\QGIS Stuff\\KRCP kmzs"

kmlsavepath = "D:\\Work\\QGIS Stuff\\TestStuff\\"
housecoords = (42.068611, -111.786667)



def main():
    krcp1 = pd.read_excel(openpath, sheet_name = 0)
    df_to_kmzs(krcp1)



#inputs DataFrame, outputs nothing but saves kmzs
#for now have to manually smash them all together into one kmz with google earth, can fix later if needed
def df_to_kmzs(df):
    df_groups = groupbyCommunityBiweek(df)
    makeBiweekCommFolders(kmzfolderpath)

    for (comm, biweek), group in df_groups:
        filename = comm + '-' + biweek + '.kml'
        filesavepath = kmzfolderpath + "\\" + comm + "\\" + filename

        currentkmz = skml.Kml()
        currentkmz.document.name = comm + '-' + biweek

        #iterates over every row, 1 row = 1 circle
        for _, row in group.iterrows():
            isValidRow = (
                row["fixed_radius"] is not None and 
                row["fixed_radius"] > 0 and
                -180.0 < row["N"] < 180.0 and
                -180.0 < row["E"] < 180.0
            )

            if isValidRow:
                #the center of the circle

                currentkmz.newpoint(
                    coords = [(row["E"], row["N"])]
                )

                #the circle
                circle = polycircles.Polycircle(
                    latitude = row["N"],
                    longitude = row["E"],
                    radius = row["fixed_radius"],
                    number_of_vertices = 36
                )
                currentkmz.newpolygon(
                    outerboundaryis = circle.to_kml()
                )
        
        currentkmz.save(filesavepath)


        




#inputs dataframe, outputs a DataframeGroupBy
#ignores 2023 dates and oldonyo_nyokie community
def groupbyCommunityBiweek(inputdf):
    
    #inputs datetime64, outputs string
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
            case otherThing:
                print(otherThing)
                raise NameError("FAIL: unrecognized comm")
    
    #filters 2023 dates and oldonyo_nyokie
    inputdf = inputdf.loc[
        (inputdf["Date"].dt.year == 2024) &
        (inputdf["Community"] != "oldonyo_nyokie") &
        (inputdf["Community"] != "ol_donyo_nyokie")
    ]

    #these give "a value is trying to be set on a copy of a slice from a DataFrame" warning, googling indicates probably don't need to care
    inputdf["Biweek"] = inputdf["Date"].apply(date_to_biweek)
    inputdf["CommAbbreviation"] = inputdf["Community"].apply(comm_to_abbr)

    inputdf_groups = inputdf.groupby(
        ["CommAbbreviation","Biweek"]
    )

    return inputdf_groups

#makes the six subfolders in the root folder
def makeBiweekCommFolders(rootFolder):
    mkdir(rootFolder + "\\ESL")
    mkdir(rootFolder + "\\RME")
    mkdir(rootFolder + "\\OLK")
    mkdir(rootFolder + "\\OLG")
    mkdir(rootFolder + "\\OMN")
    mkdir(rootFolder + "\\SHO")


if __name__ == '__main__':
    main()