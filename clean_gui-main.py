import os
import sys
import time
import random
import requests
import threading
from threading import Thread
import pandas as pd
import concurrent.futures
# GUI stuff
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtWidgets, QtCore, QtGui
from clean_gui3 import Ui_MainWindow
from load_screen import Ui_SplashScreen
from PyQt5.QtWidgets import QFileDialog, QGraphicsDropShadowEffect
# Own files
import openCSV as o
import generateInvoices as g

# Global Variables
counter = 0
class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent=parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Drops title bar
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # Drop the shadow effect
        self.ui.shadow = QGraphicsDropShadowEffect(self)
        self.ui.shadow.setBlurRadius(80)
        self.ui.shadow.setXOffset(0)
        self.ui.shadow.setYOffset(0)
        self.ui.shadow.setColor(QColor(0, 0, 0, 60))
        self.ui.dropShadowFrame.setGraphicsEffect(self.ui.shadow)

        # Variables
        self.threadLock = threading.Lock()
        self.filename = ""
        self.my_progress = {'value': 0}
        self.percentageComplete = 0
        self.complete = 0
        self.totalInvoices = 0
        self.fakeTotal = 0
        self.timeout = 5
        self.offset = None
        # Initial checks
        self.initChecks()
        # MOST IMPORTANT FUNCTION IN THIS PROGRAM
        # Assign inspiration background
        self.randomVin()
        # Assigning functions to buttons
        self.ui.button_SelectSpreadsheet.clicked.connect(self.selectFile)
        self.ui.buttton_GenerateInvoices.clicked.connect(self.generateInvoices)
        self.ui.button_Exit.clicked.connect(exit)
        # Update labels
    
    def randomVin(self):
        path = r"Images/"
        random_vin = random.choice([
            x for x in os.listdir(path)
            if os.path.isfile(os.path.join(path, x))
        ])
        if random_vin == ".DS_Store":
            random_vin = random.choice([
                x for x in os.listdir(path)
                if os.path.isfile(os.path.join(path, x))
            ])
        print(f"{path}{random_vin}")
        self.ui.label_logo.setPixmap(QtGui.QPixmap(f"{path}{random_vin}"))
        # threading.Timer(20, self.randomVin).start()

    def selectFile(self):
        print("Selecting CSV/Excel file")
        # Current directory
        filename = QFileDialog.getOpenFileName()
        path = filename[0]
        print(path)
        
        # If file is selected
        if len(path) > 0:
            # Store file name to filename
            self.filename = os.path.basename(path)
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
                    self.ui.label_FileSelected.setText(f"File: {self.filename}")
                    self.ui.label_FileSelected.adjustSize()
                    self.filename = "reformatted_" + self.filename
                except Exception as e:
                    print(f"[*]\tFail\t{e}")
            # Check if it's an excel file
            else:
                print(f"Not sure what format this is...\"{self.filename}\"")

    def getInvoices(self):
        csv_reader = g.CSVParser(self.filename)
        self.array_of_invoices = csv_reader.get_array_of_invoices()
        # print(f"[*]\tGenerating invoices from : {self.filename}")
        self.totalInvoices = len(self.array_of_invoices)
        print(f"Total: {self.totalInvoices}")

    def generateInvoices(self):
        self.getInvoices()
        self.counter = 0
        totalLitres = 0
        unitCost = 0
        totalDolla = 0
        thread_list = []
        self.allInvoices = iter(self.array_of_invoices)
        for invoice in self.array_of_invoices:
            for item in invoice.items:
                totalLitres += item['quantity']
                unitCost = item['unit_cost']
                totalDolla += (totalLitres*unitCost)
        
        self.fakeTotal = len(self.array_of_invoices)
        QtCore.QTimer.singleShot(0, self.nextInvoice)
        os.remove(self.filename)
        print("Done all the shiz")
        # print(f"[*]\tTotals:\t {totalLitres} Litres\t £{totalLitres*1.45}")
        # if self.complete >= len(self.array_of_invoices) and self.fakeTotal == len(self.array_of_invoices):
        #     print("[*]\tAll invoices have been successfully generated!")
        # elif self.complete >= self.fakeTotal and self.fakeTotal < len(self.array_of_invoices):
        #     print(f"[*]\tSome invoices were generated... {self.complete}/{len(self.array_of_invoices)}")

    def nextInvoice(self):
        try:
            self.invoice = next(self.allInvoices)
            self.step(len(self.array_of_invoices), self.complete)
        except StopIteration:
            return
        self.generateOneInvoice(self.invoice)
        QtCore.QTimer.singleShot(0, self.nextInvoice)

    def generateOneInvoice(self, invoice):
        self.ui.label_about.setText(f"Generating {invoice.name}'s invoice")
        self.ui.label_about.adjustSize()
        print(f"[*] Generating Invoice for {invoice.name}")

        try:
            g.main(invoice)
            with self.threadLock:
                self.complete += 1
        except:
            print(f"Error >> {e}")
            self.fakeTotal -= 1
    
    def step(self, invoice_total, invoices_done):
        if invoices_done == invoice_total:
            self.percentageComplete = 100
        elif invoices_done < invoice_total:
            self.percentageComplete = int((invoices_done / invoice_total)*100)
            print(f"{invoices_done}/{invoice_total}")
        else:
            print(f"{invoices_done}/{invoice_total}")
            return
        # Update progress bar val
        self.ui.progressBar.setValue(self.percentageComplete)
        self.ui.label_progress.setText(f"{self.percentageComplete}%")
        self.ui.label_progress.adjustSize()

    def checkInternetConnection(self):
        try:
            request = requests.get("https://www.google.com", timeout=self.timeout)
            # print("[*]\tInternet Connection : Estabilished")
            return True
        except (requests.ConnectionError, requests.Timeout) as exception:
            # print("[*]\tInternet Connection : Failed")
            return False

    def initChecks(self):
        if self.checkInternetConnection() == False:
            self.ui.label_InternetStatus.setText("Internet: Disconnected")
        else:
            self.ui.label_InternetStatus.setText("Internet: Connected")

        self.ui.label_InternetStatus.adjustSize()    

    # The next three mouse functions handle the window being draggable
    # https://stackoverflow.com/questions/58901806/how-to-make-my-title-less-window-drag-able-in-pyqt5
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.offset = event.pos()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == QtCore.Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.offset)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.offset = None
        super().mouseReleaseEvent(event)

