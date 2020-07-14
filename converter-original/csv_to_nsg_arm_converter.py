""" This program converts a CSV or Excel file to a Network Security Group (NSG) Azure Resource Manager (ARM) Template. """

#### CSV to NSG-ARM-Template Converter || Written by: Alex Helvaty || Created: 6/1/18 || Modified: 6/25/18

### JSON validator to verify output format : https://jsonformatter.curiousconcept.com/

### Table of Contents:
## 25 - 109  | Program Modules, Input, Constants, Variables
## 112 - 127 | Input File Extension Based Controller/Switch
## 130 - 163 | EXCEL to CSV Converter
## - 137 - 158 | CSV MODIFIER (of Newly Output CSV)
## 166 - 211 | CSV to JSON Converter
## - 178 - 190 | Modification of "Name" Object Key for Alphabetical Sort
## - 197 - 201 | Alphabetizing of Object Keys
## 214 - 419 | JSON Manipulator
## 421 - 447 | JSON Filter

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


### Input File Extension Based Controller/Switch
## IF statement that determines if a .csv, .xls(x), or alternate file type has been input and continues or exits the program based on input
EXCEL_EXTENSIONS = ['.xls', '.xlsx']
splitName = os.path.splitext(CL_INPUT_FILE)[0]
splitExt = os.path.splitext(CL_INPUT_FILE)[1]
## if input file is a CSV, the program continues
if splitExt == '.csv':
    wasExcelInput = False
    print("\nNice! It's a CSV already!!! :D Onward!\n...\n")
## if the input file is an Excel Spreadsheet, the program terminates - support coming soon
elif splitExt in EXCEL_EXTENSIONS:
    wasExcelInput = True
    print("\nAyyyyy, we can convert Excel files to CSV files. I mean it takes a little bit more work. But, that's just how dedicated we are to making you happy. Onward!!\n...\n...\n...\n")
else:
    print("\nSorry, we don't accept files with the " + splitExt + " extension/format yet. Input a CSV, though, and we'll get convertin' for ya.\n")
    exit()


### EXCEL TO CSV
## if CL_INPUT_FILE is formatted as an Excel file, it is converted to a CSV
if wasExcelInput:
    excelDocument = CL_INPUT_FILE
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


### CSV TO JSON ###
## converts CSV to JSON and sorts "name" object key to 1st position
with open(CL_INPUT_FILE) as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    sorted_rows = rows
## removes the unneeded CSV file from the disk IF the input file was NOT a CSV
if splitExt != ".csv":
    os.remove(CL_INPUT_FILE)
with open(WORK_FILE_JSON, 'w') as f:
    json.dump(rows, f, sort_keys=True, indent=4, separators=(',', ': '))

## moves the line with the 'name' object to the beginning of each section
with open(WORK_FILE_JSON, 'r') as f1, open(TEMP_FILE_JSON, 'w') as f2:
    for line in f1:
        if line.split(":")[0].lower().find(NAME.lower()) > -1:
            newLine = line
            lineList = newLine.split(":")
            print(lineList)
            lineList[1] = lineList[1].lstrip()
            filterObjectName = lineList[0].split('\"', 1)
            filterObjectName[1] = '\"' + "1Aa" + NAME + '\"'
            lineList[0] = filterObjectName[0] + filterObjectName[1]
            f2.write(lineList[0] + ": " + lineList[1])
        else:
            f2.write(line)
            print("else")
            print(line)

## To prevent WinError 32 on Windows OS - remove WORK_FILE_JSON from disk
os.remove(WORK_FILE_JSON)
## - then rename TEMP_FILE_JSON (modified data from WORK_FILE_JSON) as WORK_FILE_JSON
os.rename(TEMP_FILE_JSON, WORK_FILE_JSON)

## sort the object keys alphabetically in the json file
with open(WORK_FILE_JSON) as dataFile:
    JSON_TO_BE_SORTED = json.load(dataFile)
    with open(TEMP_FILE_JSON, 'w') as tempJson:
        json.dump(JSON_TO_BE_SORTED, tempJson, sort_keys=True, indent=4, separators=(',', ': '))

## To prevent WinError 32 on Windows OS - remove WORK_FILE_JSON from disk
os.remove(WORK_FILE_JSON)
## - then rename TEMP_FILE_JSON (modified data from WORK_FILE_JSON) as WORK_FILE_JSON
os.rename(TEMP_FILE_JSON, WORK_FILE_JSON)

## rename input file to newly created and sorted json file for further modification
CL_INPUT_FILE = WORK_FILE_JSON

CL_OUTPUT_FILE = TEMP_FILE_JSON
sys.exit("Error message")

