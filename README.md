# Personal Expense Tracker

A desktop expense-tracking application built with Python, Tkinter, SQLite, and Matplotlib.

## Features
- Dashboard for total income, total expenses, and available balance
- Add income and expense transactions
- Categories, dates, and optional notes
- Recent transaction history
- Delete selected transactions
- Expense category donut chart
- SQLite database saves transactions locally between sessions

## Requirements
- Python 3.10 or newer
- PyCharm (or another Python IDE)

## Setup on Windows
1. Open this folder in PyCharm.
2. Open the PyCharm terminal.
3. Install the dependency:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Run `main.py`.

Tkinter and SQLite are included with most standard Windows Python installations. If Tkinter is missing, repair/reinstall Python and ensure Tcl/Tk support is included.

## Data storage
The app creates `expenses.db` in the project folder the first time it runs. Keep this file if you want to preserve your transactions.

## Built with
- Python
- Tkinter / ttk
- SQLite
- Matplotlib

## Note
This is a learning project. It stores data locally on your computer and does not connect to a bank account.
