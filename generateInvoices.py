import requests
from dataclasses import dataclass
from typing import List
import os
import csv
import typer

# Manually set attributes for the invoices
from_who = "Kelland Dairy\nLapford, Crediton\nEX17 6AG\n"
customNote = "Thank you for choosing Kelland Dairy!\n\nIf you need to contact us, you can email or call us.\nmilk@kellanddairy.co.uk\n01363 779134\n\nIf you want to know more about us, visit our website!\nwww.kellanddairy.co.uk"
ukCurrency = "GBP"
ourLogo = "https://www.kellanddairy.co.uk/wp-content/uploads/2018/07/Kelland-Dairy-Final-450-Logo.png"
bankInfo = "Payment methods: Bank Transfer, BACS, Standing order or Cheque\nSort code: 30-93-14\nAccount Number: 0556 9802"

@dataclass
class Invoice:
    name: str
    # logo: str
    date: str
    items: List[dict]
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
        # 
        self.invoices_directory = f"{os.path.dirname(os.path.abspath(__file__))}/{'invoices'}"

    def connect_to_api_and_save_invoice_pdf(self, invoice: Invoice) -> None:
        invoice_parsed = {
            'to': invoice.name,
            'from': from_who,
            'logo': ourLogo,
            'date': invoice.date,
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
        invoice_name = f"{invoice.name}_invoice.pdf"
        invoice_path = f"{self.invoices_directory}/{invoice_name}"
        with open(invoice_path, 'wb') as f:
            typer.echo(f"Generate invoice for {invoice_name}")
            f.write(pdf_content)


def main(csv_name: str = typer.Argument('invoices.csv')):
    # Lets the user know it's running
    print("[*]  Internet required to run")
    typer.echo(f"Generating invoices using : {csv_name}")
    csv_reader = CSVParser(csv_name)
    array_of_invoices = csv_reader.get_array_of_invoices()
    api = ApiConnector()
    counter = 0
    for invoice in array_of_invoices:
        counter = counter + 1
        api.connect_to_api_and_save_invoice_pdf(invoice)
        if counter == array_of_invoices.__len__:
            print("Done")

if __name__ == "__main__":
    typer.run(main)