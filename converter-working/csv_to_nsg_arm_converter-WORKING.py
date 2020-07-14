""" This program converts a CSV or Excel file to a Network Security Group (NSG) Azure Resource Manager (ARM) Template. """

#### CSV to NSG-ARM-JSON-Template Converter || Written by: Alex Helvaty || Created: 6/1/18 || Modified: 6/25/18

### JSON validator to verify output format : https://jsonformatter.curiousconcept.com/

### TO-DO:
## - Filter comma above "access"
## - Organized and useful print statements - or none at all - decide necessity
## - Add True/False variables for formats
## - Uncertain as to plausibility, but:
##   - read files to a variable without opening and writing separate files per editing/manipulating block

## MODULES
import csv
import json
import sys
import os
import pandas as pd

### COMMAND-LINE INPUT
## - File:
CL_INPUT_FILE = sys.argv[1]

## - Name for NSG (internally - within file)
# NSG_NAME_INPUT = sys.argv[2]
NSG_NAME_INPUT = os.path.splitext(CL_INPUT_FILE)[0]

## - Location for NSG:
## Command-Line Input:
# NSG_LOCATION_INPUT = sys.argv[3]
## Location determined automatically based on location of NSG resource group in Azure
NSG_LOCATION_INPUT = "[resourceGroup().location]"

### MASTER FILE
MASTER_FILE = CL_INPUT_FILE

### ACCEPTIBLE LOCATIONS :  Comment out if 
# ACCEPTABLE_LOCATIONS = ["centralus", "westeurope"]
# DEFAULT_LOCATION = "centralus"
## - if the input location is not contained in the ACCEPTIBLE_LOCATIONS list
##   then the NSG_LOCATION_INPUT is assigned to the DEFAULT_LOCATION
# if NSG_LOCATION_INPUT not in ACCEPTABLE_LOCATIONS:
#     NSG_LOCATION_INPUT = DEFAULT_LOCATION

### OBJECT NAMES
ACCESS = "access"
DAP = "destinationAddressPrefix"
DESCRIPTION = "description"
DIRECTION = "direction"
DPR = "destinationPortRange"
NAME = "name"
PRIORITY = "priority"
PROTOCOL = "protocol"
SAP = "sourceAddressPrefix"
SPR = "sourcePortRange"

### FORMATTING CONSTANTS
## - to be appended after "name"
PROPERTIES_APPEND = "\"properties\": {\n"

## - tab shortcuts
TWO_TABS = "\t\t"
THREE_TABS = "\t\t\t"
FOUR_TABS = "\t\t\t\t"
FIVE_TABS = "\t\t\t\t\t"
SIX_TABS = "\t\t\t\t\t\t"
SEVEN_TABS = "\t\t\t\t\t\t\t"
EIGHT_TABS = "\t\t\t\t\t\t\t\t"

### STATIC VARIABLES
## - change the object values in the first 11 lines
SCHEMA_STATIC = "http://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#"
CONTENT_VERSION_STATIC = "1.0.0.0"
TYPE_STATIC = "Microsoft.Network/networkSecurityGroups"
API_VERSION_STATIC = "2017-10-01"
LOCATION_STATIC = NSG_LOCATION_INPUT
NAME_STATIC = NSG_NAME_INPUT

### FILES
fileName = os.path.splitext(CL_INPUT_FILE)[0]
## JSON - TEMPORARY
TEMP_FILE_JSON = fileName + "-temp" + ".json"
## JSON - WORKING
WORK_FILE_JSON = fileName + ".json"
## CSV - TEMPORARY
TEMP_FILE_CSV = fileName + "-temp" + ".csv"
## CSV - WORKING
WORK_FILE_CSV = fileName + ".csv"

