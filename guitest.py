from tkinter import *
from tkinter import ttk

root = Tk()
root.geometry("200x200")

def show():
    lbl.config(text=cb.get())

# Dropdown options  
a = ["Apple", "Banana", "Cherry", "Date", "Elderberry"]

# Combobox  
cb = ttk.Combobox(root, values=a)
cb.set("Select a fruit")
cb.pack()

# Button to display selection  
Button(root, text="Show Selection", command=show).pack()

# Label to show selected value  
lbl = Label(root, text=" ")
lbl.pack()

root.mainloop()