import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import sqlite3
from pathlib import Path

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "expenses.db"

BG = "#101820"
PANEL = "#182630"
PANEL_LIGHT = "#20333e"
GREEN = "#35d07f"
TEXT = "#f3f7f8"
MUTED = "#9db0b8"
RED = "#ff6b6b"
BORDER = "#2a414c"


class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker | Personal Finance")
        self.root.geometry("900x900")
        self.root.state("normal")
        self.root.minsize(950, 650)
        self.root.configure(bg=BG)

        self.setup_database()
        self.setup_styles()
        self.build_ui()
        self.refresh_all()

    def setup_database(self):
        with sqlite3.connect(DB_PATH) as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kind TEXT NOT NULL CHECK(kind IN ('Income', 'Expense')),
                    amount REAL NOT NULL CHECK(amount > 0),
                    category TEXT NOT NULL,
                    note TEXT DEFAULT '',
                    trans_date TEXT NOT NULL
                )
            """)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview", background=PANEL, foreground=TEXT,
            fieldbackground=PANEL, rowheight=30, borderwidth=0,
            font=("Segoe UI", 10)
        )
        style.configure(
            "Treeview.Heading", background=PANEL_LIGHT, foreground=TEXT,
            font=("Segoe UI", 10, "bold"), relief="flat"
        )
        style.map("Treeview", background=[("selected", "#285b48")])
        style.configure(
            "TCombobox", fieldbackground=PANEL_LIGHT,
            background=PANEL_LIGHT, foreground=TEXT, arrowcolor=TEXT
        )

    def label(self, parent, text, size=10, color=TEXT, bold=False):
        return tk.Label(
            parent, text=text, bg=parent.cget("bg"), fg=color,
            font=("Segoe UI", size, "bold" if bold else "normal")
        )

    def build_ui(self):
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=22, pady=10)

        tk.Label(
            header, text="Expense Tracker",
            bg=BG, fg=TEXT,
            font=("Segoe UI", 23, "bold")
        ).pack(side="left")

        tk.Label(
            header, text="PERSONAL FINANCE DASHBOARD",
            bg=BG, fg=GREEN,
            font=("Segoe UI", 9, "bold")
        ).pack(side="left", padx=15)

        cards = tk.Frame(self.root, bg=BG)
        cards.pack(fill="x", padx=22, pady=5)

        self.income_value = self.make_card(
            cards, "TOTAL INCOME", GREEN
        )
        self.expense_value = self.make_card(
            cards, "TOTAL EXPENSES", RED
        )
        self.balance_value = self.make_card(
            cards, "AVAILABLE BALANCE", TEXT
        )

        # Scrollable main area
        outer = tk.Frame(self.root, bg=BG)
        outer.pack(fill="both", expand=True, padx=22, pady=10)

        canvas = tk.Canvas(
            outer, bg=BG, highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(
            outer, orient="vertical",
            command=canvas.yview
        )

        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        content = tk.Frame(canvas, bg=BG)

        window_id = canvas.create_window(
            (0, 0), window=content, anchor="nw"
        )

        content.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfigure(
                window_id, width=e.width
            )
        )

        # Mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(
                int(-1 * (event.delta / 120)), "units"
            )

        canvas.bind_all("<MouseWheel>", on_mousewheel)

        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=2)

        # Transaction form
        form = tk.Frame(
            content, bg=PANEL,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        form.grid(
            row=0, column=0,
            sticky="new", padx=(0, 12), pady=5
        )

        self.label(
            form, "Add Transaction", 15, TEXT, True
        ).pack(anchor="w", padx=18, pady=18)

        self.kind_var = tk.StringVar(value="Expense")
        self.category_var = tk.StringVar(value="Food")
        self.amount_var = tk.StringVar()
        self.note_var = tk.StringVar()
        self.date_var = tk.StringVar(
            value=date.today().isoformat()
        )

        self.label(form, "Transaction Type", color=MUTED).pack(
            anchor="w", padx=18
        )

        kind_box = ttk.Combobox(
            form, textvariable=self.kind_var,
            values=["Expense", "Income"],
            state="readonly"
        )
        kind_box.pack(
            fill="x", padx=18, pady=(5, 12), ipady=4
        )
        kind_box.bind(
            "<<ComboboxSelected>>", self.on_kind_change
        )

        self.label(form, "Amount (₹)", color=MUTED).pack(
            anchor="w", padx=18
        )
        tk.Entry(
            form, textvariable=self.amount_var,
            bg=PANEL_LIGHT, fg=TEXT,
            insertbackground=TEXT, relief="flat"
        ).pack(fill="x", padx=18, pady=(5, 12), ipady=7)

        self.label(form, "Category", color=MUTED).pack(
            anchor="w", padx=18
        )

        self.category_box = ttk.Combobox(
            form, textvariable=self.category_var,
            values=[
                "Food", "Travel", "Shopping",
                "Education", "Bills", "Health", "Other"
            ],
            state="readonly"
        )
        self.category_box.pack(
            fill="x", padx=18, pady=(5, 12), ipady=4
        )

        self.label(
            form, "Date (YYYY-MM-DD)", color=MUTED
        ).pack(anchor="w", padx=18)

        tk.Entry(
            form, textvariable=self.date_var,
            bg=PANEL_LIGHT, fg=TEXT,
            insertbackground=TEXT, relief="flat"
        ).pack(fill="x", padx=18, pady=(5, 12), ipady=7)

        self.label(form, "Note (Optional)", color=MUTED).pack(
            anchor="w", padx=18
        )

        tk.Entry(
            form, textvariable=self.note_var,
            bg=PANEL_LIGHT, fg=TEXT,
            insertbackground=TEXT, relief="flat"
        ).pack(fill="x", padx=18, pady=(5, 15), ipady=7)

        tk.Button(
            form,
            text="+  Add Transaction",
            command=self.add_transaction,
            bg=GREEN, fg="#082016",
            activebackground="#62e99e",
            relief="flat", cursor="hand2",
            font=("Segoe UI", 11, "bold"),
            pady=10
        ).pack(fill="x", padx=18, pady=(0, 15))

        # Transaction history
        history = tk.Frame(
            content, bg=PANEL,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        history.grid(
            row=0, column=1,
            sticky="new", pady=5
        )

        self.label(
            history, "Recent Transactions", 14, TEXT, True
        ).pack(anchor="w", padx=15, pady=15)

        columns = (
            "date", "type", "category", "note", "amount"
        )

        self.tree = ttk.Treeview(
            history, columns=columns,
            show="headings", height=8
        )

        headings = {
            "date": "DATE",
            "type": "TYPE",
            "category": "CATEGORY",
            "note": "NOTE",
            "amount": "AMOUNT"
        }

        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=100, anchor="center")

        self.tree.pack(
            fill="both", expand=True,
            padx=12, pady=10
        )

        tk.Button(
            history, text="Delete Selected",
            command=self.delete_selected,
            bg="#4a2930", fg="white",
            relief="flat", cursor="hand2",
            pady=7
        ).pack(anchor="e", padx=12, pady=(0, 12))

        # Expense chart
        chart_panel = tk.Frame(
            content, bg=PANEL,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        chart_panel.grid(
            row=1, column=0, columnspan=2,
            sticky="nsew", pady=12
        )

        self.label(
            chart_panel, "Expense Breakdown",
            14, TEXT, True
        ).pack(anchor="w", padx=15, pady=12)

        self.chart_area = tk.Frame(
            chart_panel, bg=PANEL, height=250
        )
        self.chart_area.pack(
            fill="both", expand=True, padx=8, pady=8
        )
        self.chart_area.pack_propagate(False)
    def make_card(self, parent, title, color):
        card = tk.Frame(parent, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        card.pack(side="left", fill="x", expand=True, padx=(0, 12))
        tk.Label(card, text=title, bg=PANEL, fg=MUTED, font=("Segoe UI", 9, "bold")).pack(
            anchor="w", padx=18, pady=(14, 5))
        value = tk.Label(card, text="₹0.00", bg=PANEL, fg=color, font=("Segoe UI", 21, "bold"))
        value.pack(anchor="w", padx=18, pady=(0, 14))
        return value

    def on_kind_change(self, _event=None):
        if self.kind_var.get() == "Income":
            self.category_box.configure(values=["Salary", "Freelance", "Gift", "Investment", "Other"])
            if self.category_var.get() not in ["Salary", "Freelance", "Gift", "Investment", "Other"]:
                self.category_var.set("Salary")
        else:
            self.category_box.configure(values=["Food", "Travel", "Shopping", "Education", "Bills", "Health", "Entertainment", "Other"])
            if self.category_var.get() not in ["Food", "Travel", "Shopping", "Education", "Bills", "Health", "Entertainment", "Other"]:
                self.category_var.set("Food")

    def add_transaction(self):
        kind = self.kind_var.get()
        category = self.category_var.get().strip()
        note = self.note_var.get().strip()
        try:
            amount = float(self.amount_var.get().strip())
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid amount", "Please enter an amount greater than zero.")
            return
        trans_date = self.date_var.get().strip()
        try:
            date.fromisoformat(trans_date)
        except ValueError:
            messagebox.showerror("Invalid date", "Enter the date in YYYY-MM-DD format, e.g. 2026-10-16.")
            return
        with sqlite3.connect(DB_PATH) as con:
            con.execute(
                "INSERT INTO transactions (kind, amount, category, note, trans_date) VALUES (?, ?, ?, ?, ?)",
                (kind, amount, category, note, trans_date)
            )
        self.amount_var.set("")
        self.note_var.set("")
        self.refresh_all()

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Select transaction", "Please select a transaction to delete.")
            return
        if not messagebox.askyesno("Confirm delete", "Delete the selected transaction?"):
            return
        ids = [self.tree.item(item, "tags")[0] for item in selected]
        with sqlite3.connect(DB_PATH) as con:
            con.executemany("DELETE FROM transactions WHERE id = ?", [(int(i),) for i in ids])
        self.refresh_all()

    def refresh_all(self):
        with sqlite3.connect(DB_PATH) as con:
            totals = con.execute("""
                SELECT
                    COALESCE(SUM(CASE WHEN kind='Income' THEN amount ELSE 0 END), 0),
                    COALESCE(SUM(CASE WHEN kind='Expense' THEN amount ELSE 0 END), 0)
                FROM transactions
            """).fetchone()
            rows = con.execute("""
                SELECT id, trans_date, kind, category, note, amount
                FROM transactions ORDER BY trans_date DESC, id DESC LIMIT 200
            """).fetchall()
            category_totals = con.execute("""
                SELECT category, SUM(amount) FROM transactions
                WHERE kind='Expense' GROUP BY category ORDER BY SUM(amount) DESC
            """).fetchall()

        income, expenses = totals
        balance = income - expenses
        self.income_value.config(text=f"₹{income:,.2f}")
        self.expense_value.config(text=f"₹{expenses:,.2f}")
        self.balance_value.config(text=f"₹{balance:,.2f}", fg=GREEN if balance >= 0 else RED)

        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            tid, trans_date, kind, category, note, amount = row
            self.tree.insert("", "end", values=(
                trans_date, kind, category, note or "—", f"{amount:,.2f}"
            ), tags=(str(tid),))
        self.draw_chart(category_totals)

    def draw_chart(self, data):
        for child in self.chart_area.winfo_children():
            child.destroy()
        if not data:
            tk.Label(self.chart_area, text="Add an expense to see your chart.",
                     bg=PANEL, fg=MUTED, font=("Segoe UI", 10)).pack(expand=True)
            return
        labels = [item[0] for item in data]
        values = [item[1] for item in data]
        fig = Figure(figsize=(5.3, 2.35), dpi=100, facecolor=PANEL)
        ax = fig.add_subplot(111)
        ax.set_facecolor(PANEL)
        wedges, _ = ax.pie(values, startangle=90, wedgeprops={"width": 0.42, "edgecolor": PANEL})
        ax.legend(wedges, [f"{name}  ₹{value:,.0f}" for name, value in zip(labels, values)],
                  loc="center left", bbox_to_anchor=(0.86, 0.5), frameon=False,
                  labelcolor=TEXT, fontsize=8)
        fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)
        canvas = FigureCanvasTkAgg(fig, master=self.chart_area)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


def main():
    root = tk.Tk()
    ExpenseTracker(root)
    root.mainloop()


if __name__ == "__main__":
    main()
