import openpyxl as pxl
from itertools import groupby
import sys
from finalAlg import maxClusterArea
#functions for reading and writing excel sheets

'''
iterate over radius column
for each cell, associate to it
    1. the date, block, and zone cells in the same row
    2. the result cell in the "maximum cluster area" column
'''

filepath = "Excel Files\Kajiado Data v1.xlsx"
kaj = pxl.load_workbook(filepath)
kaj1 = kaj[kaj.sheetnames[0]]

#for each column, makes a dictionary entry of the value of the 1st row, and the rest of the cells
def getCols(sheet):
    cols = {}
    for col in sheet.iter_cols():
        title = col[0].value #whatever type col[0].value is, probably a string
        cols[title] = col[1:] #the non-first elements of the column, skipping the title
    return cols

def getAreasOfActualClusters():
    pass


def applyMaxClusterArea():
    columns = getCols(kaj1)

    def assocCells(colName, dataCols, resultCol):
        #string, [string], string
        results = []
        for cell in columns[colName]:
            rowNum = cell.row - 2
            results.append([cell,[columns[name][rowNum].value for name in dataCols], columns[resultCol][rowNum]])
        return results

    stuff = assocCells("fixed radius", ["Date","Zone","Grazing Block"],"max cluster area")

    groupedRows = [list(grp) for k, grp in
        groupby(stuff, lambda c: c[1])]

    print("There are",len(groupedRows),"groups")

    doit()
    saveit()

    def doit():
        for g in groupedRows:
            try:
                radii = [el[0].value for el in g]
                if None in radii:
                    mcArea = None
                elif 0 in radii:
                    nonzeroRadii = [r for r in radii if r != 0]
                    if nonzeroRadii == []:
                        mcArea = None
                    else:
                        mcArea = maxClusterArea(nonzeroRadii)
                else:
                    mcArea = maxClusterArea(radii)

                for cell in [el[2] for el in g]:
                    cell.value = mcArea

                print("Finished group")
            except:
                print(g)
                sys.exit(0)
        print("Finished all the groups")

    def saveit():
        resultpath = "Excel Files\Kajiado Data Results.xlsx"
        kaj.save(resultpath)
