#This is a price comparison system. 
#In V1, I need to implement an input search function and sort the results. 
#I also need to use TKinter to help me write a GUI.

import os#this is used to get the current file path and read the list.txt file.
import re#this is used to parse the price and quantity from the input string.
import tkinter as tk
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


def search(query):
    # only allow a word with at least 2 letters (no spaces, no single letter)
    cleaned_query = query.strip()
    if not cleaned_query or " " in query or len(cleaned_query) == 1 or not re.fullmatch(r"[A-Za-z]+", cleaned_query):
        messagebox.showerror("Input Error", "Please enter a valid word (at least 2 letters, no spaces).")
        result_text.delete("1.0", tk.END)
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
    result_text.delete("1.0", tk.END)
    if not parsed_items:
        #If no comparable products were found, display a message in the result_text widget.
        result_text.insert(tk.END, "No comparable products were found.")
        return

    #Sort by unit price and display the most affordable items.
    parsed_items.sort(key=lambda item: item["unit_price"])
    #Get the most affordable item
    best = parsed_items[0]

    result_text.insert(
        tk.END,
        "Most affordable items:\n"
        f"{best['name']} | ${best['price']:.2f} | {best['quantity']}{best['unit']} | "
        f"${best['unit_price']:.4f}/{best['base_unit']} | {best['supermarket']}\n\n"
    )
    result_text.insert(tk.END, "Sort by unit price (low -> high):\n")

    for i, item in enumerate(parsed_items, start=1):
        result_text.insert(
            tk.END,
            f"{i}. {item['name']} | ${item['price']:.2f} | {item['quantity']}{item['unit']} | "
            f"${item['unit_price']:.4f}/{item['base_unit']} | {item['supermarket']}\n",
        )
#TKinter GUI setup
windows = tk.Tk()
windows.title("Price Comparison System")
windows.geometry("700x600")

# title label
title_frame = Frame(windows, bg="lightblue", width=700, height=50)
title_frame.pack(fill=tk.X)
title_label = tk.Label(title_frame, text="Price Comparison System", font=("Arial", 20), bg="lightblue")
title_label.pack(pady=10)

# logo frame
logo_frame = tk.Frame(windows, bg="lightblue", width=100, height=50)
logo_frame.place(x=10, y=10)    
logo_label = tk.Label(logo_frame, text="Logo", font=("Arial", 12), bg="lightblue")
logo_label.pack(pady=10)

# menu frame
menu_frame = tk.Frame(windows, bg="brown", width=50, height=700)
menu_frame.pack(side=tk.LEFT, fill=tk.X)
menu_label = tk.Label(menu_frame, text="Menu", font=("Arial", 12), bg="brown", height=700)
menu_label.pack(pady=10)

# search frame
search_frame = tk.Frame(windows, bg="yellow", width=700, height=50)
search_frame.pack(fill=tk.X)
search_label = tk.Label(search_frame, text="Enter product name:", font=("Arial", 12), bg="yellow")
search_label.pack(pady=10)

product_name = tk.Entry(search_frame, width=60)
product_name.pack(pady=10, side=tk.LEFT, padx=8)
button = tk.Button(search_frame, text="Search", command=lambda: search(product_name.get()))
button.pack(pady=10, side=tk.RIGHT, padx=8)

# result frame
result_frame = tk.Frame(windows, bg="lightgreen", width=700, height=500)
result_frame.pack(fill=tk.BOTH, expand=True)
result_label = tk.Label(result_frame, text="Results", font=("Arial", 12), bg="lightgreen")
result_label.pack(pady=10)


result_text = tk.Text(result_frame, width=80, height=24)
result_text.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

windows.mainloop()

