#This is a price comparison system. 
#In V2， I have added a login and sign up system. The user can sign up with a username and password,
#which will be stored in a JSON file. The user can then log in with their credentials to access the main page of the application.
#The main page allows the user to search for products and compare prices based on unit price.


import os#this is used to get the current file path and read the list.txt file.
import re#this is used to parse the price and quantity from the input string.
import tkinter as tk
from PIL import Image, ImageTk
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

        image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Logo.png")
        self.img_logo = ImageTk.PhotoImage(Image.open(image_path).resize((50, 50)))

        self.configure(bg="#F1EFE8")
        self.create_widgets()
    def create_widgets(self):
        logo_frame = tk.Frame(self, bg="white")
        logo_frame.pack(pady=(20, 10))

        tk.Label(logo_frame, image=self.img_logo).pack(padx=10,pady=10)

        self.label_introduce = tk.Label(self, text="Compare supermarket prices")
        self.label_introduce.pack(pady=5)

        self.label_username = tk.Label(self, text="Username:",width=20, anchor="w", justify="left")
        self.label_username.pack(pady=5)

        self.entry_username = tk.Entry(self)
        self.entry_username.pack(pady=5)

        self.label_password = tk.Label(self, text="Password:",width=20, anchor="w", justify="left")
        self.label_password.pack(pady=5)


        self.entry_password = tk.Entry(self, show="*")
        self.entry_password.pack(pady=5)

        self.label_password_confirm = tk.Label(self, text="Confirm Password:",width=20, anchor="w", justify="left")
        self.label_password_confirm.pack(pady=5)

        self.entry_password_confirm = tk.Entry(self, show="*")
        self.entry_password_confirm.pack(pady=5)

        #Add a row for the buttons and pack them side by side
        button_row = tk.Frame(self, bg="#F1EFE8")
        button_row.pack(pady=10)

        self.button_signup = tk.Button(button_row, text="Sign Up", width=20,bg="#0F6E56",fg="white",command=self.sign_up)
        self.button_signup.pack(side=tk.RIGHT, padx=(0, 10))

        self.button_back = tk.Button(button_row, text="Back", width=8, bg="#F1EFE8", fg="#1E88E5", activebackground="#F1EFE8", activeforeground="#1E88E5", borderwidth=0, relief="flat", highlightthickness=0, cursor="hand2", command=lambda: self.controller.show_frame("login"))
        self.button_back.pack(side=tk.LEFT)

        #Add hover effect for the back button
        self.button_back.bind("<Enter>", lambda e: self.button_back.config(fg="#0D47A1", font=("Arial", 10, "underline")))
        self.button_back.bind("<Leave>", lambda e: self.button_back.config(fg="#1E88E5", font=("Arial", 10)))


    def sign_up(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        confirm_password = self.entry_password.get()

        if not username or not password or " " in username or " " in password or len(username) < 3 or len(password) < 3 or len(username) > 20 or len(password) > 20:
            messagebox.showerror("Sign Up Failed", "Username and password must be at least 3 characters long and cannot contain spaces.")
            return
        if password != confirm_password:
            messagebox.showerror("Sign Up Failed", "Passwords do not match.")
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

        image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Logo.png")
        self.img_logo = ImageTk.PhotoImage(Image.open(image_path).resize((50, 50)))

        self.configure(bg="#F1EFE8")
        self.create_widgets()

    def create_widgets(self):
        logo_frame = tk.Frame(self, bg="white")
        logo_frame.pack(pady=(20, 10))
        tk.Label(logo_frame, image=self.img_logo).pack(padx=10,pady=10)

        self.label_introduce = tk.Label(self, text="Compare supermarket prices")
        self.label_introduce.pack(pady=5)

        self.label_username = tk.Label(self, text="Username:",width=20, anchor="w", justify="left")
        self.label_username.pack(pady=5)

        self.entry_username = tk.Entry(self)
        self.entry_username.pack(pady=5)

        self.label_password = tk.Label(self, text="Password:",width=20, anchor="w", justify="left")
        self.label_password.pack(pady=5)

        self.entry_password = tk.Entry(self, show="*")
        self.entry_password.pack(pady=5)

        self.button_login = tk.Button(self, text="Login",width=20,bg="#0F6E56",fg="white", command=self.login)
        self.button_login.pack(pady=10)

        self.button_signup = tk.Button(self, text="Sign Up",width=20,bg="#0F6E56",fg="white",command=lambda: self.controller.show_frame("signup"))
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

        image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Logo.png")
        self.img_logo = ImageTk.PhotoImage(Image.open(image_path).resize((50, 50)))
        image_Discount = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Discount.png")
        self.img_Discount = ImageTk.PhotoImage(Image.open(image_Discount).resize((50, 50)))
        image_History = os.path.join(os.path.dirname(os.path.abspath(__file__)), "History.png")
        self.img_History = ImageTk.PhotoImage(Image.open(image_History).resize((50, 50)))
        image_Home = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Home.png")
        self.img_Home = ImageTk.PhotoImage(Image.open(image_Home).resize((50, 50)))
        image_Nearby = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Nearby.png")
        self.img_Nearby = ImageTk.PhotoImage(Image.open(image_Nearby).resize((50, 50)))
        image_Search = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Search.png")
        self.img_Search = ImageTk.PhotoImage(Image.open(image_Search).resize((50, 50)))
        image_Settings = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Settings.png")
        self.img_Settings = ImageTk.PhotoImage(Image.open(image_Settings).resize((50, 50)))

        #TKinter GUI setup


        # logo frame
        logo_frame = tk.Frame(self, bg="white")
        logo_frame.pack(side=tk.TOP, fill=tk.X)
        tk.Label(logo_frame, image=self.img_logo, bg="white").pack(side=tk.LEFT, padx=10, pady=10)
        logo_label = tk.Label(logo_frame, text="PriceWise", font=("Arial", 12), bg="white")
        logo_label.pack(side=tk.LEFT)


        # menu frame
        menu_frame = tk.Frame(self, bg="white", width=200, height=700)
        menu_frame.pack(side=tk.LEFT, fill=tk.Y)
        menu_frame.pack_propagate(False)

        # Home row (highlighted green because this is the main page)
        row_home = tk.Frame(menu_frame, bg="#DCEEE3")
        row_home.pack(fill=tk.X)
        tk.Label(row_home, image=self.img_Home, bg="#DCEEE3").pack(side=tk.LEFT, padx=10, pady=10)
        tk.Label(row_home, text="Home", font=("Arial", 12), fg="#2C2C2A", bg="#DCEEE3").pack(side=tk.LEFT)

        # Discount row
        row_discount = tk.Frame(menu_frame, bg="white")
        row_discount.pack(fill=tk.X)
        self.button_discount = tk.Label(row_discount, image=self.img_Discount, bg="white")
        self.button_discount.pack(side=tk.LEFT, padx=10, pady=10)
        tk.Label(row_discount, text="Discount", font=("Arial", 12), fg="#2C2C2A", bg="white").pack(side=tk.LEFT)
        row_discount.bind("<Button-1>", lambda e: self.controller.show_frame("discount"))

        # History row
        row_history = tk.Frame(menu_frame, bg="white")
        row_history.pack(fill=tk.X)
        self.button_history = tk.Label(row_history, image=self.img_History, bg="white")
        self.button_history.pack(side=tk.LEFT, padx=10, pady=10)
        tk.Label(row_history, text="History", font=("Arial", 12), fg="#2C2C2A", bg="white").pack(side=tk.LEFT)
        row_history.bind("<Button-1>", lambda e: self.controller.show_frame("history"))

        # Nearby row
        row_nearby = tk.Frame(menu_frame, bg="white")
        row_nearby.pack(fill=tk.X)
        self.button_nearby = tk.Label(row_nearby, image=self.img_Nearby, bg="white")
        self.button_nearby.pack(side=tk.LEFT, padx=10, pady=10)
        tk.Label(row_nearby, text="Nearby", font=("Arial", 12), fg="#2C2C2A", bg="white").pack(side=tk.LEFT)
        row_nearby.bind("<Button-1>", lambda e: self.controller.show_frame("nearby"))

        # Settings row, pinned to bottom, smaller font
        row_settings = tk.Frame(menu_frame, bg="white")
        row_settings.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        tk.Label(row_settings, image=self.img_Settings, bg="white").pack(side=tk.LEFT, padx=10)
        tk.Label(row_settings, text="Settings", font=("Arial", 9), fg="#2C2C2A", bg="white").pack(side=tk.LEFT)
                # right content area
        content_frame = tk.Frame(self, bg="white")
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        big_title = tk.Label(content_frame, text="Compare grocery prices", font=("Arial", 22, "bold"), bg="white")
        big_title.pack(anchor="w", padx=20, pady=(20, 5))

        subtitle = tk.Label(content_frame, text="Find the cheapest option across supermarkets", font=("Arial", 10), fg="#9E9E9E", bg="white")
        subtitle.pack(anchor="w", padx=20, pady=(0, 15))

        search_row = tk.Frame(content_frame, bg="white")
        search_row.pack(anchor="w", padx=20, pady=(0, 15))
        tk.Label(search_row, image=self.img_Search, bg="white").pack(side=tk.LEFT, padx=(0, 5))
        self.entry_search = tk.Entry(search_row, width=40)
        self.entry_search.pack(side=tk.LEFT, padx=5)
        tk.Button(search_row, text="Search", bg="#0F6E56", fg="white",
                  command=lambda: self.search(self.entry_search.get())).pack(side=tk.LEFT, padx=5)

        # three result rows: supermarket name left, price right
        self.results_frame = tk.Frame(content_frame, bg="white")
        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.result_rows = []
        for i in range(3):
            row = tk.Frame(self.results_frame, bg="white", highlightbackground="#E0E0E0", highlightthickness=1)
            row.pack(side=tk.TOP, fill=tk.X, pady=5)
            self.result_rows.append(row)

    def search(self, query):
        cleaned_query = query.strip()
        if not cleaned_query or " " in query or len(cleaned_query) == 1 or not re.fullmatch(r"[A-Za-z]+", cleaned_query):
            messagebox.showerror("Input Error", "Please enter a valid word (at least 2 letters, no spaces).")
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

        parsed_items.sort(key=lambda item: item["unit_price"])

        # clear previous results from each row
        for row in self.result_rows:
            for widget in row.winfo_children():
                widget.destroy()

        if not parsed_items:
            tk.Label(self.result_rows[0], text="No comparable products were found.", bg="white").pack(pady=10)
            return

        for item, row in zip(parsed_items, self.result_rows):
            tk.Label(row, text=item["supermarket"], bg="white").pack(side=tk.LEFT, padx=10, pady=10)
            tk.Label(row, text=f"${item['price']:.2f}", bg="white").pack(side=tk.RIGHT, padx=10, pady=10)


        
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Price Comparison System")
        self.geometry("700x600")

        self.img_logo = ImageTk.PhotoImage(Image.open("Logo.png").resize((50, 50)))

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