import os
import sys
import csv
import operator
import shutil
from tempfile import NamedTemporaryFile

# Name of file we're reading from
filename = "data.csv"
temp_file = NamedTemporaryFile(mode="w+", delete=False)

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

    for row in data:
        # Stores every element of every row from data
        every = [rw for rw in data if rw[0] == row[0]]

        # Resets the string for each new name
        finaloutput = ""
        
        # every[0]    - each row
        # every[0][0] - names
        # every[0][1] - product
        # every[0][2] - amount
        # every[0][3] - date
        # every[0][4] - unit_cost

        # If name is already in the list 'names'
        # Append the required attributes from the row repeating the name to the row where the first instance of the name.
        # print("Is " + every[0][0] + "in names")
        counter = 0
        if every[0][0] in names:
            for name in every:
                counter += 1
                if counter == 1:
                    # This appends at the beginning of the final output entry
                    finaloutput += "{\"name\": \"" + every[0][3] + " - " + every[0][1] + "\", \"quantity\": " + every[0][2] + ", \"unit_cost\":" + every[0][4] + "}"
                if counter > 1:
                    finaloutput += ", {\"name\": \"" + every[0][3] + " - " + every[0][1] + "\", \"quantity\": " + every[0][2] + ", \"unit_cost\":" + every[0][4] + "}"
            # When skipping the rest of this for loop, it moves to the next name/row in the list rather than check if the name that repeated here has repeated more than 2 times.

        if every[0][0] is not names:
            # Appends every name from data (should only happen once)
            names.append(every[0][0])
            continue
        
        print(finaloutput)
        # Appends the necessary string format of data from the data csv file to freshoutput. The order these are appended correlates with the order the names are stored.
        freshoutput.append(finaloutput)
        counter = 0

    # Print every element in names
    for name in freshoutput:
        print(name)


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