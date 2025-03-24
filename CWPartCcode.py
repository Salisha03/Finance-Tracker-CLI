import tkinter as tk
from tkinter import ttk
import json
import os

#create the FinanceTRackerCLI class for command-line interface operations
class FinanceTrackerCLI:
    def __init__(self):
        #intialize the class with a filename for stroing transactions
        self.filename = "transactions.json"
        #load the transactions 
        self.transactions = self.load_transactions(self.filename)

    def load_transactions(self, filename):
        #checking if the file exists and load transactions
        if os.path.exists(filename):
            with open(filename, "r")as file:
                return json.load(file)
        else:
            return {}

    def save_transactions(self, filename):
        #save the current transactions to the specified file in the json format
        with open(filename, "w")as file:
            json.dump(self.transactions, file, indent=4)

    def run_cli(self):
        #run the CLI, displaying a menu and handling user input
        while True:
            print("\nPersonal Finance Tracker")
            print("1. Show all transactions")
            print("2. Add a new transaction")
            print("3. Update a transaction")
            print("4. Delete transaction")
            print("5. Display Summary")
            print("6. Launch GUI")
            print("7. Exit")
            choice = input("Enter your choice: ")

            if choice == "1":
                self.show_transactions()
            elif choice == "2":
                self.add_transaction()
                self.save_transactions(self.filename)
            elif choice == "3":
                self.update_transaction()
            elif choice == "4":
                self.delete_transaction()
                self.save_transactions(self.filename)
            elif choice == "5":
                self.display_summary()
            elif choice == "6":
                self.launch_gui()
            elif choice == "7":
                self.save_transactions(self.filename)
                print("Exiting the program")
                break
            else:
                print("Invalid choice.Please check again.")

    def show_transactions(self):
        #iterate the transactions dictionary and print each transaction
        for category, transactions in self.transactions.items():
            print(f"\n{category}: ")
            for transaction in transactions:
                print(f"Amount: {transaction['amount']}, Date: {transaction['date']}")

    def add_transaction(self):
        #get the category,date, amount from the user
        category = input("Enter the category: ")
        if category not in self.transactions:
            self.transactions[category] = []
        date =input("Enter the transaction date(YYYY-MM-DD): ")
        amount = float(input("Enter the transaction amount: "))
        #create a new transaction dictionary and append it
        new_transaction = {"date": date, "amount": amount}
        self.transactions[category].append(new_transaction)
        self.save_transactions(self.filename)
        print("Transactions added successfully!")

    def update_transaction(self):
        #get the category and index of the transaction
        category = input("Enter the category of the transaction to update: ")
        if category in self.transactions:
            #validate the index input and update the transaction details 
            while True:
                try:
                    index = int(input("Enter the index of the transaction to update: ")) - 1
                    if 0 <= index < len(self.transactions[category]):
                        break
                    else:
                        print("Invalid index.Please check again.")
                except ValueError:
                    print("Invalid input.Enter a number.")

            while True:
                try:
                    amount = float(input("Enter the new transaction amount: "))
                    break
                except ValueError:
                    print("Invalid input.Please check again.")

            date = input("Enter the transaction date(YYYY-MM-DD): ")

            self.transactions[category][index] = {"amount": amount, "date": date}
            print("Transaction updated successfully!")
        else:
            print("Category not found.")

    def delete_transaction(self):
        category = input("Enter the category of the transaction to delete: ")
        if category in self.transactions:
            index = int(input("Enter the index of the  transaction to delete: ")) - 1
            if 0 <= index < len(self.transactions[category]):
                #remove the transaction from the category list
                del self.transactions[category][index]
                print("Transaction deleted.")
            else:
                print("Invalid index.Try again.")
        else:
            print("Entered category not found.Please check again.")

    def display_summary(self):
        #calculate the total amount spent in each category
        total_by_category = {}
        total_amount = 0

        for category,transactions_list in self.transactions.items():
            total_category = sum(transaction['amount'] for transaction in transactions_list)
            total_by_category[category] = total_category
            total_amount += total_category

        #display summary
        print("\nSummary")
        if not total_category:
            print("No transactions to display.")
        else:
            for category, amount in total_by_category.items():
                print(f"{category}: {amount}")

        print(f"Total: {total_amount}")
        print("End of summary")

    def launch_gui(self):
        #initialize the root window and create GUI
        root = tk.Tk()
        app = FinanceTrackerGUI(root,self.transactions)
        root.mainloop()
        #updte the transaction dictionary with the latest data from the GUI
        self.transactions = app.transactions
        self.save_transactions(self.filename)
                           
