import tkinter as tk
from tkinter import ttk
from tkinter import*
import pandas as pd


class OptionsPage(tk.Frame):
    def __init__(self, parent, controller,bg="white"):
        tk.Frame.__init__(self, parent)


        left = Frame(self, borderwidth=2, relief="solid")
        right = Frame(self, borderwidth=2, relief="solid")


        left.pack(side="left", expand=True, fill="both")    #
        right.pack(side="right", expand=True, fill="both")  #



