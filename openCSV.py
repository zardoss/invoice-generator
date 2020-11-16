import os
import sys
import csv
import operator
import shutil
import typer
from tempfile import NamedTemporaryFile
from collections import defaultdict

# Name of file we're reading from
temp_file = NamedTemporaryFile(mode="w+", delete=False)
# Creates an empty dictionary to store data ready for new file
d = defaultdict(lambda: [])

def reformatCSVData(filename):
    print("[*]\tStage 1 - reformat the data from " + filename)
    # -- STAGE 1 -- Merging duplicate entries based on name.
    with open(filename, newline='') as f:
        reader = csv.reader(f, delimiter=',')
        # Stores CSV data to a list: data
        data = list(reader)
        # Deletes the headers that are always at the beginning of the list
        # TODO: Can't always rely on CSV file having headers... Maybe find alternative solution to checking for them / dealing with them
        del data[0]
        # For every row/line of info in data.csv file
        for line in data:
            
            # Append data to dictionary using line[0] as a key.
            d[line[0]].append({
                "name": line[0],
                "date": line[3],
                "items" : "{\"name\":\"" + line[3] + " - " + line[1] + "\", \"quantity\":" + line[2] + ", \"unit_cost\":" + line[4] + "}"
            })

def writeNewDataToFile(filename, newFileName):
    # -- STAGE 2 -- To write new data to CSV file...
    print("[*]\tStage 2 - Write newly formatted data to " + newFileName)
    with open(filename, "r") as csvfile, temp_file:
        # Headers for new CSV file
        fieldnames = ['name','date','items']
        # Will be writing to a temp_file csv using the fieldnames above
        writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
        # Write headers
        writer.writeheader()

        # For each unique name, write their order to file
        for name in sorted(d.keys()):
            counter = 0
            everyorder = ""
            for order in d[name]:
                counter += 1
                if name == order['name']:
                    # Correctly formats the items column in list[dict] format
                    if counter == len(d[name]) and len(d[name]) != 1:
                        everyorder += order['items'] + "]"
                    elif counter == 1 and len(d[name]) != 1:
                        everyorder += "[" + order['items'] + ","
                    elif len(d[name]) == 1:
                        everyorder += "[" + order['items'] + "]"
                    else:
                        everyorder += order['items'] + ","

            # Writes each row of new CSV file
            writer.writerow({
                        'name': order['name'],
                        'date': order['date'],
                        'items': everyorder
                    })
        try:
            # Creates new CSV file with written info from above
            shutil.move(temp_file.name, newFileName)
            print("[*]\tSuccessfully saved file")
        except:
            # Will print this if unsuccessful
            print("File not saved fucker")
        
def main(csv_name: str = typer.Argument('invoices.csv')):
    print("[*]\tStarting CSV formatter")
    # If no csv file is given to program, shut down.
    if len(sys.argv) == 1:
        print("[*]\tWe'll get 'em next time")
        print("[*]\tShutting down CSV formatter")
        exit()
    # File names
    filename = csv_name
    newFileName = "reformatted_" + filename
    # Reformats the simple csv file data so I can create invoices
    reformatCSVData(filename)
    # Writes the data in a more complicated format to a new file
    writeNewDataToFile(filename, newFileName)
    print("[*]\tShutting down CSV formatter")

if __name__ == "__main__":
    typer.run(main)