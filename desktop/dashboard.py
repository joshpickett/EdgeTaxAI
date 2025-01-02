from desktop.setup_path import setup_desktop_path

setup_desktop_path()

import tkinter as tk
from tkinter import messagebox, simpledialog
from pathlib import Path
import requests
import matplotlib.pyplot as plt
from desktop.config import ASSETS_DIR, API_BASE_URL

DASHBOARD_LOGO = ASSETS_DIR / "logo" / "primary" / "edgetaxai-horizontal-color.svg"


# Dashboard Window
class ExpenseDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Expense Dashboard")
        self.geometry("600x400")
        self.iconphoto(True, tk.PhotoImage(file=str(DASHBOARD_LOGO)))

        # UI Elements
        self.expense_listbox = tk.Listbox(self, width=80, height=15)
        self.expense_listbox.pack(pady=20)

        # Buttons
        self.fetch_button = tk.Button(
            self, text="Fetch Expenses", command=self.fetch_expenses
        )
        self.fetch_button.pack()

        self.edit_button = tk.Button(
            self, text="Edit Selected Expense", command=self.edit_expense
        )
        self.edit_button.pack()

        self.delete_button = tk.Button(
            self, text="Delete Selected Expense", command=self.delete_expense
        )
        self.delete_button.pack()

        self.bar_chart_button = tk.Button(
            self, text="Show Bar Chart", command=self.show_bar_chart
        )
        self.bar_chart_button.pack()

        self.pie_chart_button = tk.Button(
            self, text="Show Pie Chart", command=self.show_pie_chart
        )
        self.pie_chart_button.pack()

        self.logout_button = tk.Button(
            self, text="Logout", command=self.logout, bg="#FF5733", fg="white"
        )
        self.logout_button.pack(pady=10)

        self.expenses = []  # Initialize the expenses list
        self.fetch_expenses()  # Load expenses on startup

    def fetch_expenses(self):
        try:
            response = requests.get(f"{API_BASE_URL}/expenses/list")
            if response.status_code == 200:
                self.expense_listbox.delete(0, tk.END)
                self.expenses = response.json()["expenses"]
                for expense in self.expenses:
                    self.expense_listbox.insert(
                        tk.END,
                        f"{expense['id']} - {expense['description']} - ${expense['amount']} - {expense['category']}",
                    )
            else:
                messagebox.showerror("Error", "Failed to fetch expenses.")
        except Exception as e:
            messagebox.showerror("Error", f"Error fetching expenses: {e}")

    def edit_expense(self):
        try:
            selected = self.expense_listbox.curselection()
            if not selected:
                messagebox.showwarning("Warning", "Please select an expense to edit.")
                return

            index = selected[0]
            expense = self.expenses[index]

            # Prompt for new values
            new_description = simpledialog.askstring(
                "Edit Expense",
                "Enter new description:",
                initialvalue=expense["description"],
            )
            new_amount = simpledialog.askfloat(
                "Edit Expense", "Enter new amount:", initialvalue=expense["amount"]
            )
            new_category = simpledialog.askstring(
                "Edit Expense", "Enter new category:", initialvalue=expense["category"]
            )

            if new_description and new_amount and new_category:
                updated_data = {
                    "description": new_description,
                    "amount": new_amount,
                    "category": new_category,
                }
                response = requests.put(
                    f"{API_BASE_URL}/expenses/edit/{expense['id']}", json=updated_data
                )
                if response.status_code == 200:
                    messagebox.showinfo("Success", "Expense updated successfully!")
                    self.fetch_expenses()
                else:
                    messagebox.showerror("Error", "Failed to update expense.")
        except Exception as e:
            messagebox.showerror("Error", f"Error editing expense: {e}")

    def delete_expense(self):
        try:
            selected = self.expense_listbox.curselection()
            if not selected:
                messagebox.showwarning("Warning", "Please select an expense to delete.")
                return

            index = selected[0]
            expense = self.expenses[index]

            confirm = messagebox.askyesno(
                "Confirm Deletion",
                f"Are you sure you want to delete expense '{expense['description']}'?",
            )
            if confirm:
                response = requests.delete(
                    f"{API_BASE_URL}/expenses/delete/{expense['id']}"
                )
                if response.status_code == 200:
                    messagebox.showinfo("Success", "Expense deleted successfully!")
                    self.fetch_expenses()
                else:
                    messagebox.showerror("Error", "Failed to delete expense.")
        except Exception as e:
            messagebox.showerror("Error", f"Error deleting expense: {e}")

    def show_bar_chart(self):
        try:
            categories = [expense["category"] for expense in self.expenses]
            amounts = [expense["amount"] for expense in self.expenses]

            if not categories or not amounts:
                messagebox.showwarning("No Data", "No expenses available to display.")
                return

            plt.figure(figsize=(8, 6))
            plt.bar(categories, amounts, color="skyblue")
            plt.title("Expense Summary")
            plt.xlabel("Category")
            plt.ylabel("Amount")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
        except Exception as e:
            messagebox.showerror("Error", f"Error generating bar chart: {e}")

    def show_pie_chart(self):
        try:
            categories = [expense["category"] for expense in self.expenses]
            amounts = [expense["amount"] for expense in self.expenses]

            if not categories or not amounts:
                messagebox.showwarning("No Data", "No expenses available to display.")
                return

            plt.figure(figsize=(8, 6))
            plt.pie(
                amounts,
                labels=categories,
                autopct="%1.1f%%",
                startangle=140,
                colors=plt.cm.Paired.colors,
            )
            plt.title("Expense Breakdown")
            plt.tight_layout()
            plt.show()
        except Exception as e:
            messagebox.showerror("Error", f"Error generating pie chart: {e}")

    def logout(self):
        try:
            response = requests.post(f"{API_BASE_URL}/logout")
            if response.status_code == 200:
                messagebox.showinfo("Logout", "You have been logged out successfully.")
            else:
                messagebox.showwarning("Logout", "Failed to notify server of logout.")
        except Exception as e:
            print(f"Error during logout: {e}")

        self.destroy()
        messagebox.showinfo("Logout", "Session ended. Please log in again.")


if __name__ == "__main__":
    app = ExpenseDashboard()
    app.mainloop()
