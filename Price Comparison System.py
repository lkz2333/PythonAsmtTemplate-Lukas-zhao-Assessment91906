#This is a price comparison system. 
#In V2， I have added a login and sign up system. The user can sign up with a username and password,
#which will be stored in a JSON file. The user can then log in with their credentials to access the main page of the application.
#The main page allows the user to search for products and compare prices based on unit price.


import os#this is used to get the current file path and read the list.txt file.
import re#this is used to parse the price and quantity from the input string.
import tkinter as tk
import json
from tkinter import Frame#this is used to create a frame in the GUI.
from tkinter import messagebox



def load_lines(file_name="list.txt"):
    #read the list.txt file and return a list of non-empty lines
    base_dir = os.path.dirname(os.path.abspath(__file__))

    #get the full path of the list.txt file
    file_path = os.path.join(base_dir, file_name)

    #check if the file exists, if not return an empty list 
    if not os.path.exists(file_path):
        return []

    with open("list.txt", "r") as f:
        return [line.strip() for line in f if line.strip()]


def to_base_quantity(quantity, unit):
    #convert the quantity to a base unit (g or ml) for comparison
    unit = unit.lower()
    if unit == "kg":
        return quantity * 1000, "g"
    if unit == "g":
        return quantity, "g"
    if unit == "l":
        return quantity * 1000, "ml"
    if unit == "ml":
        return quantity, "ml"
    return quantity, "ea"


def parse_line(line):
    #parse a line of text to extract the product name, price, quantity, and unit
    lowered = line.lower()

    price_match = re.search(r"\$\s*(\d+(?:\.\d+)?)", line)

    if price_match:
        price = float(price_match.group(1))
    else:
        fallback_match = re.search(r"(\d+(?:\.\d+)?) \s* $", line)
        if not fallback_match:
            return None
        price = float(fallback_match.group(1))

    size_match = re.search(r"(\d+(?:\.\d+)?) \s* (kg|g|l|ml)\b", lowered)
    if size_match:
        quantity = float(size_match.group(1))
        unit = size_match.group(2)
    else:
        quantity = 1.0
        unit = "ea"
        
    supermarket_match = re.search(r"\|\s*([^\|]+)\s*$", line)
    if supermarket_match:
        supermarket = supermarket_match.group(1).strip()
    else:
        supermarket = "Unknown Supermarket"

    base_quantity, base_unit = to_base_quantity(quantity, unit)

    unit_price = price / base_quantity

    name = re.split(r"[,\-\|]", line, maxsplit=1)[0].strip()
    if not name:
        name = "Unknown Item"

    return {
        "name": name,
        "price": price,
        "quantity": quantity,
        "unit": unit,
        "base_quantity": base_quantity,
        "base_unit": base_unit,
        "unit_price": unit_price,
        "supermarket": supermarket,
    }

