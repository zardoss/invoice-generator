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
import concurrent.futures
# Import my own scripts
import openCSV as o
import generateInvoices as g
from openCSV import main

linux, macOS, windows = False, False, False

if platform == "linux" or platform == "linux2":
    linux = True
    print("[*]\tLinux Distrib\t[*]")
    # linux
elif platform == "darwin":
    macOS = True
    print("[*]\tMac OS\t[*]")
    # Fixes GUI issues for macosx - https://pypi.org/project/tkmacosx/
    from tkmacosx import Button, ColorVar, Marquee, Colorscale
elif platform == "win32":
    windows = True
    print("[*]\tWindows\t[*]")

class InvoiceGUI:

    def __init__(self, master):
        backgroundColour = "lightgrey"
        self.master = master
        master.title("Invoice Generator V1.0 - Cal")
        master.config(bg=backgroundColour)
        

        # ---- Screen Properties ---- #
        app_width = 350
        app_height = 400
        # Resize buttons
        widthbtn = int(app_width*0.5)
        heightbtn = int(app_height*0.1)
        if windows: 
            # Resize buttons
            widthbtn = int(app_width*0.08)
            heightbtn = int(app_height*0.005)

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
        # self.testButton = Button(frame, text="test", bg= "red", command=lambda: threading.Thread(target=self.testStep, args=(100,1)).start())
        # Set buttons sizes
        self.selectCSV.config(width = widthbtn, height = heightbtn)
        self.generate.config(width = widthbtn, height = heightbtn)
        self.exitButton.config(width = int(widthbtn*0.6), height = int(heightbtn*0.6))
        # Position buttons
        self.selectCSV.grid(row = 2, padx = 10, pady = 20)
        self.generate.grid(row = 6, pady = 10)
        self.exitButton.grid(row =9, column = 0)
        # self.testButton.grid(row = 6, column = 1)

        # ---- Progress Bar ---- #
        self.my_progress = ttk.Progressbar(frame, orient=HORIZONTAL, length=app_width-(app_width*0.2), mode = 'determinate')
        self.progress_label = Label(frame, text=f"{self.percentageComplete}%", bg = backgroundColour)
        # Position elements
        self.my_progress.grid(row = 5, column = 0)
        self.progress_label.grid(row = 5, column = 1)

        # ---- Labels ---- #
        # self.welcome = Label(frame, text="Invoice Generator V1.0 - Cal", bg = backgroundColour)
        self.step1 = Label(frame, text="Step 1. Select your spreadsheet containing ALL \norders from the past 2 weeks", bg = backgroundColour, pady=5)
        self.step2 = Label(frame, text="Step 2. Click \"Generate Invoices\" to generate the invoices", bg = backgroundColour, pady=10)
        self.whichDirectory = "No file selected"
        self.currentlySelected = Label(frame, text=f"File: {self.whichDirectory}", background = "yellow")
        # Position labels
        # self.welcome.grid(row=0)
        self.step1.grid(row=1)
        self.currentlySelected.grid(row = 3)
        self.step2.grid(row = 4)

    def selectFile(self, master):
        print("Selecting CSV/Excel file")
        # Current directory
        currdir = os.getcwd()
        tempdir = fdialog.askopenfilename(parent=master, initialdir=currdir, title='Please open your csv file', filetypes=(("all files", "*.*"), ("excel files", "*.xlsx"),("csv files", "*.csv")))
        
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
                    self.currentlySelected.config(text=f"File: {self.filename}", bg = "lightgreen")
                    self.master.update_idletasks()
                    self.filename = "reformatted_" + self.filename
                except Exception as e:
                    print(f"[*]\tFail\t{e}")
            # Check if it's an excel file
            else:
                print(f"Not sure what format this is...\"{self.filename}\"")

    def generateInvoices(self):
        csv_reader = g.CSVParser(self.filename)
        array_of_invoices = csv_reader.get_array_of_invoices()
        print(f"[*]\tGenerating invoices from : {self.filename}")
        self.counter = 0
        totalLitres = 0
        unitCost = 0
        totalDolla = 0
        thread_list = []

        for invoice in array_of_invoices:
            totalLitres += invoice.items[0]['quantity']
            unitCost = invoice.items[0]['unit_cost']
            totalDolla += (totalLitres*unitCost)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            # steps = [executor.map(self.step,(len(array_of_invoices), _)) for _ in len(array_of_invoices)]
            results = executor.map(self.generateOneInvoice, array_of_invoices)
        
        if self.counter >= len(array_of_invoices):
            print(f"[*]\tTotals:\t {totalLitres} Litres\t £{totalLitres*1.45}")
            print("[*]\tAll invoices have been successfully generated!")

        # for invoice in array_of_invoices:
        #     totalLitres += invoice.items[0]['quantity']
        #     unitCost = invoice.items[0]['unit_cost']
        #     totalDolla += (totalLitres*unitCost)
        #     # with concurrent.futures.ThreadPoolExecutor() as executor:
        #     #     results = [executor.submit(self.generateOneInvoice, invoice) for invoice in array_of_invoices]
        #     #     thread = executor.submit(self.generateOneInvoice, invoice)
        #     # thread = threading.Thread(target=self.generateOneInvoice, args=(invoice,))
        #     # thread_list.append(thread)

        # for thread in thread_list:
        #     counter += 1
        #     invoiceIndex = thread_list.index(thread)
            
        #     try:
        #         # self.step(nInvoices, counter)
        #         threading.Thread(target=self.step, args = (len(array_of_invoices), counter,)).start()
        #         thread.start()
        #         # thread.join()
        #         # threading.Thread(self.generateOneInvoice, invoice).start()
        #         # threading.Thread(target=self.generateOneInvoice, args=(invoice)).start()
        #         # self.generateOneInvoice(invoice)
        #     except Exception as e:
        #         self.failed = True
        #         print(f"Couldn't generate invoice for {invoiceIndex}: {invoice.name}\t{e}")
        #         # return
    
        #     if counter == len(array_of_invoices) and self.failed == False:
        #         print(f"[*]\tTotals:\t {totalLitres} Litres\t £{totalLitres*1.45}")
        #         print("[*]\tAll invoices have been successfully generated!")
        #     elif self.failed == True:
        #         print("[*]\tInvoices failed to generate")

        # for thread in thread_list:
        #     thread.join()
        

    def generateOneInvoice(self, invoice):
        g.main(invoice)
        self.counter += 1
        # self.step(totalInvoices, 1)

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

root = Tk()
e = InvoiceGUI(root)
root.mainloop()