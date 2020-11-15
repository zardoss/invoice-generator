# invoice-generator
## What is this project?
This is one of my first Python projects. It's my attempt at creating an invoice generator via multiple .py scripts using CSV files. I'm actualy creating this for a local milk business (free of charge due to how crap and basic it is).


## How do I use it?
1. User downloads their simple/readable spreadsheet as CSV
2. User passes this CSV file to openCSV.py to create a new CSV file
3. User will pass this newly generated CSV file to generateInvoices.py which will generate all the PDF invoices to a folder called "Invoices"
</br></br>
First, the user will download their 'simple' spreadsheet as a CSV file. This CSV file will be passed as a parameter to my openCSV.py script which will convert the data from the simple format to a more complex, more integral format (This is so it becomes readable for my PDF invoice generator). After the new CSV file has been created, the user will pass this new CSV file to generateInvoices.py script and it will generate a bunch of invoices according the data.

## How does it work?
This whole project is currently dependant on this free and online [invoice generator](https://invoice-generator.com). My program simply passes the appropriate information to the appropriate boxes and downloads the generated result. I've made the generateInvoices.py file to successfully create PDF invoice files using a CSV file that's passed in as a parameter when running the script
</br></br>
This script makes use of the online invoice generator's API.

## References
[Online Invoice Generator](https://invoice-generator.com)
