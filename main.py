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
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QFileDialog, QGraphicsDropShadowEffect, QMessageBox, QShortcut
from GUI_Layout2 import Ui_MainWindow
from load_screen2 import Ui_MainWindow as Ui_SplashScreen
import qtawesome as qta
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
        self.timeout = 5
        self.offset = None
        self.generatingInvoicesComplete = None
        # Initial checks
        self.initChecks()
        # MOST IMPORTANT FUNCTION IN THIS PROGRAM
        self.randomVin()
        # Assigning functions to buttons
        # self.ui.button_SelectSpreadsheet.clicked.connect(self.invoiceGeneratingFinished)
        self.ui.button_GenerateInvoices.clicked.connect(self.startGenerating)
        # self.ui.button_Exit.clicked.connect(exit)
        # Keyboard shortcuts
        self.generateShortcut = QShortcut(QKeySequence('g'), self)
        self.generateShortcut.activated.connect(self.startGenerating)
        self.changeBigVin = QShortcut(QKeySequence('v'), self)
        self.changeBigVin.activated.connect(self.randomVin)
        self.exit_program = QShortcut(QKeySequence('esc'), self)
        self.exit_program.activated.connect(exit)

        # icon name from the qta-browser
        # icon = qta.icon("mdi.close")
        # self.ui.button_exit.setIcon(icon)
        # self.ui.button_exit.clicked.connect(exit)
        # icon = qta.icon("fa.expand")
        # self.ui.button_expand.setIcon(icon)
        # icon = qta.icon("fa5.window-minimize")
        # self.ui.button_minimise.setIcon(icon)

    def randomVin(self):
        path = r"Images/"
        
        random_vin = random.choice([
            x for x in os.listdir(path)
            if os.path.isfile(os.path.join(path, x))
        ])
        while random_vin == ".DS_Store":
            random_vin = random.choice([
                x for x in os.listdir(path)
                if os.path.isfile(os.path.join(path, x))
            ])

        
        random_vin = "kelland.jpg"
        print(f"{path}{random_vin}")
        self.ui.label_logo.setPixmap(QtGui.QPixmap(f"{path}{random_vin}"))
        # threading.Timer(20, self.randomVin).start()

    def startGenerating(self):
        self.generatingInvoicesComplete = False
        self.worker = Worker()
        # Select file.
        self.worker.selectFile()
        # Collects invoices from file
        self.worker.getInvoices()
        # Starts run function
        self.worker.start()
        self.worker.update_fileSelected.connect(self.updateFileSelected)
        self.worker.finished.connect(self.invoiceGeneratingFinished)
        # Passes update_progress value to updateProgress as parameter.
        self.worker.update_progress.connect(self.updateProgress)
        self.worker.update_whichInvoice.connect(self.updateWhichInvoice)
        if self.generatingInvoicesComplete is False:
            self.ui.button_GenerateInvoices.setStyleSheet("background-color: grey")
        else:
            self.ui.label_about.setText(f"<html><head/><body><p><span style=\" font-weight:600;\">Finished generating invoices!</span></p></body></html>")

    def invoiceGeneratingFinished(self):
        self.generatingInvoicesComplete = True
        message = "Invoices have been generated"
        QMessageBox.information(self, "Invoices generated", message)
        
    def updateProgress(self, value):
        self.ui.label_progress.setText(f"{value}%")
        self.ui.progressBar.setValue(value)

    def updateFileSelected(self, text):
        print(f"Updated caption: {text}")
        self.ui.label_FileSelected.setText(f"<html><head/><body><p><span style=\" font-weight:600;\">File:</span>{text}</p></body></html>")
    
    def updateWhichInvoice(self, text):
        self.ui.label_about.setText(f"<html><head/><body><p><span style=\" font-weight:600;\">Generating invoice for:</span>\t{text}</p></body></html>")

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
            # Thread
            self.gi = self.generateOneInvoice(invoice)
            self.generate_thread = QtCore.QThread()
            self.gi.moveToThread(self.gi)
            self.gi.finished.connect(self.generate_thread.quit)
            self.generate_thread.start()

        self.fakeTotal = len(self.array_of_invoices)
        # QtCore.QTimer.singleShot(0, self.nextInvoice)
        
        print("Done all the shiz")
        
    def nextInvoice(self):
        try:
            self.invoice = next(self.allInvoices)
            self.step(len(self.array_of_invoices), self.complete)
        except StopIteration:
            return
        self.generateOneInvoice(self.invoice)
        QtCore.QTimer.singleShot(0, self.nextInvoice)

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
            self.ui.label_InternetStatus.setText("<html><head/><body><p><span style=\" font-weight:600;\">Internet: </span>Disconnect</p></body></html>")
        else:
            self.ui.label_InternetStatus.setText("<html><head/><body><p><span style=\" font-weight:600;\">Internet: </span>Connected</p></body></html>")
        self.ui.label_InternetStatus.adjustSize()    

    def getInvoices(self):
        if self.filename == "":
            print ("No file selected")
            return
        csv_reader = g.CSVParser(self.filename)
        self.array_of_invoices = csv_reader.get_array_of_invoices()
        print(type(self.array_of_invoices))
        # print(f"[*]\tGenerating invoices from : {self.filename}")
        # self.totalInvoices = len(self.array_of_invoices)
        # print(f"Total: {self.totalInvoices}")
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

