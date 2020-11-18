from sys import platform
import os
from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fdialog
from tkinter import Label
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

if platform == "linux" or platform == "linux2":
    print("[*]\tLinux Distrib\t[*]")
    # linux
elif platform == "darwin":
    print("[*]\tMac OS\t[*]")
    # Fixes GUI issues for macosx - https://pypi.org/project/tkmacosx/
    from tkmacosx import Button, ColorVar, Marquee, Colorscale
elif platform == "win32":
    print("[*]\tWindows\t[*]")
    # Windows...

class InvoiceGUI:

    def __init__(self, master):
        backgroundColour = "grey"
        self.master = master
        master.title("Invoice Generator V1.0 - Cal")
        master.config(bg=backgroundColour)

        # ---- Screen Properties ---- #
        app_width = 350
        app_height = 400

        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()

        # Centers the app to the screen
        x = (screen_width/2) - (app_width/2)
        y = (screen_height/2) - (app_height/2)
        master.geometry(f"{app_width}x{app_height}+{int(x)}+{int(y)}")

        # Start in fg
        master.lift()
        master.attributes('-topmost',True)
        master.after_idle(master.attributes,'-topmost',False)
    
        frame = Frame(master)
        frame.config(bg = backgroundColour)
        frame.pack()
        
        # Variables
        self.filename = ""
        self.my_progress = {'value': 0}
        self.percentageComplete = 0

        # ---- Buttons ---- #
        # Lambda reference: https://stackoverflow.com/questions/6920302/how-to-pass-arguments-to-a-button-command-in-tkinter
        self.selectCSV = Button(frame, text="Select your spreadsheet", bg="white", command=lambda: self.selectFile(master))
        self.generate= Button(frame, text="Generate Invoices!", bg="white", command=self.generateInvoices)
        self.exitButton = Button(frame, text="Exit", bg="yellow", fg="black", command=exit)
        self.testButton = Button(frame, text="test", bg= "red", command=lambda: threading.Thread(target=self.testStep, args=(100,1)).start())
        # Resize buttons
        self.selectCSV.config(width = app_width-(app_width*0.2), height = app_height*0.1)
        self.generate.config(width = app_width-(app_width*0.4), height = app_height*0.1)
        self.exitButton.config(width = app_width-(app_width*0.75), height = app_height*0.1)
        # Position buttons
        self.selectCSV.grid(row = 1)
        self.generate.grid(row = 4)
        self.exitButton.grid(row = 6)
        self.testButton.grid(row = 7)

        # ---- Progress Bar ---- #
        self.my_progress = ttk.Progressbar(frame, orient=HORIZONTAL, length=app_width-(app_width*0.2), mode = 'determinate')
        self.progress_label = Label(frame, text=f"{self.percentageComplete}%")
        # Position elements
        self.my_progress.grid(row = 5)
        self.progress_label.grid(row = 8)

        # ---- Labels ---- #
        self.welcome = Label(frame, text="Invoice Generator V1.0 - Cal", height=2)

        self.whichDirectory = self.filename
        if len(self.filename) == 0:
            self.whichDirectory = "nothing selected"
            
        self.currentlySelected = Label(frame, text=f"File: {self.whichDirectory}")
        # Position labels
        self.welcome.grid(row=0)
        self.currentlySelected.grid(row = 2)

        # ---- Main Menu ---- #
        # self.menu = Menu(master)
        # self.master.config(menu=self.menu)

        # -- Import -- #
        # self.subMenu = Menu(menu)
        # self.menu.add_cascade(label="Import", menu=self.subMenu)
        # self.subMenu.add_command(label="CSV File", command=self.selectFile)
        # self.subMenu.add_separator()
        # self.subMenu.add_command(label="Exit", command=exit)
        
    def selectFile(self, master):
        print("Selecting CSV/Excel file")
        # Current directory
        currdir = os.getcwd()
        tempdir = fdialog.askopenfilename(parent=master, initialdir=currdir, title='Please open your csv file', filetypes=(("excel files", "*.xlsx"),("csv files", "*.csv"), ("all files", "*.*")))
        
        # If file is selected
        if len(tempdir) > 0:
            # Store file name to filename
            self.filename = os.path.basename(tempdir)
            if self.filename.endswith(".xlsx"):
                print(f"[*]\tConverting excel spreadsheet to csv")
                # Read and store content of the excel file 
                try:
                    self.df = pd.read_excel(self.filename)  # sheetname is optional
                    # Replaces .xlsx with nothing
                    self.filename = self.filename.replace('.xlsx', '')
                    # Adds .csv extension to name before converting .xlsx file type to .csv
                    self.filename = f"{self.filename}.csv"
                    # Write the dataframe object into csv file 
                    self.df.to_csv(self.filename, index=False)  # index=False prevents pandas to write row index
                except Exception as e:
                    print(e)
            # Check if it's a csv file
            if self.filename.endswith(".csv"):
                print("[*]\tCSV File selected")
                try:
                    o.main(self.filename)
                    self.whichDirectory = self.filename
                    self.master.update_idletasks()
                    self.filename = "reformatted_" + self.filename
                except:
                    print(f"[*]\t\t\tfail")
            # Check if it's an excel file
            else:
                print(f"Not sure what format this is...\"{self.filename}\"")

    def generateInvoices(self):
        csv_reader = g.CSVParser(self.filename)
        array_of_invoices = csv_reader.get_array_of_invoices()
        print(f"[*]\tGenerating invoices from : {self.filename}")
        nInvoices = len(array_of_invoices)
        counter = 0
        totalLitres = 0
        unitCost = 0
        totalDolla = 0
        self.failed = False

        for invoice in array_of_invoices:
            counter += 1
            totalLitres += invoice.items[0]['quantity']
            unitCost = invoice.items[0]['unit_cost']
            totalDolla += (totalLitres*unitCost)
            try:
                # self.step(nInvoices, counter)
                threading.Thread(target=self.step, args = (nInvoices, counter)).start()
                # threading.Thread(self.generateOneInvoice, invoice).start()
                threading.Thread(target=self.generateInvoices, args=(invoice))
                # self.generateOneInvoice(invoice)
            except Exception as e:
                
                self.failed = True
                print(f"Couldn't generate invoice for {invoice.name}\t{e}")
                # return

            if counter == nInvoices and self.failed == False:
                print(f"[*]\tTotals:\t {totalLitres} Litres\t £{totalLitres*1.45}")
                print("[*]\tAll invoices have been successfully generated!")
            elif self.failed == True:
                print("[*]\tInvoices failed to generate")

    def generateOneInvoice(self, invoice):
        g.main(invoice)

    def testStep(self, invoice_total, invoices_done):
        
        if invoice_total > 0:
            # try:
            self.master.after(500, self.step(invoice_total, invoices_done))
            # except Exception as e:
            #     print(e)
        else:
            print("give vals")

    def step(self, invoice_total, invoices_done):
        if self.my_progress['value'] == 100:
            print("done")
        else:
            percentageComplete = (invoices_done / invoice_total)*100
            
            # Update progress bar val
            self.my_progress['value'] = percentageComplete
            # Update label val
            self.progress_label.config(text=f"{percentageComplete}%")
            self.master.update_idletasks()
        # print(f"{my_progress['value']}")
        # time.sleep(1)

        # Test step function
        # self.my_progress['value'] = 20
        # self.master.update_idletasks()
        # time.sleep(3)

        # self.my_progress['value'] = 40
        # self.master.update_idletasks()
        # time.sleep(3)

        # self.my_progress['value'] = 60
        # self.master.update_idletasks()
        # time.sleep(3)

        # self.my_progress['value'] = 75
        # self.master.update_idletasks()
        # time.sleep(3)

        # self.my_progress['value'] = 100
        # self.master.update_idletasks()
        # time.sleep(3)

    # Starts window above all then allows it to fall to background if done so by user    
    # def raise_above_all(window):
    #     window.lift()
    #     window.attributes('-topmost',True)
    #     window.after_idle(window.attributes,'-topmost',False)

root = Tk()
e = InvoiceGUI(root)
root.mainloop()