## - static lines (1-11) : prepends the constant static lines to the beginning of the JSON file
STATIC_BEGINNING = "{" \
                    + "\n\t\"$schema\": \"" + SCHEMA_STATIC + "\"," \
                    + "\n\t\"contentVersion\": \"" + CONTENT_VERSION_STATIC + "\"," \
                    + "\n\t\"resources\": [" \
                    + "\n\t\t{" \
                    + "\n\t\t\t\"type\": \"" + TYPE_STATIC + "\"," \
                    + "\n\t\t\t\"name\": \"" + NAME_STATIC + "\"," \
                    + "\n\t\t\t\"apiVersion\": \"" + API_VERSION_STATIC + "\"," \
                    + "\n\t\t\t\"location\": \"" + LOCATION_STATIC + "\"," \
                    + "\n\t\t\t\"properties\": {" \
                    + "\n\t\t\t\t\"securityRules\": "



def input_File_Gatekeeper(inputFile):
    """
    IF statement that determines if a .csv, .xls(x), or alternative file type has been input and continues or exits the program (based on the file type input)
    
    Parameters:
    ----------
    inputFile : str
        Path to file
    ----------

    Returns:
    ----------
    Boolean value that determines how the program continues functioning
    ----------
    """

    EXCEL_EXTENSIONS = ['.xls', '.xlsx']
    splitName = os.path.splitext(inputFile)[0]
    splitExt = os.path.splitext(inputFile)[1]
    ## if input file is a CSV, the program continues
    if splitExt == '.csv':
        wasExcelInput = False
        print("\nNice! It's a CSV already!!! :D Onward!\n...\n")
    ## if the input file is an Excel Spreadsheet, the program terminates - support coming soon
    elif splitExt in EXCEL_EXTENSIONS:
        wasExcelInput = True
        print("\nAyyyyy, we can convert Excel files to CSV files. I mean it takes a little bit more work. But that's just how dedicated we are to making you happy. Onward!!\n...\n...\n...\n")
    else:
        print("\nSorry, we don't accept files with the " + splitExt + " extension/format yet. Input a CSV/Excel file and we'll get convertin' for ya.\n")
        exit()
    return:
        wasExcelInput



def excel_TO_CSV(inputFile, wasExcelInput):
    """
    Converts inputFile from Excel to CSV format
    
    Parameters:
    ----------
    inputFile : str
        Path to file
    wasExcelInput : boolean
        Excel file or not
    ----------

    Returns:
    ----------
    Working CSV file for use in rest of program
    ----------
    """

    if wasExcelInput:
        excelDocument = inputFile
        excelData = pd.read_excel(excelDocument, index_col=0)
        excelData.to_csv(WORK_FILE_CSV, encoding='utf-8')
        print("We've successfuly converted your " + splitExt + " file to a .csv. \nFiltering...\n...\n...")
        ### MODIFICATION of CSV:
        ## checks for and removes row of unnamed column headers and empty row(s) preceding the data body
        with open(WORK_FILE_CSV, 'r') as f1, open(TEMP_FILE_CSV, 'w') as f2:
            csvReader = csv.reader(f1)
            csvRowList = list(csvReader)
            rowsToRemove = []
            for row in csvRowList:
                for cell in row:
                    if cell.lower().find("destination") > -1:
                        foundAllPrecedingBadRows = True
                        break
                    else:
                        foundAllPrecedingBadRows = False
                if foundAllPrecedingBadRows:
                    break
                else:
                    rowsToRemove.append(row)
            for row in rowsToRemove:
                csvRowList.remove(row)
            csvWriter = csv.writer(f2)
            csvWriter.writerows(csvRowList)
        print("We are formatted and ready for JSON conversion and manipulation!\n...")
        ## To prevent WinError 32 on Windows OS - remove CSV_UNFILTERED from disk
        os.remove(WORK_FILE_CSV)
        ## - then rename TEMP_FILE_CSV (modified data from CSV_UNFILTERED) as WORK_FILE_CSV
        os.rename(TEMP_FILE_CSV, WORK_FILE_CSV)
        CL_INPUT_FILE = WORK_FILE_CSV

