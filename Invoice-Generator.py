from sys import platform
from sys import exit
import os
from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fdialog
from tkinter import Label
import requests
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
        master.wm_iconbitmap('ig_logo.ico')
        master.title("Invoice Generator V1.0 - Cal")
        master.config(bg=backgroundColour)
        # master.resizable(width=False, height =False)
        
        # ---- Screen Properties ---- #
        app_width = 350
        app_height = 400
        # Resize buttons
        widthbtn = int(app_width*0.5)
        heightbtn = int(app_height*0.1)
        if windows: 
            # Resize buttons to cater for windows weird ways
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
        frame.config(height=app_height, width=app_width,  bg = backgroundColour)
        # frame.config(highlightbackground="black", highlightthickness=3)
        frame.pack(padx = app_width*0.05, pady= app_height*0.05)
        
        # Threading related variables
        self.threadLock = threading.Lock()

        # Variables
        self.filename = ""
        self.my_progress = {'value': 0}
        self.percentageComplete = 0
        self.complete = 0
        self.totalInvoices = 0
        self.fakeTotal = 0
        self.timeout = 5

        # ---- Buttons ---- #
        # Lambda reference: https://stackoverflow.com/questions/6920302/how-to-pass-arguments-to-a-button-command-in-tkinter
        self.chooseFile = Button(frame, text="Select your spreadsheet", bg="white", command=lambda: self.selectFile(master))
        self.generate= Button(frame, text="Generate Invoices!", bg="white", command=self.generateInvoices)
        self.exitProgram = Button(frame, text="Exit", bg="yellow", fg="black", command=exit)
            # Set buttons sizes
        self.chooseFile.config(width = widthbtn, height = heightbtn)
        self.generate.config(width = widthbtn, height = heightbtn)
        self.exitProgram.config(width = int(widthbtn*0.6), height = int(heightbtn*0.6))

        # ---- Progress Bar ---- #
        self.my_progress = ttk.Progressbar(frame, orient=HORIZONTAL, length=app_width-(app_width*0.2), mode = 'determinate')
        self.progress_label = Label(frame, text=f"{self.percentageComplete}%", bg = backgroundColour)
        
        # ---- Labels ---- #
        self.stepOne = Label(frame, text="Step 1. Select your spreadsheet containing ALL \norders from the past 2 weeks", bg = backgroundColour, padx = 5,pady=5)
        self.stepTwo = Label(frame, text="Step 2. Click \"Generate Invoices\" \nto generate the invoices", bg = backgroundColour, pady=10)
        self.whichDirectory = "No file selected"
        self.currentlySelected = Label(frame, text=f"File: {self.whichDirectory}", background = "yellow")
        self.internetStatus = Label(frame, text = "Loading...")
        # Check what stage user is at
        self.stage = Label(frame)
        self.currentStage(1)
        
        # ---- Position tkinter GUI elements (place) ---- #
        self.stepOne.place(relx = 0.5, rely = 0.08, anchor=CENTER, bordermode=INSIDE)
        self.chooseFile.place(relx=0.5, rely = 0.2, anchor=CENTER)
        self.currentlySelected.place(relx = 0.25, rely = 0.3, anchor = CENTER)
        self.internetStatus.place(relx = 0.75, rely = 0.3, anchor = CENTER)
        self.stepTwo.place(relx = 0.5, rely = 0.45, anchor=CENTER, bordermode=INSIDE)
        # ---- Progress bar / label
        self.my_progress.place(width = 200, relx = 0.46, rely = 0.55, anchor=CENTER)
        self.progress_label.place(relx = 0.85, rely = 0.55, anchor=CENTER)
        # ---- Generate Button
        self.generate.place(relx = 0.5, rely = 0.65, anchor = CENTER)
        self.stage.place(relx = 0.5, rely = 0.75, anchor = CENTER)
        self.exitProgram.place(relx = 0.5, rely = 0.9, anchor=CENTER)

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
                    self.currentStage(2)
                except Exception as e:
                    print(f"[*]\tFail\t{e}")
            # Check if it's an excel file
            else:
                print(f"Not sure what format this is...\"{self.filename}\"")

    def generateInvoices(self):
        self.currentStage(3)
        csv_reader = g.CSVParser(self.filename)
        array_of_invoices = csv_reader.get_array_of_invoices()
        print(f"[*]\tGenerating invoices from : {self.filename}")
        self.totalInvoices = len(array_of_invoices)
        self.counter = 0
        totalLitres = 0
        unitCost = 0
        totalDolla = 0
        thread_list = []

        for invoice in array_of_invoices:
            for item in invoice.items:
                totalLitres += item['quantity']
                unitCost = item['unit_cost']
                totalDolla += (totalLitres*unitCost)
        
        self.fakeTotal = len(array_of_invoices)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(self.generateOneInvoice, array_of_invoices)
            try:
                while self.complete < self.fakeTotal:
                    with self.threadLock:
                        self.step(len(array_of_invoices), self.complete)
                        print(f"{self.complete}/{self.fakeTotal}")
                    time.sleep(1)
            except Exception as e:
                print(f"Error >> {e}")
                print(f"{self.complete} / {len(array_of_invoices)} invoices generated")
            
        print(f"[*]\tTotals:\t {totalLitres} Litres\t £{totalLitres*1.45}")
        if self.complete >= len(array_of_invoices) and self.fakeTotal == len(array_of_invoices):
            print("[*]\tAll invoices have been successfully generated!")
            self.currentStage(4)
            self.master.update_idletasks()
        elif self.complete >= self.fakeTotal and self.fakeTotal < len(array_of_invoices):
            print(f"[*]\tSome invoices were generated... {self.complete}/{len(array_of_invoices)}")
            self.currentStage(5)
            self.master.update_idletasks()

    def checkInternetConnection(self):
        try:
            request = requests.get("https://www.google.com", timeout=self.timeout)
            # print("[*]\tInternet Connection : Estabilished")
            return True
        except (requests.ConnectionError, requests.Timeout) as exception:
            # print("[*]\tInternet Connection : Failed")
            return False
    def invoiceGenerationStatus(self):
        percentageComplete = 0
        if self.totalInvoices > 0:
            percentageComplete = self.totalInvoices/self.complete

        return percentageComplete

    def currentStage(self, stageNo):
        # Stages
        # Stage 1 - Awaiting file selection
        # Stage 2 - File ready - Press generate
        # Stage 3 - Generating invoices...
        # Stage 4 - Finishes generating invoices.
        if stageNo == 1:
            self.stage.config(text="Awaiting File...", bg="orange")
        elif stageNo == 2:
            self.stage.config(text="File is ready - Press Generate!", bg = "lightgreen")
        elif stageNo == 3:
            print("stage 3")
            self.stage.config(text="Generating Invoices...", bg = "yellow")
        elif stageNo == 4:
            self.stage.config(text="Finished generating invoices!", bg="green")
        elif stageNo == 5:
            self.stage.config(text="Finished generating some of the invoices...", bg="maroon")

        self.master.update_idletasks()

    def generateOneInvoice(self, invoice):
        print(f"[*] Generating Invoice for {invoice.name}")
        # try:
        try:
            g.main(invoice)
            with self.threadLock:
                self.complete += 1
        except:
            print(f"Error >> {e}")
            self.fakeTotal -= 1
            # except Exception as e:
                # print(f"Error >> {e}")
                # print(f"{self.complete} / {len(array_of_invoices)} invoices generated")
        # except:
        #     print("[*]\tFailed to generate invoice for {invoice.name}")

    def testStep(self, invoice_total, invoices_done):
        if invoice_total > 0:
            # try:
            self.master.after(500, self.step(invoice_total, invoices_done))
            # except Exception as e:
            #     print(e)
        else:
            print("give vals")

    def step(self, invoice_total, invoices_done):
        # print(f"{invoices_done} / {invoice_total}")

        # if self.my_progress['value'] == 100:
            # print("done")
        # else:
        try:
            self.percentageComplete = round((invoices_done / invoice_total)*100, 2)
        except Exception as e:
            print(f"Error >> {e}")
        # Update progress bar val
        try:
            self.my_progress['value'] = self.percentageComplete
        except Exception as e:
            print(f"Error >> {e}")
        # Update label val
        try:
            self.progress_label.config(text=f"{self.percentageComplete}%")
        except Exception as e:
            print(f"Error >> {e}")
        
        try:
            self.master.update_idletasks()
        except:
            print(f"Error >> {e}")

    def task(self):
        print("Checking in background")
        # Checks if internet connection is good
        if self.checkInternetConnection is False:
            self.internetStatus.config(text=" Internet : Disconnected ", bg = "red")
        else:
            self.internetStatus.config(text=" Internet : Connected ", bg = "lightgreen")

        # print(f"{self.invoiceGenerationStatus}")
        percentageComplete = self.invoiceGenerationStatus()
        if  percentageComplete > 0:
            self.progress_label.config(text=f"{self.invoiceGenerationStatus}")

        self.master.update_idletasks()
        self.master.after(5000, self.task)

root = Tk()
e = InvoiceGUI(root)
root.after(2000, e.task)
root.mainloop()