from geoThings import Circle, newCircle

import pandas as pd
from shapely import Point, Polygon
from polycircles import polycircles
import simplekml as skml
import utm

'''
utm uses lat, lon
kml.newpoint uses lon lat
'''

openpath = "D:\\Work\\Excel Files\\KRCPLivestockdata Locations UTM Fixed Radii.xlsx"

def main():
    krcp1 = pd.read_excel(openpath, sheet_name = 0)
    groupbyCommunityBiweek(krcp1)




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
                return "OLK"
            case "shompole":
                return "SHO"
            case "shompole_group_ranch":
                return "SHO"
    
    #filters 2023 dates and oldonyo_nyokie
    inputdf = inputdf.loc[
        (inputdf["Date"].dt.year == 2024) &
        (inputdf["Community"] != "oldonyo_nyokie") &
        (inputdf["Community"] != "ol_donyo_nyokie")
    ]

    inputdf["Date"] = inputdf["Date"].apply(date_to_biweek)
    inputdf["Community"] = inputdf["Community"].apply(comm_to_abbr)

    inputdf_groups = inputdf.groupby(
        ["Date","Community"]
    )

    return inputdf_groups


if __name__ == '__main__':
    main()