#sign up page
class SignUpPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()
    def create_widgets(self):
        self.label_username = tk.Label(self, text="Username:")
        self.label_username.pack(pady=5)

        self.entry_username = tk.Entry(self)
        self.entry_username.pack(pady=5)

        self.label_password = tk.Label(self, text="Password:")
        self.label_password.pack(pady=5)

        self.entry_password = tk.Entry(self, show="*")
        self.entry_password.pack(pady=5)

        self.button_signup = tk.Button(self, text="Sign Up", command=self.sign_up)
        self.button_signup.pack(pady=10)

    def sign_up(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        if not username or not password or " " in username or " " in password or len(username) < 3 or len(password) < 3:
            messagebox.showerror("Sign Up Failed", "Username and password must be at least 3 characters long and cannot contain spaces.")
            return

        # Load existing user data from JSON file
        try:
            with open("users.json", "r") as f:
                users = json.load(f)
        except FileNotFoundError:
            users = {}

        # Check if the username already exists
        if username in users:
            messagebox.showerror("Sign Up Failed", "Username already exists.")
            return

        # Add the new user to the dictionary
        users[username] = password

        # Save the updated user data back to the JSON file
        with open("users.json", "w") as f:
            json.dump(users, f)

        messagebox.showinfo("Sign Up Successful", "You can now log in with your new account.")
        self.controller.show_frame("login")

#Login page
class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        self.label_username = tk.Label(self, text="Username:")
        self.label_username.pack(pady=5)

        self.entry_username = tk.Entry(self)
        self.entry_username.pack(pady=5)

        self.label_password = tk.Label(self, text="Password:")
        self.label_password.pack(pady=5)

        self.entry_password = tk.Entry(self, show="*")
        self.entry_password.pack(pady=5)

        self.button_login = tk.Button(self, text="Login", command=self.login)
        self.button_login.pack(pady=10)

        self.button_signup = tk.Button(
        self,
        text="Sign Up",
        command=lambda: self.controller.show_frame("signup"))
        self.button_signup.pack(pady=10)

    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        # Load user data from JSON file
        try:
            with open("users.json", "r") as f:
                users = json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Error", "User data file not found.")
            return

        # Check if the username exists and the password matches
        if username in users and users[username] == password:
            messagebox.showinfo("Login Successful", f"Welcome, {username}!")
            self.controller.show_frame("main")
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")



class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        self.result_text = tk.Text(self, width=80, height=24)
        #TKinter GUI setup

        # title label
        title_frame = Frame(self, bg="lightblue", width=700, height=50)
        title_frame.pack(fill=tk.X)
        title_label = tk.Label(title_frame, text="Price Comparison System", font=("Arial", 20), bg="lightblue")
        title_label.pack(pady=10)

        # logo frame
        logo_frame = tk.Frame(self, bg="lightblue", width=100, height=50)
        logo_frame.place(x=10, y=10)    
        logo_label = tk.Label(logo_frame, text="Logo", font=("Arial", 12), bg="lightblue")
        logo_label.pack(pady=10)

        # menu frame
        menu_frame = tk.Frame(self, bg="brown", width=50, height=700)
        menu_frame.pack(side=tk.LEFT, fill=tk.X)
        menu_label = tk.Label(menu_frame, text="Menu", font=("Arial", 12), bg="brown", height=700)
        menu_label.pack(pady=10)

        # search frame
        search_frame = tk.Frame(self, bg="yellow", width=700, height=50)
        search_frame.pack(fill=tk.X)
        search_label = tk.Label(search_frame, text="Enter product name:", font=("Arial", 12), bg="yellow")
        search_label.pack(pady=10)

        product_name = tk.Entry(search_frame, width=60)
        product_name.pack(pady=10, side=tk.LEFT, padx=8)
        button = tk.Button(search_frame, text="Search", command=lambda: self.search(product_name.get()))
        button.pack(pady=10, side=tk.RIGHT, padx=8)

        # result frame
        result_frame = tk.Frame(self, bg="lightgreen", width=700, height=500)
        result_frame.pack(fill=tk.BOTH, expand=True)
        result_label = tk.Label(result_frame, text="Results", font=("Arial", 12), bg="lightgreen")
        result_label.pack(pady=10)


        self.result_text = tk.Text(result_frame, width=80, height=24)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

    def search(self, query):
        cleaned_query = query.strip()
        if not cleaned_query or " " in query or len(cleaned_query) == 1 or not re.fullmatch(r"[A-Za-z]+", cleaned_query):
            messagebox.showerror("Input Error", "Please enter a valid word (at least 2 letters, no spaces).")
            self.result_text.delete("1.0", tk.END)
            return

        lines = load_lines()
        parsed_items = []

        for line in lines:
            item = parse_line(line)
            if item is not None:
                parsed_items.append(item)

        key = cleaned_query.lower()
        if key:
            parsed_items = [item for item in parsed_items if key in item["name"].lower()]

        self.result_text.delete("1.0", tk.END)
        if not parsed_items:
            self.result_text.insert(tk.END, "No comparable products were found.")
            return

        parsed_items.sort(key=lambda item: item["unit_price"])
        best = parsed_items[0]

        self.result_text.insert(
            tk.END,
            "Most affordable items:\n"
            f"{best['name']} | ${best['price']:.2f} | {best['quantity']}{best['unit']} | "
            f"${best['unit_price']:.4f}/{best['base_unit']} | {best['supermarket']}\n\n"
        )
        self.result_text.insert(tk.END, "Sort by unit price (low -> high):\n")

        for i, item in enumerate(parsed_items, start=1):
            self.result_text.insert(
                tk.END,
                f"{i}. {item['name']} | ${item['price']:.2f} | {best['quantity']}{best['unit']} | "
                f"${item['unit_price']:.4f}/{item['base_unit']} | {best['supermarket']}\n",
            )


        
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Price Comparison System")
        self.geometry("700x600")

        self.frames = {}

        self.frames["signup"] = SignUpPage(self, self)
        self.frames["login"] = LoginPage(self, self)
        self.frames["main"] = MainPage(self,self)
        

        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.show_frame("login")
    def show_frame(self, page_name):
        self.frames[page_name].tkraise()

if __name__ == "__main__":
    app = App()
    app.mainloop()