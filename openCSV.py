import os
import sys
import csv
import operator
import shutil
from tempfile import NamedTemporaryFile

# Name of file we're reading from
filename = "CSV/data.csv"
temp_file = NamedTemporaryFile(mode="w+", delete=False)
print("[*]\tStarting CSV conversion")
# -- STAGE 1 -- Merging duplicate entries based on name.
with open(filename, newline='') as f:
    dataCSV = csv.reader(f, delimiter=',')
    # Sorts the data to order alphabetically in name column
    reader = sorted(dataCSV, key=operator.itemgetter(0))
    # Stores CSV data to a list: data
    data = list(reader)
    # names stores each name from the data without repeating it
    freshoutput, names = [], []
    
    finaloutput = ""
    counter = 0
    for row in data:
        counter += 1
        # Stores every element of every row from data
        every = [rw for rw in data if rw[0] == row[0]]
        # Resets the string for each new name
        finaloutput = ""

        if every[0][0] in names:
            # When skipping the rest of this for loop, it moves to the next name/row in the list rather than check if the name that repeated here has repeated more than 2 times.
            finaloutput += ", {\"name\": \"" + every[0][3] + " - " + every[0][1] + "\", \"quantity\": " + every[0][2] + ", \"unit_cost\":" + every[0][4] + "}"
            continue

        # This appends at the beginning of the final output entry
        finaloutput += "{\"name\": \"" + every[0][3] + " - " + every[0][1] + "\", \"quantity\": " + every[0][2] + ", \"unit_cost\":" + every[0][4] + "}"
        # Appends every name from data (should only happen once)
        names.append(every[0][0])
        
        print("[" + str(counter) + "]\t" + finaloutput)
        # Appends the necessary string format of data from the data csv file to freshoutput. The order these are appended correlates with the order the names are stored.
        freshoutput.append(finaloutput)

    # Print every element in names
    for name in freshoutput:
        print("[*]\t" + name)

print("[*]\tEnding CSV conversion")

# # -- STAGE 2 -- To write new data to CSV file...
# with open(filename, "r") as csvfile, temp_file:
#     # Will be reading from the simple csv file
#     reader = csv.DictReader(csvfile)
#     # fieldnames for new CSV file
#     fieldnames = ['name','date', 'items']
#     # Will be writing to a temp_file csv using the fieldnames above
#     writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
#     # Writes column headers
#     writer.writeheader()
#     # For every row in csvfile
#     for row in reader:
#         # write each new row
#         writer.writerow({
#             'name': row['name'],
#             'date': row['date'],
#             # Want to write the items column according to the appropriate name.
#             'items': "name"
#             # 'items': '[{\"name\":\"' + row['date'] +  " - " + row['product'] + "\",\"quantity\":" + row['amount'] + ", \"unit_cost\"" + row["unit_cost"] + "}]"
#         })
#     shutil.move(temp_file.name, "USETHIS.csv")