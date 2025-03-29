import os
import csv

from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog

root = tk.Tk()

# Global Variable
directory = None
csv_file = "ucl.csv"
original_data = [] #

# Wrapper Section
wrapper1 = LabelFrame(root, text="Search")
wrapper2 = LabelFrame(root, text="Folder List")

wrapper1.pack(fill="both", expand=False, padx=20, pady=10)
wrapper2.pack(fill="both", expand=True, padx=20, pady=10)


# Search Events
def search():
    query = search_entry.get().lower()
    tree.delete(*tree.get_children())

    for item in original_data:
        if query in item[0].lower():
            tree.insert("", "end", values=item)

def reset_search():
    search_entry.delete(0, tk.END)
    tree.delete(*tree.get_children())

    for item in original_data:
        tree.insert("", "end", values=item)

# Search
search_entry = tk.Entry(wrapper1, width=60)
search_entry.pack(side="left", padx=10, pady=10)

btn_search = tk.Button(wrapper1, text="Search", command=search)
btn_search.pack(side="left", padx=5)

btn_reset = tk.Button(wrapper1, text="Reset", command=reset_search)
btn_reset.pack(side="right", padx=5)


# TreeView Events
def on_click(event):
    item_id = tree.identify_row(event.y)  # Dapatkan item yang diklik
    column_id = tree.identify_column(event.x)  # Kolom yang diklik (misalnya "#3" untuk kolom ke-3)
    
    if item_id and column_id in ("#3", "#4"):  # Hanya untuk kolom checkbox
        toggle_checkbox(item_id, int(column_id[1]) - 1)

# TreeView
columns = ("Name", "Type", "Long Video", "Short Video")
tree = ttk.Treeview(wrapper2, columns=columns, show="headings", height=6)

# Scrollbar Vertikal
scroll_y = ttk.Scrollbar(wrapper2, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scroll_y.set)

# Scrollbar Horizontal
scroll_x = ttk.Scrollbar(wrapper2, orient="horizontal", command=tree.xview)
tree.configure(xscrollcommand=scroll_x.set)

# Menempatkan Scrollbar dan Treeview dalam frame
scroll_y.pack(side="right", fill="y")
scroll_x.pack(side="bottom", fill="x")

# Bind event klik ke Treeview
tree.bind("<Button-1>", on_click)
tree.pack(fill="both", expand=True, padx=10, pady=10)

# header columns
for col in columns:
    tree.heading(col, text=col)
    if col != "Name":
        tree.column(col, width=10)


## Events
def open_directory():
    global directory
    directory = filedialog.askdirectory()
    if not directory:
        return
    
    directory_sync()

def directory_sync():
    global csv_file

    if not directory:
        return 
    
    # clear data
    tree.delete(*tree.get_children())
    original_data.clear()

    csv_file = os.path.join(directory, csv_file)

    # check if csv exist, if not make new
    if not os.path.exists(csv_file):
        with open(csv_file, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(columns) # Header

    # read csv to hold checkbox state
    checkbox_data = {}
    with open(csv_file, mode="r", newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader, None)
        for row in reader:
            # save row 2 long_video, row 3 short_video
            checkbox_data[row[0]] = [row[2], row[3]]

    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        item_type = "Folder" if os.path.isdir(item_path) else "File"

        # if folder/file is new, set default checkbox "No"
        checkbox_value = checkbox_data.get(item, ["No", "No"])

        values = (item, item_type, checkbox_value[0], checkbox_value[1])

        tree.insert("", "end", values=values)
        original_data.append(values)
    
    save_to_csv()

def save_to_csv():
    with open(csv_file, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(columns) #header

        for row_id in tree.get_children():
            row = tree.item(row_id)["values"]
            writer.writerow(row)

def toggle_checkbox(item_id, col_idx):
    values = tree.item(item_id, "values")
    new_values = list(values)
    
    answer = messagebox.askyesno("Confirmation", "Are you sure?")

    if answer:
        # Ubah status checkbox (True <-> False)
        new_values[col_idx] = "Yes" if new_values[col_idx] == "No" else "No"
    
    # Perbarui tampilan
    tree.item(item_id, values=new_values)

    save_to_csv()

# Menu Bar
menubar = Menu(root)

## File Menu
file = Menu(menubar, tearoff=0)
menubar.add_cascade(label="File", menu=file)
file.add_command(label="Open Folder", command=open_directory)

## Help Menu
def show_about():
    messagebox.showinfo("Information About", 
                        "This program is intended to help checklist about upload video!"
                        "\nif youre content creator hopefully this program help you which folder that contain video that already uploaded"
                        "\nucl.csv will be created automaticaly to save and track cheklist"
                        "\n\nby @logicxscale @bagusa4 for @unboxgapid projects"
                        "\nhttps://github.com/logicxscale/ucl.git"
                        "")
menubar.add_cascade(label="About", command=show_about)

# Debug


# Sync each 5 seconds
def auto_update():
    directory_sync()
    root.after(5000, auto_update)

## Main
root.title("UCL - Upload Check List")
root.geometry("800x800")
root.config(menu=menubar)
root.after(5000, auto_update) # start sync folder
root.mainloop()