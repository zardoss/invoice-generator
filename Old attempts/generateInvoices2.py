import openpyxl

wb = openpyxl.load_workbook('/Users/callummclennan/Desktop/Invoicing/invoices.xlsx')

logo = Image.open('logo.png')
width,height = logo.size
ratio = width/height