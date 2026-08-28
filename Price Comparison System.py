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
from tkinter import simpledialog



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

    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", line)
    date = date_match.group(1) if date_match else None
    if not date:
        date_match = re.search(r"(\d{2}/\d{2}/\d{4})", line)
        if date_match:
            date = date_match.group(1)

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
        "date": date
    }

#load and resize every icon used across pages, keyed by name
def load_menu_images():
    #load and resize every icon used across pages, keyed by name
    base_dir = os.path.dirname(os.path.abspath(__file__))
    filenames = {
        "logo": "Logo.png",
        "discount": "Discount.png",
        "history": "History.png",
        "home": "Home.png",
        "nearby": "Nearby.png",
        "search": "Search.png",
        "settings": "Settings.png",
    }
    return {
        key: ImageTk.PhotoImage(Image.open(os.path.join(base_dir, filename)).resize((50, 50)))
        for key, filename in filenames.items()
    }

#menu builder function, used by both the main page and the discount page
def build_menu(menu_frame, controller, images, active_page):
    #build the nav buttons, highlighting whichever page is currently active
    menu_items = [
        ("main", "Home", images["home"]),
        ("discount", "Discount", images["discount"]),
        ("history", "History", images["history"]),
        ("nearby", "Nearby", images["nearby"]),
    ]

    #loop through the menu items and create a button for each one, highlighting the active page
    for page_name, label_text, image in menu_items:
        bg = "#DCEEE3" if page_name == active_page else "white"
        btn = tk.Button(
            menu_frame, image=image, text=label_text, compound=tk.LEFT,
            font=("Arial", 12), fg="#2C2C2A", bg=bg, activebackground=bg,
            bd=0, highlightthickness=0, relief="flat", anchor="w",
            padx=10, pady=10, cursor="hand2",
            command=lambda p=page_name: controller.show_frame(p),
        )
        btn.pack(fill=tk.X)

    settings_btn = tk.Button(
        menu_frame, image=images["settings"], text="Settings", compound=tk.LEFT,
        font=("Arial", 9), fg="#2C2C2A", bg="white", activebackground="white",
        bd=0, highlightthickness=0, relief="flat", anchor="w",
        padx=10, pady=10, cursor="hand2",
    )
    settings_btn.pack(side=tk.BOTTOM, fill=tk.X)


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
        username = self.entry_username.get().lower()
        password = self.entry_password.get().lower()
        confirm_password = self.entry_password_confirm.get()

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
        users[username] = {"password": password, "saved_products": []}

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
        username = self.entry_username.get().lower()
        password = self.entry_password.get().lower()

        # Load user data from JSON file
        try:
            with open("users.json", "r") as f:
                users = json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Error", "User data file not found.")
            return

        # Check if the username exists and the password matches
        if username in users and users[username]["password"] == password:
            self.controller.current_user = username
            messagebox.showinfo("Login Successful", f"Welcome, {username}!")
            self.controller.show_frame("main")
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")



