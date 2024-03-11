import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import ttk


def make_lst_box(parent_comp, name):
    listbox = Listbox(parent_comp, height=23,
                      width=20,
                      bg="grey",
                      activestyle='dotbox',
                      font="Helvetica",
                      fg="yellow")

    listlbl = Label(parent_comp, text=name)
    listlbl.pack()
    listbox.pack()
    return listbox
