# Tax Assistant

Script calculating the tax to paid from dividends, stocks and options. Data taken from IB/LYNX broker trading reports.


## Table of contents
* [Technologies](#technologies)
* [Setup](#setup)
* [Contact](#contact)

## Technologies
* Python version: 3.8.5

## Setup
To create virtual environment:
```
python3 -m venv venv
```

To activate virtual environment:
```
source venv/bin/activate
```

To install library:
```
pip install -r requirements.txt
```

Dividends, stocks and options reports should be generated with this instruction:
https://drive.google.com/file/d/1mQEkB4aBKqfeYbAGbqRqFAvxJprXFws6/view

Every report should be in `data/` catalog with name `STOCKS.csv` or `DIVIDENDS.csv`.

To run script:
```
python3 summary.py
```

Example output:
```
SUMMARY:
------------------------------------------------------------
DIV: 47.32 PLN
------------------------------------------------------------
STK: -889.28 PLN
------------------------------------------------------------
OPT: 356.99 PLN
------------------------------------------------------------
SUM: -484.97 PLN
```

## Contact
Created by Adam Misiak