#### JSON MANIPULATION/FORMATTING ####
with open(CL_INPUT_FILE, 'r') as f1, open(CL_OUTPUT_FILE, 'w') as f2:
    ## writes the first 11 static lines to file
    f2.write(STATIC_BEGINNING)
    ## checks each line for specific criteria and either modifies and writes or writes as is to new file
    for line in f1:
        if line.find("[\n", 0, 2) > -1:
            f2.write(line)
        elif line == "]" or line == "]\n":
            if line == "]":
                f2.write(FOUR_TABS + line + "\n")
            else:
                f2.write(FOUR_TABS + line)
        ## formats the squiggly brackets
        elif line.find("    {") > -1 or line.find("]") > -1:
            f2.write(FOUR_TABS + line)
        elif line.find("    },") > -1 or line.find("    }") > -1:
            f2.write(SIX_TABS + "}\n" + FOUR_TABS + line)
        ## finds the "name" line and appends the "properties" line to the end of it
        elif line.split(":")[0].lower().find(NAME.lower()) > -1:
            newLine = line
            lineList = newLine.split(":")
            lineList[1] = lineList[1].lstrip()
            filterObjectName = lineList[0].split('\"', 1)
            filterObjectName[1] = '\"' + NAME + '\"'
            lineList[0] = filterObjectName[0] + filterObjectName[1]
            f2.write(FOUR_TABS + lineList[0] + ": " + lineList[1] + SIX_TABS + PROPERTIES_APPEND)
        ## finds the "priority" line
        elif line.split(":")[0].lower().find(PRIORITY.lower()) > -1:
            newLine = line
            lineList = newLine.split(":")
            lineList[1] = lineList[1].lstrip()
            ## removes the trailing "\n" and ",",
            lineList[1] = lineList[1].rstrip("\n")
            lineList[1] = lineList[1].rstrip(",")
            filterObjectName = lineList[0].split('\"', 1)
            filterObjectName[1] = '\"' + PRIORITY + '\"'
            lineList[0] = ",\n" + FIVE_TABS + filterObjectName[0] + filterObjectName[1]
            ## if the "priority" value is not empty (is a number), then it is stripped of the apostrophes to be read as an integer
            if len(lineList[1]) > 2:
                priority_stripped = lineList[1].replace("\"", "")
                f2.write(lineList[0] + ": " + priority_stripped)
            ## if the "priority" value is empty, then it is written back as just empty apostrophes
            else:
                f2.write(lineList[0] + ": " + lineList[1])
        ## finds the "protocol" line
        elif line.split(":")[0].lower().find(PROTOCOL.lower()) > -1:
            newLine = line
            lineList = newLine.split(":")
            lineList[1] = lineList[1].lstrip()
            ## removes the trailing "\n" and ",",
            lineList[1] = lineList[1].rstrip("\n")
            lineList[1] = lineList[1].rstrip(",")
            filterObjectName = lineList[0].split('\"', 1)
            filterObjectName[1] = '\"' + PROTOCOL + '\"'
            lineList[0] = ",\n" + FIVE_TABS + filterObjectName[0] + filterObjectName[1]
            ## capitalizes the first letter of the "protocol" value
            lineList[1] = lineList[1].title()
            protocolValues = ["\"Tcp\"", "\"Udp\"", "\"*\""]
            if lineList[1] not in protocolValues:
                lineList[1] = "\"*\""
            f2.write(lineList[0] + ": " + lineList[1])
        ## finds the "direction" line
        elif line.split(":")[0].lower().find(DIRECTION.lower()) > -1:
            newLine = line
            lineList = newLine.split(":")
            lineList[1] = lineList[1].lstrip()
            ## removes the trailing "\n" and ",",
            lineList[1] = lineList[1].rstrip("\n")
            lineList[1] = lineList[1].rstrip(",")
            filterObjectName = lineList[0].split('\"', 1)
            filterObjectName[1] = '\"' + DIRECTION + '\"'
            lineList[0] = ",\n" + FIVE_TABS + filterObjectName[0] + filterObjectName[1]
            ## if the "direction" value is valid ("Inbound" or "Outbound"), then it writes it back as read
            if lineList[1].find("Inbound") > -1 or lineList[1].find("Outbound") > -1:
                f2.write(lineList[0] + ": " + lineList[1])
            ## otherwise, it writes it back with just the first letter capitalized
            else:
                lineList[1] = lineList[1].title()
                f2.write(lineList[0] + ": " + lineList[1])
        ## finds the "access" line
        elif line.split(":")[0].lower().find(ACCESS.lower()) > -1:
            newLine = line
            lineList = newLine.split(":")
            lineList[1] = lineList[1].lstrip()
            ## removes the trailing "\n" and ",",
            lineList[1] = lineList[1].rstrip("\n")
            lineList[1] = lineList[1].rstrip(",")
            filterObjectName = lineList[0].split('\"', 1)
            filterObjectName[1] = '\"' + ACCESS + '\"'
            lineList[0] = filterObjectName[0] + filterObjectName[1]
            ## capitalizes the first letter of the "access" value if it is "allow" or "deny"
            if lineList[1].find("allow") > -1 or lineList[1].find("deny") > -1:
                lineList[1] = lineList[1].title()
                f2.write(FIVE_TABS + lineList[0] + ": " + lineList[1])
            ## otherwise, it writes it back as it was originally read from the file
            else:
                f2.write(FIVE_TABS + lineList[0] + ": " + lineList[1])
        ## finds the description line
        elif line.split(":")[0].lower().find(DESCRIPTION.lower()) > -1:
            newLine = line
            lineList = newLine.split(":")
            lineList[1] = lineList[1].lstrip()
            ## removes the trailing "\n" and ",",
            lineList[1] = lineList[1].rstrip("\n")
            lineList[1] = lineList[1].rstrip(",")
            filterObjectName = lineList[0].split('\"', 1)
            filterObjectName[1] = '\"' + DESCRIPTION + '\"'
            lineList[0] = ",\n" + FIVE_TABS + filterObjectName[0] + filterObjectName[1]
        ## if the line contains "sourceAddressPrefix" or "destinationAddressPrefix" or "destinationPortRange" or "sourcePortRange" then a list is created with the name as element 0 and the data as element 1
        elif line.split(":")[0].lower().find(SAP.lower()) > -1 or line.split(":")[0].lower().find(DAP.lower()) > -1 or line.split(":")[0].lower().find(DPR.lower()) > -1 or line.split(":")[0].lower().find(SPR.lower()) > -1:
            newLine = line
            lineList = newLine.split(":")
            lineList[1] = lineList[1].lstrip()
            ## removes the trailing "\n" and ",",
            lineList[1] = lineList[1].rstrip("\n")
            lineList[1] = lineList[1].rstrip(",")
            # lineList[1] = lineList[1][:-2]
            IP_Address_String = lineList[1]
            if IP_Address_String.count(",") > 0 or IP_Address_String.count(";") > 0:
                ## if there is more than one IP Address in the list, then it will pluralize 'Prefix'
                if SAP.lower() in lineList[0].lower():
                    filterObjectName = lineList[0].split('\"', 1)
                    filterObjectName[1] = '\"' + SAP + 'es\": '
                    lineList[0] = filterObjectName[0] + filterObjectName[1]
                elif DAP.lower() in lineList[0].lower():
                    filterObjectName = lineList[0].split('\"', 1)
                    filterObjectName[1] = '\"' + DAP + 'es\": '
                    lineList[0] = filterObjectName[0] + filterObjectName[1]
                elif DPR.lower() in lineList[0].lower():
                    filterObjectName = lineList[0].split('\"', 1)
                    filterObjectName[1] = '\"' + DPR + 's\": '
                    lineList[0] = filterObjectName[0] + filterObjectName[1]
                elif SPR.lower() in lineList[0].lower():
                    filterObjectName = lineList[0].split('\"', 1)
                    filterObjectName[1] = '\"' + SPR + 's\": '
                    lineList[0] = filterObjectName[0] + filterObjectName[1]
                ## if there is more than one IP Address/Port in the list, then the IP Addresses/Ports will be put into a list format
                if IP_Address_String.count(";") == 0:
                    IP_Address_List = IP_Address_String.split(",")
                elif IP_Address_String.count(";") > 0:
                    IP_Address_List = IP_Address_String.split(";")
                i = 0
                IP_Address_List_Range = range(len(IP_Address_List))
                while i in IP_Address_List_Range:
                    IP_Address_List[i] = IP_Address_List[i].strip()
                    IP_Address_List[i] = IP_Address_List[i].strip("\"")
                    IP_Address_List[i] = IP_Address_List[i].strip()
                    if '(' in IP_Address_List[i]:
                        if len(IP_Address_List[i].split(" (")) > 1:
                            IP_Address_List[i] = IP_Address_List[i].split(" (")[0]
                        elif len(IP_Address_List[i].split("(")) > 1:
                            IP_Address_List[i] = IP_Address_List[i].split("(")[0]
                        IP_Address_List[i] = IP_Address_List[i].strip()
                        IP_Address_List[i] = IP_Address_List[i].strip("\"")
                        IP_Address_List[i] = IP_Address_List[i].strip()
                    i += 1
                ## formatting each IP Address/Port in the list
                f2.write(",\n" + FIVE_TABS + lineList[0] + "[")
                for x in IP_Address_List:
                    if x is IP_Address_List[-1]:
                        f2.write("\n" + EIGHT_TABS + "\"" + x + "\"")
                        f2.write("\n" + SEVEN_TABS + "]")
                    elif x is IP_Address_List[0]:
                        f2.write("\n" + EIGHT_TABS + "\"" + x + "\"" + ",")
                    else:
                        f2.write("\n" + EIGHT_TABS + "\"" + x + "\"" + ",")
            else:
                if SAP.lower() in lineList[0].lower():
                    filterObjectName = lineList[0].split('\"', 1)
                    filterObjectName[1] = '\"' + SAP + '\": '
                    lineList[0] = ",\n" + FIVE_TABS + filterObjectName[0] + filterObjectName[1]
                elif DAP.lower() in lineList[0].lower():
                    filterObjectName = lineList[0].split('\"', 1)
                    filterObjectName[1] = '\"' + DAP + '\": '
                    lineList[0] = ",\n" + FIVE_TABS + filterObjectName[0] + filterObjectName[1]
                elif DPR.lower() in lineList[0].lower():
                    filterObjectName = lineList[0].split('\"', 1)
                    filterObjectName[1] = '\"' + DPR + '\": '
                    lineList[0] = ",\n" + FIVE_TABS + filterObjectName[0] + filterObjectName[1]
                elif SPR.lower() in lineList[0].lower():
                    filterObjectName = lineList[0].split('\"', 1)
                    filterObjectName[1] = '\"' + SPR + '\": '
                    lineList[0] = ",\n" + FIVE_TABS + filterObjectName[0] + filterObjectName[1]
                f2.write(lineList[0] + lineList[1])
        else:
            ## if the object key is not referenced above, it is FILTERED out
            print(line)
            if line.find(":") > -1:
                line = ""
                f2.write(line)
                ## if the object key is not referenced above, it still prints it, but CHANGES it to an acceptable format
                ## COMMENT OUT 401 - 403 and UNCOMMENT 406 - 416 if there are more keys (more column headers with values in CSV/spreadsheet)
                # newLine = line
                # lineList = newLine.split(":")
                # lineList[1] = lineList[1].lstrip()
                # ## removes the trailing "\n" and ",",
                # lineList[1] = lineList[1].rstrip("\n")
                # lineList[1] = lineList[1].rstrip(",")
                # filterObjectName = lineList[0].split('\"', 1)
                # downcaseFirstLetter = filterObjectName[1][0].lower() + filterObjectName[1][1:]
                # filterObjectName[1] = '\"' + downcaseFirstLetter
                # lineList[0] = ",\n" + FIVE_TABS + filterObjectName[0] + filterObjectName[1]
                # f2.write(lineList[0] + ": " + lineList[1])
            else:
                f2.write(FIVE_TABS + line)
    f2.write(THREE_TABS + "}\n" + TWO_TABS + "}\n" + "\t" + "]\n" + "}")


