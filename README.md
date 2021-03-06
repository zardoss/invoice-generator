# invoice-generator

<h2>Contents</h2>

1. [What is this project?](#whatisthisproject)
2. [How do I use this?](#howdoiusethis)
    1. [Virtual Environment](#venv)
    2. [Requirements](#requirements)
    3. [Convert simple CSV to program CSV](#conversion)
    4. [Invoices](#invoices)
3. [How does it work?](#howdoesthiswork)
4. [Any issues?](#anyissues)
5. [Invoices generator GUI](#GUI)
6. [References](#references)
7. [Credits](#credits)

---

<!-- Section 1 -->
<h2>What is this project?<a name="whatisthisproject"></a></h2>
This is one of my first Python projects. It's my attempt at creating an invoice generator via multiple .py scripts using CSV files. I'm actualy creating this for a local milk business (free of charge due to how crap and basic it is).

---
<!-- Section 2 -->
<h2> How do I use this? <a name="howdoiusethis"></a> </h2>

1. User downloads their simple/readable spreadsheet as CSV
2. User passes this CSV file to openCSV.py to create a new CSV file
3. User will pass this newly generated CSV file to generateInvoices.py which will generate all the PDF invoices to a folder called "Invoices"
</br>
<h3> Initialise a virtual python environment <a name="venv"></a></h3>

```python
# Create virtual environment
python3 -m venv env

# Activate virtual environment
. venv/bin/activate
```

<h3> Requirements <a name="requirements"></a> </h3>
You'll need python 3+ for these scripts to work

```python
# Installs libraries listed in the requirements.txt file
pip3 install -r requirements.txt
```

<h3> Convert simple csv file to program compatible csv file <a name="conversion"></a></h3>

```python
python3 openCSV.py <user specified csv file>

#Example
python3 openCSV.py data.csv
```

<h3> Convert new CSV file generated by openCSV.py to freshly formatted PDF invoices <a name="invoices"></a></h3>

```python
# openCSV will produce a new CSV file which should be used when generating invoices via my script
python3 generateInvoices.py <user specified CSV file generated by openCSV.py>

# Example
python3 generateInvoices.py newData.csv
```

The user will download their 'simplified' spreadsheet as a <b>CSV file</b>. This CSV file will be passed as a parameter to the openCSV.py script which will convert the data from the simple format to a more complex format.
</br >
This format allows the data to become readable by my PDF invoice generator script. After the new CSV file has been created by openCSV.py, the user will pass this new CSV file to generateInvoices.py script and it will generate a bunch of invoices according the data.

---

<h2> How does it work? <a name="howdoesthiswork"></a></h2>
This whole project is currently dependant on this free online [invoice generator](https://invoice-generator.com). My program simply passes the appropriate information to the API they provide and downloads the generated result. I've made the generateInvoices.py file to successfully create PDF invoice files using the CSV file it's given.

---

<h2> Any issues? <a name="anyissues"></a></h2>
Contact me via Discord: zardoss#6558

---

<h3>Invoice generator GUI<a name="GUI"></a></h3>
<!-- <h2>Tkinter - GUI<a name="tkinter"></a></h2> -->
I tried using tkinter GUI library but faced a freezing issue which occured when generating the PDF invoices. I even tried threading and the GUI still froze. It's a good GUI besides that. I favoured the place layout methods as I could place GUI elements relative to the GUI window's size. 

<!-- <h2>PyQt5 - GUI<a name="pyqt5"></a></h2> -->
Ended up reworking the GUI with PyQt5 library.
<h3>Loading screen</h3>
<!--When changing values of the labels, you need to resize them too.-->
<img src="READMEImages/load.png" alt="Loading screen">
I thought it was a quite cool learning experience to incorporate a loading screen to my invoice-generator's GUI. It works a charm and looks really cool.

<h3>Invoice-generator main screen</h3>
<img src="READMEImages/vin1.png" alt="Main screen">
Here's a prototype main screen I've done in the past - bit of a jokey design but definitely aided in learning more about the PyQt5 library as a whole. I've added the essential buttons to the GUI making it easier to use. This is quite an intuitive design for someone to use. There's a progress bar to let them know how far along the program is when it generates invoices!

I'm currently working toward incorporating some form of threading into the program so:
1. The GUI window doesn't freeze up.
2. The invoices generate faster 10 fold.

---


<h2> References <a name="references"></a></h2>
<h3>Python Program references</h3>

- [Invoice generator tutorial (Partially works - good foundation material)](https://www.youtube.com/watch?v=icvjtqoufMM&t=849s)
- [Indexing/Slicing for lists, tuple, strings and other sequential data](https://railsware.com/blog/python-for-machine-learning-indexing-and-slicing-for-lists-tuples-strings-and-other-sequential-types/)
- [Online invoice generator](https://invoice-generator.com)
- [Used to check if invoices folder exists](https://www.guru99.com/python-check-if-file-exists.html)
- [Aesthetic: Press key to exit](https://intellipaat.com/community/5566/how-do-i-make-python-to-wait-for-a-pressed-key)

<h3>Spreadsheet references</h3>

- [Multiple tables into master table](https://www.youtube.com/watch?v=q8awNSYNdq4)

---

<h2> Credits <a name="credits"></a></h2>
Discord User : Felixi#4661
</br>
Helped me regarding the formatting of the list[dict] required for the items column in the CSV file. This is required for listing the items in the PDF via the invoice-generator.
</br></br>
Discord User: thatjoe#1201
Helped me in regards to threading/ attempting to multithread the tasks. It worked but unfortunately tkinter can't handle it and freezes regardless of whether I use threads or not!