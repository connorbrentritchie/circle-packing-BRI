#for fixing radius data on spreadsheet

import pandas as pd
import openpyxl as pxl

def radFix(thingy):
    radius = float(thingy)
    if radius <0:
        return None
    elif 5 < radius < 8:
        return None
    elif 0 <= radius <= 5:
        return radius*1000
    elif radius >= 8:
        return radius

def script(file,sheet,func,sourceCol,resultCol,save_loc):
    """file -> string, sheet -> string, func, sourceCol -> String, resultCol -> String, save_loc -> string"""
    def getCols(sheet):
        cols = {}
        for col in sheet.iter_cols():
            title = col[0].value #whatever type col[0].value is, probably a string
            cols[title] = col #a pxl column
        return cols

    #reads the files and sheets
    pdfile = pd.ExcelFile(file, engine = "openpyxl")
    wbfile = pxl.load_workbook(file)

    pdfileS = pdfile.parse(sheet_name = sheet)
    wbfileS = wbfile[sheet]
    wbfileS_cols = getCols(wbfileS)

    #applies func to sourceCol
    pdfileS[resultCol] = pdfileS[sourceCol].apply(func)

    #copies that data into pxl book
    ser = pdfileS[resultCol]
    data = [ser.name] + ser.to_list()
    for i, cell in enumerate(wbfileS_cols[ser.name]):
        cell.value = data[i]

    #saves modified pxl book
    wbfile.save(save_loc)
    print("Success!")


file = r"Excel Files\Kajiado Data v1.xlsx"
sheet = r"Kajiado Livestock Count and Loc"
func = radFix
sourceCol = "radius"
resultCol = "fixed radius"
save_loc = r"Excel Files\Kajiado Data v1 (Fixed Radii).xlsx"
def doit():
    script(file,sheet,func,sourceCol,resultCol,save_loc)
