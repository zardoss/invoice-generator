import os
from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fdialog
import time
# Import my own scripts
import openCSV as o
import generateInvoices as g
from openCSV import main

# Fixes GUI issues for macosx - https://pypi.org/project/tkmacosx/
from tkmacosx import Button, ColorVar, Marquee, Colorscale

csvDirectory = ""
excelDirectory = ""

def csvFile():
    print("Selecting CSV file")
    # Current directory
    currdir = os.getcwd()
    tempdir = fdialog.askopenfilename(parent=root, initialdir=currdir, title='Please open your csv file', filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
    
    if len(tempdir) > 0:
        global csvDirectory
        csvDirectory = os.path.basename(tempdir)
        # print(f"\"{csvDirectory}\"")
        try:
            o.main(csvDirectory)
            global whichDirectory
            whichDirectory = csvDirectory
            csvDirectory = "reformatted_" + csvDirectory
            print("great success")
            frame.update_idletasks()
        except:
            print("fail")
    
# TODO: convert excel to csv
def excelFile():
    print("Excel File")

def generateInvoices():
    # print(f"{csvDirectory}")
    if len(csvDirectory) > 0:
        # print(f"Generating invoices for {csvDirectory}")
        step()
        g.main(csvDirectory)
    else:
        print("No file selected. Can't generate invoices")

def step():
    print("lol")
    # my_progress['value'] = 20
    # progress_label.config(text=my_progress['value'])
    # frame.update_idletasks()
    # time.sleep(1)
        

root = Tk()
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
subMenu.add_command(label="CSV File", command=csvFile)
subMenu.add_command(label="Excel File", command=excelFile)
subMenu.add_separator()
subMenu.add_command(label="Exit", command=exit)

# ---- Text ---- #
welcometext = "Invoice Generator V1.0 - Cal"

# ---- Labels ---- #

welcome = Label(frame, text=welcometext, height=2).grid(row=0)

whichDirectory = csvDirectory
if len(csvDirectory) == 0:
    whichDirectory = "nothing selected"

currentlySelected = Label(frame, text=f"File: {whichDirectory}").grid(row = 2)

# ---- Buttons ---- #
selectCSV = Button(frame, text="Select your spreadsheet", bg="white", command=csvFile)
generate= Button(frame, text="Generate Invoices!", bg="white", command=generateInvoices)

selectCSV.grid(row = 1)
generate.grid(row = 4)

# ---- Progress Bar ---- #
my_progress = ttk.Progressbar(frame, orient=HORIZONTAL, length=app_width-(app_width*0.2), mode = 'determinate')
my_progress.grid(row = 5,column=0)

progress_label = Label(frame, text="").grid(row = 5, column=1)

frame.pack()
root.mainloop()