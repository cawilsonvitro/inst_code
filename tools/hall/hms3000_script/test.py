# import tkinter as tk

# def changed(*args):
#     print("You changed the selection. The new selection is %s." % clicked.get())


# root = tk.Tk()

# OPTIONS = list(range(8))

# clicked = tk.StringVar(master=root) # Always pass the `master` keyword argument
# clicked.set(OPTIONS[0]) # default value
# clicked.trace("w", changed)

# drop = tk.OptionMenu(root, clicked, *OPTIONS)
# drop.pack()

# root.mainloop()


import tkinter as tk
from tkinter import ttk

tkwindow = tk.Tk()

cbox = ttk.Combobox(tkwindow, values=[1,2,3], state='readonly')
cbox.grid(column=0, row=0)


def callback(eventObject):
    print(eventObject)

cbox.bind("<<ComboboxSelected>>", callback)

tkwindow.mainloop()