import os
from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fdialog
import pandas as pd
import threading
import time
import json
import csv
import xlrd
# Import my own scripts
import openCSV as o
import generateInvoices as g
from openCSV import main

# Fixes GUI issues for macosx - https://pypi.org/project/tkmacosx/
from tkmacosx import Button, ColorVar, Marquee, Colorscale

filename = ""
excelDirectory = ""
my_progress = {'value': 0}

def selectFile():
    print("Selecting CSV/Excel file")
    # Current directory
    currdir = os.getcwd()
    tempdir = fdialog.askopenfilename(parent=root, initialdir=currdir, title='Please open your csv file', filetypes=(("excel files", "*.xlsx"),("csv files", "*.csv"), ("all files", "*.*")))
    
    # If file is selected
    if len(tempdir) > 0:
        global filename
        # Store file name to filename
        filename = os.path.basename(tempdir)
        if filename.endswith(".xlsx"):
            print(f"[*]\tConverting excel spreadsheet to csv")
            # Read and store content of the excel file 
            df = pd.read_excel(filename)  # sheetname is optional
            filename = f"{filename}.csv"
            # Write the dataframe object into csv file 
            df.to_csv(filename, index=False)  # index=False prevents pandas to write row index
        # Check if it's a csv file
        if filename.endswith(".csv"):
            print("[*]\tCSV File selected")
            try:
                o.main(filename)
                global whichDirectory
                whichDirectory = filename
                root.update_idletasks()
                filename = "reformatted_" + filename
                print("[*]\tgreat success")
            except:
                print(f"[*]\t\t\tfail")
        # Check if it's an excel file
        else:
            print(f"Not sure what format this is...\"{filename}\"")

def generateInvoices():
    csv_reader = g.CSVParser(filename)
    array_of_invoices = csv_reader.get_array_of_invoices()
    print(f"[*]\tGenerating invoices from : {filename}")
    nInvoices = len(array_of_invoices)
    counter = 0
    totalLitres = 0
    unitCost = 0
    totalDolla = 0

    for invoice in array_of_invoices:
        counter += 1
        totalLitres += invoice.items[0]['quantity']
        unitCost = invoice.items[0]['unit_cost']
        totalDolla += (totalLitres*unitCost)
        try:
            step(nInvoices, counter)
            generateOneInvoice(invoice)
        except:
            print("couldn't step")

        if counter == nInvoices:
            print(f"[*]\tTotals:\t {totalLitres} Litres\t £{totalLitres*1.45}")
            print("[*]\tAll invoices have been successfully generated!")

def generateOneInvoice(invoice):
    g.main(invoice)

def testStep():
    step(20, 1)

def step(invoice_total, invoices_done):
    if my_progress['value'] == 100:
        print("done")
    else:
        my_progress['value'] += (invoices_done / invoice_total)*100
        progress_label.config(text=f"{str(int(my_progress['value']))}%")
        frame.update_idletasks()
        time.sleep(0.1)

# Starts window above all then allows it to fall to background if done so by user    
def raise_above_all(window):
    window.lift()
    window.attributes('-topmost',True)
    window.after_idle(root.attributes,'-topmost',False)

root = Tk()
raise_above_all(root)
root.title("Invoice Generator V1.0 - Cal")

frame = Frame(root)
# ---- Screen Properties ---- #

app_width = 350
app_height = 400

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Centers the app to the screen
x = (screen_width/2) - (app_width/2)
y = (screen_height/2) - (app_height/2)
root.geometry(f"{app_width}x{app_height}+{int(x)}+{int(y)}")

# ---- Main Menu ---- #
menu = Menu(root)
root.config(menu=menu)

    # -- Import -- #
subMenu = Menu(menu)
menu.add_cascade(label="Import", menu=subMenu)
subMenu.add_command(label="CSV File", command=selectFile)
subMenu.add_separator()
subMenu.add_command(label="Exit", command=exit)

# ---- Text ---- #
welcometext = "Invoice Generator V1.0 - Cal"

# ---- Labels ---- #

welcome = Label(frame, text=welcometext, height=2).grid(row=0)

whichDirectory = filename
if len(filename) == 0:
    whichDirectory = "nothing selected"

currentlySelected = Label(frame, text=f"File: {whichDirectory}").grid(row = 2)

# ---- Buttons ---- #
selectCSV = Button(frame, text="Select your spreadsheet", bg="white", command=selectFile)
# generate= Button(frame, text="Generate Invoices!", bg="white", command=threading.Thread(target=generateInvoices).start())
generate= Button(frame, text="Generate Invoices!", bg="white", command=generateInvoices)
exitButton = Button(frame, text="click to exit", bg="orange", command=exit)
testButton = Button(frame, text="test", bg= "red", command=testStep)

selectCSV.grid(row = 1)
generate.grid(row = 4)
exitButton.grid(row = 6)
testButton.grid(row = 7)

# ---- Progress Bar ---- #
my_progress = ttk.Progressbar(frame, orient=HORIZONTAL, length=app_width-(app_width*0.2), mode = 'determinate')
my_progress.grid(row = 5)

progress_label = Label(frame, text="0%")
progress_label.grid(row = 8)

frame.pack()
root.mainloop()