#### FILTER ####
## - filters out any objects that do not contain data values within the "securityRules" object
## - specifically checks to see if an object within the "securityRules" object does not have a name (is listed as ' "name": "" ')
##   and if so, removes that object from the "securityRules" object

## opens and loads JSON file
NSG_OBJECTS = json.load(open(CL_OUTPUT_FILE))

## sets range of objects to search
OBJECT_RANGE = range(len(NSG_OBJECTS["resources"][0]["properties"]["securityRules"]))

## applies filter to the "securityRules" objects
i = 0
while i in OBJECT_RANGE:
    if NSG_OBJECTS["resources"][0]["properties"]["securityRules"][i]["name"] == "":
        del NSG_OBJECTS["resources"][0]["properties"]["securityRules"][i]
        OBJECT_RANGE = range(len(NSG_OBJECTS["resources"][0]["properties"]["securityRules"]))
    i += 1

## overwrites newly filtered data back to file
with open(CL_OUTPUT_FILE, 'w') as f:
    json.dump(NSG_OBJECTS, f, sort_keys=True, indent=4, separators=(',', ': '))

## To prevent WinError 32 on Windows OS - remove CL_INPUT_FILE from disk
os.remove(CL_INPUT_FILE)
## - then rename CL_OUTPUT_FILE (modified data from CL_INPUT_FILE) as CL_OUTPUT_FILE
os.rename(CL_OUTPUT_FILE, CL_INPUT_FILE)

#### END ####