class LoadingScreen(QtWidgets.QMainWindow):
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

class Worker(QThread):
    
    update_whichInvoice = pyqtSignal(str)
    update_fileSelected = pyqtSignal(str)
    update_progress = pyqtSignal(int)
    percentageComplete = 0
    dFileName = ""
    filename = ""

    def run(self):
        self.update_fileSelected.emit(self.dFileName)
        totalLitres = 0
        unitCost = 0
        totalDolla = 0
        counter = 0
        for invoice in self.array_of_invoices:
            # print(f"type: {type(invoice)}")
            for item in invoice.items:
                totalLitres += item['quantity']
                unitCost = item['unit_cost']
                totalDolla += (totalLitres*unitCost)
            self.generateOneInvoice(invoice)
            counter += 1
            self.step(counter, len(self.array_of_invoices))

        os.remove(self.filename)
        print(f"[*]\tTotals:\t {totalLitres} Litres\t £{totalDolla}")
        # if self.complete >= len(self.array_of_invoices) and self.fakeTotal == len(self.array_of_invoices):
        #     print("[*]\tAll invoices have been successfully generated!")
        # elif self.complete >= self.fakeTotal and self.fakeTotal < len(self.array_of_invoices):
        #     print(f"[*]\tSome invoices were generated... {self.complete}/{len(self.array_of_invoices)}")

    def getInvoices(self):
        if self.filename == "":
            print ("No file selected")
            return
        csv_reader = g.CSVParser(self.filename)
        self.array_of_invoices = csv_reader.get_array_of_invoices()
        print(type(self.array_of_invoices))
        # print(f"[*]\tGenerating invoices from : {self.filename}")
        # self.totalInvoices = len(self.array_of_invoices)
        # print(f"Total: {self.totalInvoices}")

    def generateOneInvoice(self, invoice):
        # print(f"[*] Generating Invoice for {invoice.name}")
        self.update_whichInvoice.emit(invoice.name)
        try:
            g.main(invoice)
            # self.complete += 1
        except Exception as e:
            print(f"Error >> {e}")
            # self.fakeTotal -= 1

    def step(self, invoicesDone, totalInvoices):
        if invoicesDone == totalInvoices:
            self.percentageComplete = 100
        elif invoicesDone < totalInvoices:
            self.percentageComplete = int((invoicesDone / totalInvoices)*100)
        else:
            return
        self.update_progress.emit(self.percentageComplete)

    def selectFile(self):
        print("Selecting CSV/Excel file")
        # Current directory
        self.filename = QFileDialog.getOpenFileName()
        path = self.filename[0]

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
                    self.filename = "reformatted_" + self.filename
                except Exception as e:
                    print(f"[*]\tFail\t{e}")
            # Check if it's an excel file
            else:
                print(f"Not sure what format this is...\"{self.filename}\"")
        self.dFileName = self.filename
class MiniWorker(QThread):
    invoice = None

    def run(self):
        try:
            g.main(self.invoice)
            print(f"Generated for {self.invoice.name}")
        except Exception as e:
            print(f"Error >> {e}")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle(QtWidgets.QStyleFactory().create('Segoe UI'))
    w = LoadingScreen()
    w.show()
    sys.exit(app.exec_())


# Helpful links
# https://www.programmersought.com/article/6264704979/ - Helps set up UI
# https://stackoverflow.com/questions/43260595/attributeerror-ui-mainwindow-object-has-no-attribute-setcentralwidget
# https://www.youtube.com/watch?v=G7ffF0U36b0 - Helped with threading
