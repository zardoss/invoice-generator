import requests
import os
from dataclasses import dataclass
from typing import List
import pathlib
import csv
import typer

# For checking internet connection to website we're using
url = "https://invoice-generator.com"
timeout = 10
# Current working directory
currentpath = os.getcwd()
# Folder name we want
invoiceFolder = "invoices"
# Directory where we want invoices to go
path = pathlib.Path(f"{currentpath}/{invoiceFolder}")
# Number of invoices
nInvoices = 0
# Manually set attributes for the invoices
# For my company
from_who = "Kelland Dairy\nLapford, Crediton\nEX17 6AG\n"
customNote = "Thank you for choosing Kelland Dairy!\n\nIf you need to contact us, you can email or call us.\nmilk@kellanddairy.co.uk\n01363 779134\n\nIf you want to know more about us, visit our website!\nwww.kellanddairy.co.uk"
ukCurrency = "GBP"
ourLogo = "https://www.kellanddairy.co.uk/wp-content/uploads/2018/07/Kelland-Dairy-Final-450-Logo.png"
bankInfo = "Payment methods: Bank Transfer, BACS, Standing order or Cheque\nSort code: 30-93-14\nAccount Number: 0556 9802"

# For public show
# from_who = "Leaf Lane\nLeaf City\nLE4F C1T1\n"
# customNote = "Thank you for choosing Leaf!\n\nIf you need to contact us, you can email or call us.\nmilk@leaf.co.uk\n011111 11111\n\nIf you want to know more about us, visit our website!\nwww.leaf.co.uk"
# ukCurrency = "GBP"
# ourLogo = "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/1f9ed517-f705-42e3-960a-9d56d8bb2f67/d7gesj7-99f809b9-6219-4e50-8a59-d1fd1b41a350.png?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOiIsImlzcyI6InVybjphcHA6Iiwib2JqIjpbW3sicGF0aCI6IlwvZlwvMWY5ZWQ1MTctZjcwNS00MmUzLTk2MGEtOWQ1NmQ4YmIyZjY3XC9kN2dlc2o3LTk5ZjgwOWI5LTYyMTktNGU1MC04YTU5LWQxZmQxYjQxYTM1MC5wbmcifV1dLCJhdWQiOlsidXJuOnNlcnZpY2U6ZmlsZS5kb3dubG9hZCJdfQ.PeFz4A2VN7EPrkbSPt6cmhuhHLU4enYznwCE23GN85g"
# bankInfo = "Payment methods: Bank Transfer, BACS, Standing order or Cheque\nSort code: 01-02-03\nAccount Number: 1234 5678"


@dataclass
class Invoice:
    name: str
    date: str
    items: List[dict]
    # logo: str
    # notes: str
    # currency: str
    # terms: str

class CSVParser:
    def __init__(self, csv_name: str) -> None:
        # Information put into the invoice
        self.field_names = (
            'name',
            # 'logo',
            'date',
            'items',
            # 'terms'
            # 'notes',
            # 'currency'
        )
        self.csv_name = csv_name
    
    def get_array_of_invoices(self) -> List[Invoice]:
        with open(self.csv_name, 'r') as f:
            reader = csv.DictReader(f, self.field_names)
            header = 0
            current_csv = []
            for row in reader:
                if header == 0:
                    header += 1
                    continue
                invoice_obj = Invoice(**row)
                invoice_obj.items = eval(invoice_obj.items)
                current_csv.append(invoice_obj)
        return current_csv

class ApiConnector:
    def __init__(self) -> None:
        self.headers = {"Content-Type": "application/json"}
        # Website that we're using to generate the PDF invoices
        self.url = 'https://invoice-generator.com'
        # TODO; write description
        self.invoices_directory = f"{os.path.dirname(os.path.abspath(__file__))}/{'invoices'}"
        # print(f"{self.invoices_directory}")

    def connect_to_api_and_save_invoice_pdf(self, invoice: Invoice) -> None:
        invoice_parsed = {
            'to': invoice.name,
            'from': from_who,
            'logo': ourLogo,
            # 'date': invoice.date,
            'items': invoice.items,
            'notes': customNote,
            'currency': ukCurrency,
            'terms': bankInfo
        }
        r = requests.post(self.url, json=invoice_parsed, headers=self.headers)
        if r.status_code == 200 or r.status_code == 201:
            pdf = r.content
            self.save_invoice_to_pdf(pdf, invoice)
            # typer.echo("File Saved")
        else:
            typer.echo("Fail :", r.text)

    def save_invoice_to_pdf(self, pdf_content: str, invoice: Invoice) -> None:
        invoice_name = f"{invoice.name}'s invoice.pdf"
        invoice_path = f"{path}/{invoice_name}"
        
        with open(invoice_path, 'wb') as f:
            # typer.echo(f"[*]\t\tGenerated invoice for {invoice.name}")
            f.write(pdf_content)

# Checks internet connection
def checkConnection():
    try:
        request = requests. get(url, timeout=timeout)
        # print("[*]\tInternet Connection : Estabilished")
        return True
    except (requests. ConnectionError, requests. Timeout) as exception:
        print("[*]\tInternet Connection : Failed")
        return False

def createDirectory():
    if path.exists() == False:
        try:
            os.mkdir(path)
        except OSError:
            print ("[*]\tCreation of the directory %s failed" % path)
        else:
            print ("[*]\tSuccessfully created the directory %s " % path)
    else:
        return
        # print(f"[*]\tThere's already a directory called {invoiceFolder} that exists. I'll begin generating the invoices")

def main(csv_name: str = typer.Argument('invoices.csv')):
    print("[*]\tStarting invoice generator")
    # Lets the user know it's running
    if checkConnection() == False:
        print("[*]\tInternet required to run")
        print("[*]\tFailed to generate invoices")
        exit()
    
    createDirectory()
    typer.echo(f"[*]\tGenerating invoices from : {csv_name}")
    csv_reader = CSVParser(csv_name)
    array_of_invoices = csv_reader.get_array_of_invoices()
    api = ApiConnector()
    # Number of invoices to generate from data
    global nInvoices
    nInvoices = len(array_of_invoices)
    counter = 0
    print(f"[*]\tThere are {nInvoices} invoices to generate")
    for invoice in array_of_invoices:
        counter += 1
        api.connect_to_api_and_save_invoice_pdf(invoice)
        if counter == nInvoices:
            print("[*]\tAll invoices have been successfully generated!")

    # input("[*]\tPress any key to exit")
    print("[*]\tExited invoice generator!")

# Function overload to take one invoice
def main(invoice):
    # Lets the user know it's running
    if checkConnection() == False:
        print("[*]\tInternet required to run")
        print("[*]\tFailed to generate invoices")
        exit()
    # print("[*]\tGenerating single invoice")
    createDirectory()
    api = ApiConnector()
    try:
        api.connect_to_api_and_save_invoice_pdf(invoice)
    except Exception as e:
        print(f"[*]\tUnable to save invoice\nError >> {e}")
        exit()


if __name__ == "__main__":
    typer.run(main)