class FinanceTrackerGUI:
    def __init__(self, root,transactions):
        self.root = root
        self.root.title("Personal Finance Tracker")
        self.transactions = transactions
        self.sort_column = None
        self.sort_descending = False
        self.create_widgets()
        
    def create_widgets(self):
        #create the table frame, treeview,scrollbar, and search bar
        self.table_frame = ttk.Frame(self.root)
        self.table_frame.pack(fill=tk.BOTH,expand=True)

        self.tree = ttk.Treeview(self.table_frame, columns=("Category", "Amount", "Date"), show="headings")
        self.tree.heading("Category", text="Category", command= self.sort_by_category)
        self.tree.heading("Amount", text="Amount", command=self.sort_by_amount)
        self.tree.heading("Date", text="Date", command=self.sort_by_date)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill="y")
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.root, textvariable=self.search_var)
        self.search_button = ttk.Button(self.root, text="Search", command=self.search_transactions)
        self.search_entry.pack()
        self.search_button.pack()

        #display the transactions in the treeview
        self.display_transactions(self.transactions)
        
    def load_transactions(self,filename):
        try:
            with open(filename, "r")as file:
                transactions =json.load(file)
            return transactions
        except FileNotFoundError:
            print("File not found.")
            return {}

    def display_transactions(self,transactions):
        #Remove existing entries
        for row in self.tree.get_children():
            self.tree.delete(row)

        #Add transactions to treeview
        for category, data in transactions.items():
            for transaction in data:
                self.tree.insert("", tk.END, values=(category,transaction["amount"], transaction["date"]))

    def search_transactions(self):
        #search transactions based on user input
        search_criteria = self.search_var.get()
        filtered_transactions = {}
        
        for category, data in self.transactions.items():
            filtered_data= [
                transaction
                for transaction in data
                if search_criteria.lower() in transaction["date"].lower()
                or str(search_criteria) in str(transaction["amount"])
                or search_criteria in category.lower()
        ]
            if filtered_data:
                filtered_transactions[category] = filtered_data

            self.display_transactions(filtered_transactions)

    def sort_by_column(self, col,reverse):
        #sort the transactions by the specified column
        if self.sort_column == col:
            self.sort_descending = not self.sort_descending
        else:
            self.sort_column = col
            self.sort_descending = False
            
        items = self.tree.get_children("")

        if col == "Amount":
            data =[(float(self.tree.set(item, col)), item) for item in items]
        else:
            data = [(self.tree.set(item, col), item) for item in items]
        data.sort(reverse=self.sort_descending)
        for index, (val, item) in enumerate(data):
            self.tree.move(item, "", index)
        self.sort_descending = reverse
            
    def sort_by_category(self):
        self.sort_by_column("Category", False)
        
    def sort_by_amount(self):
        self.sort_by_column("Amount",self.sort_descending)
        
    def sort_by_date(self):
        self.sort_by_column("Date", True)

    def save_transactions(self, filename):
        with open(filename, "w") as file:
            json.dump(self.transactions, file, indent=4)
    
def main():
    #initialize the FinanceTrackerCLI class and run the command-line interface
    cli = FinanceTrackerCLI()
    cli.run_cli()

if __name__ == "__main__":
    main()
            