class loadingScreen(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = Ui_SplashScreen()
        self.ui.setupUi(self)

        # Drops title bar
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # Drop the shadow effect
        self.ui.shadow = QGraphicsDropShadowEffect(self)
        self.ui.shadow.setBlurRadius(80)
        self.ui.shadow.setXOffset(0)
        self.ui.shadow.setYOffset(0)
        self.ui.shadow.setColor(QColor(0, 0, 0, 60))
        self.ui.dropShadowFrame.setGraphicsEffect(self.ui.shadow)

        # Timer 
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.progress)
        self.timer.start(10)
        self.show()

        # Initial Text
        self.ui.label_description.setText("<strong>WELCOME</strong> TO MY APPLICATION")

        # Change Texts
        QtCore.QTimer.singleShot(1500, lambda: self.ui.label_description.setText("<strong>LOADING</strong> FUCK ALL CAUSE THIS IS JUST FOR AESTHETICS"))
        # QtCore.QTimer.singleShot(3000, lambda: self.ui.label_description.setText("<strong>LOADING</strong> USER INTERFACE"))

    def progress(self):

        global counter
        # SET VALUE TO PROGRESS BAR
        self.ui.progressBar.setValue(counter)
        # CLOSE SPLASH SCREE AND OPEN APP
        if counter > 100:
            # STOP TIMER
            self.timer.stop()
            # SHOW MAIN WINDOW
            self.main = MainWindow()
            self.main.show()
            # CLOSE SPLASH SCREEN
            self.close()
        # INCREASE COUNTER
        counter += 1

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = loadingScreen()
    w.show()
    sys.exit(app.exec_())


# Helpful links
# https://www.programmersought.com/article/6264704979/ - Helps set up UI
# https://stackoverflow.com/questions/43260595/attributeerror-ui-mainwindow-object-has-no-attribute-setcentralwidget