class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.images = load_menu_images()

        #TKinter GUI setup
        # logo frame
        logo_frame = tk.Frame(self, bg="white")
        logo_frame.pack(side=tk.TOP, fill=tk.X)
        tk.Label(logo_frame, image=self.images["logo"], bg="white").pack(side=tk.LEFT, padx=10, pady=10)
        logo_label = tk.Label(logo_frame, text="PriceWise", font=("Arial", 12), bg="white")
        logo_label.pack(side=tk.LEFT)

        # menu frame
        menu_frame = tk.Frame(self, bg="white", width=200, height=700)
        menu_frame.pack(side=tk.LEFT, fill=tk.Y)
        menu_frame.pack_propagate(False)
        build_menu(menu_frame, self.controller, self.images, active_page="main")

        # right content area
        content_frame = tk.Frame(self, bg="#F1EFE8")
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        big_title = tk.Label(content_frame, text="Compare grocery prices", font=("Arial", 22, "bold"), bg="#F1EFE8")
        big_title.pack(anchor="w", padx=20, pady=(20, 5))

        subtitle = tk.Label(content_frame, text="Find the cheapest option across supermarkets", font=("Arial", 10), fg="#9E9E9E", bg="#F1EFE8")
        subtitle.pack(anchor="w", padx=20, pady=(0, 15))

        search_row = tk.Frame(content_frame, bg="#F1EFE8")
        search_row.pack(anchor="w", padx=20, pady=(0, 15))
        tk.Label(search_row, image=self.images["search"], bg="white").pack(side=tk.LEFT, padx=(0, 5))
        self.entry_search = tk.Entry(search_row, width=40)
        self.entry_search.pack(side=tk.LEFT, padx=5)
        tk.Button(search_row, text="Search", bg="#0F6E56", fg="white",
                  command=lambda: self.search(self.entry_search.get())).pack(side=tk.LEFT, padx=5)

        # three result rows: supermarket name left, price right
        self.results_frame = tk.Frame(content_frame, bg="#F1EFE8")
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
        parsed_items = [parse_line(line) for line in lines if parse_line(line) is not None]

        for line in lines:
            item = parse_line(line)
            if item is not None:
                parsed_items.append(item)

        key = cleaned_query.lower()
        parsed_items = [item for item in parsed_items if key in item["name"].lower()]

        parsed_items.sort(key=lambda item: item["unit_price"])

        #group by (name, supermarket) so we can compare the latest price to the previous one
        groups={}
        for item in parsed_items:
            groups.setdefault((item["name"], item["supermarket"]), []).append(item)

        latest_per_group = []
        for group_items in groups.values():
            group_items.sort(key=lambda item: item["date"] or "")
            latest = group_items[-1]
            previous = group_items[-2] if len(group_items) > 1 else None
            percent_change = None
            if previous and previous["price"]:
                percent_change = (previous["price"] - latest["price"]) / previous["price"] * 100
            latest["percent_change"] = percent_change
            latest_per_group.append(latest)

        latest_per_group.sort(key=lambda item: item["unit_price"])

        # clear previous results from each row
        for row in self.result_rows:
            for widget in row.winfo_children():
                widget.destroy()

        if not latest_per_group:
            messagebox.showinfo("No Results", f"No products found matching '{cleaned_query}'")
            return
        #display the top 3 results in the result rows
        for item, row in zip(latest_per_group, self.result_rows):
            left_col = tk.Frame(row, bg="white")
            left_col.pack(side=tk.LEFT, padx=10, pady=10)
            tk.Label(left_col, text=item["supermarket"], bg="white").pack(anchor="w")
            tk.Label(left_col, text=item["date"] or "", fg="#9E9E9E", bg="white", font=("Arial", 8)).pack(anchor="w")

            right_col = tk.Frame(row, bg="white")
            right_col.pack(side=tk.RIGHT, padx=10, pady=10)
            tk.Label(right_col, text=f"${item['price']:.2f}", bg="white").pack(anchor="e")

            #if there is a percent change, display it with a sign and color
            if item["percent_change"] is not None:
                sign = "-" if item["percent_change"] > 0 else "+"
                tk.Label(
                    right_col, text=f"{sign}{abs(item['percent_change']):.0f}%",
                    bg="#FDEBD0", fg="#E67E22", font=("Arial", 8, "bold"),
                    relief="solid", bd=1, padx=4,
                ).pack(anchor="e", pady=(2, 0))

class DiscountPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
    
        self.images = load_menu_images()

        self.configure(bg="#F1EFE8")
        self.create_widgets()

    #page layout for the discount page
    def create_widgets(self):
        # logo frame
        logo_frame = tk.Frame(self, bg="white")
        logo_frame.pack(side=tk.TOP, fill=tk.X)
        tk.Label(logo_frame, image=self.images["logo"], bg="white").pack(side=tk.LEFT, padx=10, pady=10)
        logo_label = tk.Label(logo_frame, text="PriceWise", font=("Arial", 12), bg="white")
        logo_label.pack(side=tk.LEFT)


        # menu frame
        menu_frame = tk.Frame(self, bg="white", width=200, height=700)
        menu_frame.pack(side=tk.LEFT, fill=tk.Y)
        menu_frame.pack_propagate(False)

        build_menu(menu_frame, self.controller, self.images, active_page="discount")

        # right content area
        content_frame = tk.Frame(self, bg="#F1EFE8")
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        title_row = tk.Frame(content_frame, bg="#F1EFE8")
        title_row.pack(fill=tk.X, padx=20, pady=(20, 5))

        big_title = tk.Label(title_row, text="Discount alerts", font=("Arial", 22, "bold"), bg="#F1EFE8")
        big_title.pack(side=tk.LEFT)

        add_button = tk.Button(title_row, text="+ Add products", bg="#F1EFE8", fg="black", bd=0, relief="flat", highlightthickness=0, cursor="hand2", font=("Arial", 10), command=self.add_product,)
        add_button.pack(side=tk.RIGHT)

        subtitle = tk.Label(content_frame, text="You'll be notified when a price drops on your saved products", font=("Arial", 10), fg="#9E9E9E", bg="#F1EFE8")
        subtitle.pack(anchor="w", padx=20, pady=(0, 15))

        #saved products get listed here, refreshed by refresh_discount_list
        self.discount_frame = tk.Frame(content_frame, bg="#F1EFE8")
        self.discount_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def add_product(self):
        save_name = simpledialog.askstring("Add product", "Product name to track:")
        if not save_name:
            return
        save_name = save_name.strip().lower()

        lines = load_lines()
        matches = [parse_line(l) for l in lines if parse_line(l) is not None]
        matches = [item for item in matches if save_name in item["name"].lower()]
        if not matches:
            messagebox.showerror("Not found", f"No product matching '{save_name}' in list.txt")
            return

        with open("users.json", "r") as f:
            users = json.load(f)

        saved = users[self.controller.current_user]["saved_products"]
        if save_name not in saved:
            saved.append(save_name)

        with open("users.json", "w") as f:
            json.dump(users, f)

        self.refresh_discount_list()

    def on_show(self):
        self.refresh_discount_list()

    def refresh_discount_list(self):
        for widget in self.discount_frame.winfo_children():
            widget.destroy()

        if not self.controller.current_user:
            return

        with open("users.json", "r") as f:
            users = json.load(f)
        saved_names = users[self.controller.current_user]["saved_products"]

        lines = load_lines()
        all_items = [parse_line(l) for l in lines if parse_line(l) is not None]

        for save_name in saved_names:
            candidates = [item for item in all_items if save_name.lower() in item["name"].lower()]
            if not candidates:
                continue
            cheapest = min(candidates, key=lambda item: item["unit_price"])
            row = tk.Frame(self.discount_frame, bg="white")
            row.pack(fill=tk.X, pady=5)
            tk.Label(row, text=f"{cheapest['name']} ({cheapest['supermarket']})", bg="white").pack(side=tk.LEFT, padx=10)
            tk.Label(row, text=f"${cheapest['price']:.2f}", bg="white").pack(side=tk.RIGHT, padx=10)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Price Comparison System")
        self.geometry("700x600")

        self.img_logo = ImageTk.PhotoImage(Image.open("Logo.png").resize((50, 50)))

        self.current_user = None
        self.frames = {}

        self.frames["signup"] = SignUpPage(self, self)
        self.frames["login"] = LoginPage(self, self)
        self.frames["main"] = MainPage(self,self)
        self.frames["discount"] = DiscountPage(self,self)
        

        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.show_frame("login")
    def show_frame(self, page_name):
        frame = self.frames[page_name]
        if hasattr(frame, "on_show"):
            frame.on_show()
        frame.tkraise()
    

if __name__ == "__main__":
    app = App()
    app.mainloop()