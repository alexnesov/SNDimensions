import os
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.animation as animation
from matplotlib import style
import matplotlib.dates as mdates
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, AutoMinorLocator)
from matplotlib import pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.ticker as plticker
from PIL import ImageTk,Image 
import tkinter as tk
from tkinter import ttk
from tkinter import*
from tkinter import PhotoImage
import sqlite3
import numpy as np
import pandas as pd
from pandas import DataFrame
import re
import datetime
from bs4 import BeautifulSoup
import requests
import bs4  
from csv import writer
import csv
import time
import yfinance as yf

import DB_Access as db
import OptionsPage as op

try:
    os.chdir(f'{os.path.dirname(os.path.realpath(__file__))}') 
except OSError:
    pass
    
# STYLING
LARGE_FONT= ("Arial", 13)
NORM_FONT= ("Arial", 10)
SMALL_FONT= ("Arial", 9)
darkColor = '#406441'
lightColor = '#03F36F'
indexColor='#AD21C3'

f_real_time = plt.figure(1)
chartLoad = True

stock = "MSFT"
intra_ticker = "msft"
index="^GSPC"



def changeChartLoad(toWhat):
    global chartLoad
    global update_job
    if toWhat == "Running":
        chartLoad = True
        app.after(10000, live_update)
    elif toWhat == "Stopped":
        chartLoad = False
        app.after_cancel(update_job)


class Trading_app(tk.Toplevel):
    def __init__(self, *args, **kwargs):  #args = variables, kwargs=dictionnaries
        
        tk.Toplevel.__init__(self, *args, **kwargs)
        tk.Toplevel.wm_title(self, "SN Dimensions")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        menubar = tk.Menu(container)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Save settings", command = lambda: tk.messagebox.showinfo(title="Information",  message="Not supported yet"))
        filemenu.add_separator()
        filemenu.add_command(label="Exit        (F1)", command=ShutProgram)
        menubar.add_cascade(label="File", menu=filemenu)

        Real_time = tk.Menu(menubar, tearoff=0)
        Real_time.add_command(label="Real time data     (F2)",
                            command=lambda: self.show_frame(Real_Time_data))                          
        menubar.add_cascade(label="Real time data", menu=Real_time)

        Static_graphs = tk.Menu(menubar, tearoff=0)
        Static_graphs.add_command(label="Static Graphs Page        (F3)",
                            command=lambda: self.show_frame(StaticGraphsPage))                          
        menubar.add_cascade(label="Static graphs", menu=Static_graphs)

        FinDL = tk.Menu(menubar, tearoff=0)
        FinDL.add_command(label="Stocks     (F4)",
                                command = lambda: self.show_frame(Pricesdownloader))
        menubar.add_cascade(label="Financials downloader", menu=FinDL)

        Options = tk.Menu(menubar, tearoff=0)
        Options.add_command(label="Options",
                                command = lambda: self.show_frame(op.OptionsPage))
        menubar.add_cascade(label="Options", menu=Options)

        TimeSeries = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Time Series Analysis", menu=TimeSeries)

        tk.Tk.config(self, menu=menubar) 

        self.frames = {}

        for F in (StartPage, Real_Time_data, StaticGraphsPage, Pricesdownloader, op.OptionsPage):                       ######### PAGES

            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column = 0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

class StartPage(tk.Frame):
    def __init__(self, parent, controller,bg="white"):
        tk.Frame.__init__(self, parent)
        photo = PhotoImage(file = f'{os.path.dirname(os.path.realpath(__file__))}\\finance1.gif')
        label = ttk.Label(self, text=("Alpha version of SN Dimensions, use at yor own risk."),
         font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button1 = ttk.Button(self, text="Agree", cursor='hand2',
                            command=lambda: controller.show_frame(Real_Time_data))
        button1.pack()

        button2 = ttk.Button(self, cursor='hand2', text="Disagree", command=ShutProgram)
        button2.pack()

        box = tk.Frame(self)                                                     # new container
        box.pack()    

        gif = ttk.Label(box,image = photo,anchor=tk.CENTER)
        gif.image = photo
        gif.grid(column=0, row=3)

def save(live_update_list):
    with open(f'{os.path.dirname(os.path.realpath(__file__))}\\Data\\{intra_ticker}_intra.csv', 'a+', newline='') as write_obj:
        # Create a writer object from csv module
        csv_writer = writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(live_update_list)

def live_update(*args):
    global live_update_list
    global update_job
    df = yf.download("msft", period = "1d", interval = "1m").tail(1)
    df= df.reset_index()
    df['Datetime'] = df['Datetime'].astype('datetime64[ns]') 
    df['Datetime'] = df['Datetime'].dt.tz_localize(None)
    df['Datetime'] = df['Datetime'].astype(str)
    live_update_list = df[['Datetime', 'Open', 'High','Low','Close','Adj Close']].values.tolist()[0]
    save(live_update_list)
    update_job = app.after(15000, live_update)
    pass
    # return live_update_list

def animate(i):
    if chartLoad:
        from datetime import date
        f_real_time = plt.figure(1)
        a = plt.subplot2grid((6,2), (0,0), rowspan = 2, colspan = 4)
        v = plt.subplot2grid((6,2), (2,0), rowspan = 2, colspan = 4,sharex=a)
        index_plot = plt.subplot2grid((6,2), (4,0), rowspan = 2, colspan = 4,sharex=a)
        # SP 1
        df = pd.read_csv(f'C:\\Users\\alexa\\OneDrive\\Desktop\\SN Dimensions\\Data\\{intra_ticker}_intra.csv')
        df['Datetime'] = df['Datetime'].astype('datetime64[ns]')
        # SP 2
        dateStamps = df['Datetime']
        volume = df["Volume"]
        # SP 3
        df_index = pd.read_csv(f'C:\\Users\\alexa\\OneDrive\\Desktop\\SN Dimensions\\Data\\{index}_intra.csv')
        df_index['Datetime'] = df['Datetime'].astype('datetime64[ns]')

        a.clear()
        v.clear()
        index_plot.clear()

        a.plot("Datetime", "Open", data=df, color= lightColor, 
                                label="Open", linewidth=1, alpha=0.8)
        a.plot("Datetime", "Close", data=df, color= darkColor, 
                                label="Close", linewidth=1, linestyle="dashed", alpha=0.8)
        index_plot.plot("Datetime", "Open", data=df_index, color=indexColor, 
                                label="Open", linewidth=1, alpha=0.8)

        a.xaxis.set_minor_locator(AutoMinorLocator()) 
        a.format_xdata = mdates.DateFormatter('%H-%M-%S')
        v.fill_between(dateStamps , 0, volume, color=lightColor, alpha=0.6, edgecolor=lightColor)
        a.set_ylabel(f"Price - {stock}")
        v.set_ylabel("Volume")
        index_plot.set_ylabel("SP500")
        a.spines['top'].set_visible(False)
        a.spines['right'].set_visible(False)
        v.spines['top'].set_visible(False)
        v.spines['right'].set_visible(False)
        index_plot.spines['top'].set_visible(False)
        index_plot.spines['right'].set_visible(False)
        a.grid(color='grey', linestyle='-', linewidth=0.25, alpha=0.6)
        v.grid(color='grey', linestyle='-', linewidth=0.25, alpha=0.6)
        index_plot.grid(color='grey', linestyle='-', linewidth=0.25, alpha=0.6)

        plt.setp(a.get_xticklabels(), visible = False)
        plt.setp(v.get_xticklabels(), visible = False)

        # f_real_time.autofmt_xdate()
        a.legend(bbox_to_anchor=(0, 1.02, 1, .102), loc=3, ncol=2, borderaxespad=0)
    else:
        pass

class Real_Time_data(tk.Frame):
    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent,bg="white")
        label = ttk.Label(self, text="Real time data", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        box1 = tk.Frame(self, bg="white")                                                       # new container
        box1.pack(side="top")  

        def icon_change_resume_pause():
            if chartLoad == True:
                rec5.configure(bg="green")  
            else:
                rec5.configure(bg="red") 

        def start_stop_client():
            r_s = v_start_stop.get()
            changeChartLoad(r_s)
            print("It's:" + v_start_stop.get())

        b_refresh = ttk.Button(box1, cursor='hand2', text="Refresh",
                            command=lambda:[db.dl_quote_intraday(intra_ticker), 
                            db.dl_index_intraday(index)]
                            )
        b_refresh.pack(side="left",padx=5, pady=5,fill=tk.Y)


        # Run/Stop of the client
        RUN = ['Running', 'Stopped']    
        v_start_stop = tk.StringVar(self)
        v_start_stop.set(RUN[0])
        rec5 = tk.OptionMenu(box1, v_start_stop, *RUN)
        rec5.config(bg="green",fg="white")
        rec5.pack(side="left")
        b_run_val = tk.Button(box1, cursor='hand2', text="OK", command=lambda:[start_stop_client(),icon_change_resume_pause()])
        b_run_val.pack(side="left",padx=5, pady=5,fill=tk.Y)

        canvas = FigureCanvasTkAgg(f_real_time, self)
        canvas.draw()
        toolbar = NavigationToolbar2Tk(canvas, self)
        color = "#FFFFFF"
        toolbar.config(background=color)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

class StaticGraphsPage(tk.Frame):
    def __init__(self, parent, controller):
        
        tk.Frame.__init__(self, parent)

        f_static = plt.figure(2)

        def stock_selection(variable):
            s = variable.get()
            changeStock(s)
            print ("value is:" + variable.get())

        def changeStock(toWhat):
            global stock
            stock = toWhat

        def plot():
            f_static = plt.figure(2)
            self.ax3 = plt.subplot2grid((6,4), (0,0), rowspan = 5, colspan = 4)
            self.ax4 = plt.subplot2grid((6,4), (5,0), rowspan = 1, colspan = 4, sharex = self.ax3)

            self.ax3.clear()
            self.ax4.clear()

            static_p_entry_stock = str(self.static_stock.get())
            if "^" in static_p_entry_stock:
                static_p_entry_stock = static_p_entry_stock.replace("^", "")
            static_p_period = str(self.time_period.get())

            df = db.read_db(static_p_entry_stock,static_p_period)
            df.reset_index()
            df['Date']= pd.to_datetime(df['Date'])
            dateStamps = pd.to_datetime(df['Date'])
            volume = df["Volume"]

            self.ax3.plot("Date", "Open", data=df, color= lightColor, 
                                        label="Open", linewidth=1, alpha=0.8)
            self.ax3.plot("Date", "Close", data=df, color= lightColor, 
                            label="Close",linestyle="dashed", linewidth=1, alpha=0.8)                          

            self.ax3.xaxis.set_ticks_position('none') 
            self.ax3.spines['top'].set_visible(False)
            self.ax3.spines['right'].set_visible(False)
            self.ax4.spines['top'].set_visible(False)
            self.ax4.spines['right'].set_visible(False)
            self.ax3.set_ylabel(f"Price - {stock.upper()}")
            self.ax4.set_ylabel("Volume")
            self.ax3.legend(bbox_to_anchor=(0, 1.02, 1, .102), loc=3, ncol=2, borderaxespad=0)
            self.ax3.grid(color='grey', linestyle='-', linewidth=0.25, alpha=0.6)
            self.ax4.grid(color='grey', linestyle='-', linewidth=0.25, alpha=0.6)
            self.ax4.fill_between(dateStamps , 0, volume, color=lightColor, alpha=0.6, edgecolor=lightColor)

            self.ax3.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))  
            self.ax3.get_xaxis().get_offset_text().set_position((2,0))
            
            f_static.autofmt_xdate()
            title=f"Prices for {static_p_entry_stock}. Period: {static_p_period}."
            self.ax3.set_title(title)
            self.canvas.draw()


        label = ttk.Label(self, text="Graph Page", font=LARGE_FONT)
        label.pack(pady=10,padx=10)
        box1 = tk.Frame(self)                                                       # new container
        box1.pack(side="top")                                                       # new container

        # Available tables
        con = sqlite3.connect(f'{os.path.dirname(os.path.realpath(__file__))}\\Data\\1 Week.db3')
        mycur = con.cursor() 
        mycur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        available_table=(mycur.fetchall())
        con.close()
        global av_stocks_list
        av_stocks_list = []

        for i in range(len(available_table)):
            test = available_table[i][0]
            av_stocks_list.append(test)
        av_stocks_list = list(map(lambda x:x.upper(),av_stocks_list))
        
        rectangle = tk.Label(box1,width=10)                                                  # just some filling
        b1 = tk.Button(box1, text="Back to Home",cursor='hand2',
                    command=lambda: controller.show_frame(StartPage))

        rectangle2 = tk.Label(box1, text="Select stock:")      
        self.static_stock = tk.StringVar(self)
        self.static_stock.set(av_stocks_list[0])
        
        b2 = tk.OptionMenu(box1, self.static_stock, *av_stocks_list)
        timeFrame = ["1 Week","60 Days", "5 Years" ]
        self.time_period = tk.StringVar(self)
        self.time_period.set(timeFrame[2])                             
        menu_timeFrame = tk.OptionMenu(box1, self.time_period, *timeFrame)
        b4_stock_val = (tk.Button(box1, text="Generate plot",bg="green", fg="white",cursor='hand2', 
        command=lambda:[stock_selection(self.static_stock),plot()]
        ))
        
        #                                           ***LAYOUT***
        b1.pack(side="left", padx=5, pady=5,fill=tk.Y)
        rectangle.pack(side="left",padx=5, pady=5,fill=tk.Y)                         # just some filling    
        rectangle2.pack(side="left",padx=5, pady=5,fill=tk.Y)             
        b2.pack(side="left",padx=5, pady=5,fill=tk.Y)
        menu_timeFrame.pack(side="left", padx=5, pady=5,fill=tk.Y)
        b4_stock_val.pack(side="left",padx=5, pady=5,fill=tk.Y)

        # CANVAS
        self.canvas = FigureCanvasTkAgg(f_static, self)
        plot() # just calling the above function to have an already plotting graph when openning page

        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        color = "#FFFFFF"
        self.toolbar.config(background=color)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

class Pricesdownloader(tk.Frame):
 def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        b1 = tk.Button(self, text="Back to Home",cursor='hand2',
                            command=lambda: controller.show_frame(StartPage))
        b1.pack(side="top", padx=5, pady=5)

        #===================================================================== Left
        
        Left = tk.Frame(self)                                          
        Left.pack(side="left", expand=True, fill="both")   
        # Left.configure(background='blue')

        boxL1 = tk.Frame(Left, relief="solid",borderwidth=1)
        boxL1b = tk.Frame(Left, relief="solid",borderwidth=1)
        self.boxL2 = tk.Frame(Left, relief="solid",borderwidth=1)

        boxL1.pack(expand=True, fill="both", padx=10, pady=10)
        boxL1b.pack(expand=True, fill="both", padx=10, pady=10)
        self.boxL2.pack(expand=True, fill="both", padx=10, pady=10)
                                        
                                        # -- Widgets -- L2

        self.promptTitle = ttk.Label(self.boxL2, text="Prompt", font=LARGE_FONT)
        self.promptTitle.pack()

        self.prompt = ttk.Label(self.boxL2)
        self.prompt.pack()

        #                                  -- Widgets -- L1
        # Labels
        label = ttk.Label(boxL1, text="Prices downloader", font=LARGE_FONT)
        type_stock_symbol = ttk.Label(boxL1, text="Stock symbol:", font=NORM_FONT)
        Choose_interval = ttk.Label(boxL1, text="Time interval:", font=NORM_FONT)

        # Entry
        self.entry_stringvar = tk.StringVar(self)
        entry = ttk.Entry(boxL1, textvariable=self.entry_stringvar, width=15)

        def get_entry_stock_and_period():
            global entry_stock
            entry_stock = str(self.entry_stringvar.get())
            self.prompt = ttk.Label(self.boxL2, text=f"{entry_stock.upper()} chosen." ,justify=LEFT)
            self.prompt.pack(anchor=W)
            global period
            period = str(self.time_period.get())

            print(entry_stock+' chosen')

        # TimeFrame choice
        timeFrame = ["1 Week","60 Days", "5 Years" ]
        self.time_period = tk.StringVar(self)
        self.time_period.set(timeFrame[0])                                              # default value
        menu_timeFrame = tk.OptionMenu(boxL1, self.time_period, *timeFrame)
 
        # Select & DL buttons
        b_download = (tk.Button(boxL1, text="Download",bg="green",fg="white", cursor='hand2',
                    command=lambda:[get_entry_stock_and_period(),db.dl_quotes(self, self.boxL2, entry_stock, period)])
                    )

        # -- Layout -- L1
        label.grid(row=0,columnspan=4,padx=5, pady=5,stick="we")
        # ROW 1
        type_stock_symbol.grid(row=1, column=0)
        entry.grid(row=1, column=1, stick="we",padx=5, pady=5)
        # ROW 2
        Choose_interval.grid(row=2, column=0)
        menu_timeFrame.grid(row=2, column=1, stick="we",padx=5, pady=5)
        # ROW 3
        b_download.grid(row=3,columnspan=4,padx=5, pady=5,stick="we")

                                                    # -- Widgets -- L1b

        label_display = ttk.Label(boxL1b, text="Table display selection", font=LARGE_FONT)
        type_stock_symbol_display = ttk.Label(boxL1b, text="Stock symbol:", font=NORM_FONT)
        Choose_interval_display = ttk.Label(boxL1b, text="Time interval:", font=NORM_FONT)

        entry_stringvar_display = tk.StringVar()
        entry_display = ttk.Entry(boxL1b, textvariable=entry_stringvar_display, width=15)
        menu_timeFrame = tk.OptionMenu(boxL1b, self.time_period, *timeFrame)
        b_display = tk.Button(boxL1b,cursor='hand2', text="Display",bg="blue",fg="white",
         command=lambda:[new_tree()])

        # -- Layout -- L1b
        label_display.grid(row=0,columnspan=4,padx=5, pady=5,stick="we")
        # ROW 1
        type_stock_symbol_display.grid(row=1, column=0)
        entry_display.grid(row=1, column=1, stick="we",padx=5, pady=5)
        # ROW 2
        Choose_interval_display.grid(row=2, column=0)
        menu_timeFrame.grid(row=2, column=1, stick="we",padx=5, pady=5)
        # ROW 3
        b_display.grid(row=3,columnspan=4,padx=5, pady=5,stick="we")

        #===================================================================== Right
        Right = tk.Frame(self)                                                    
        Right.pack(side="right", fill="both") 

        boxR1 = tk.Frame(Right, relief="solid")
        boxR2 = tk.Frame(Right, relief="solid")
        boxR1.pack(expand=True, fill="both", padx=10, pady=10)

        def new_tree():
            tree.delete(*tree.get_children())   # " * " stands for 
            # with open(f"C:\\Users\\alexa\\OneDrive\\Desktop\\SN Dimensions\\Data\\insg.csv") as f:
            #     reader = csv.DictReader(f, delimiter=',')
            #     for row in reader:
            #         Date = row['Date']
            #         Open = row['Open']
            #         High = row['High']
            #         Low = row['Low']
            #         Close = row['Close']
            #         tree.insert("", 0, values=(Date, Open, High, Low, Close, Adj_Close, Volume))

        #=========================================== RIGHT SOUTH  CONTAINER
        # INITIAL TREEVIEW
        TableMargin = tk.Frame(boxR1, width=700)
        TableMargin.pack(side="bottom")
        scrollbarx = Scrollbar(TableMargin, orient=HORIZONTAL)
        scrollbary = Scrollbar(TableMargin, orient=VERTICAL)
        tree = (ttk.Treeview(TableMargin, columns=("Datetime", "Open", "High", "Low", "Close", "Adj Close", "Volume"), 
                height=400, selectmode="extended", 
                yscrollcommand=scrollbary.set, xscrollcommand=scrollbarx.set)
                )
        scrollbary.config(command=tree.yview)
        scrollbary.pack(side=RIGHT, fill=Y)
        scrollbarx.config(command=tree.xview)
        scrollbarx.pack(side=BOTTOM, fill=X)
        tree.heading('Datetime', text="Date", anchor=W)
        tree.heading('Open', text="Open", anchor=W)
        tree.heading('High', text="High", anchor=W)
        tree.heading('Low', text="Low", anchor=W)
        tree.heading('Close', text="Close", anchor=W) 
        tree.heading('Adj Close', text="Adj Close", anchor=W)    
        tree.heading('Volume', text="Volume", anchor=W)           
        tree.column('#0', stretch=NO, minwidth=0, width=0)
        tree.column('#1', stretch=NO, minwidth=0, width=120)
        tree.column('#2', stretch=NO, minwidth=0, width=120)
        tree.column('#3', stretch=NO, minwidth=0, width=120)
        tree.column('#4', stretch=NO, minwidth=0, width=120)
        tree.column('#5', stretch=NO, minwidth=0, width=120)
        tree.column('#4', stretch=NO, minwidth=0, width=120)
        tree.pack()

        with open(f'{os.path.dirname(os.path.realpath(__file__))}\\Data\\msft_intra.csv') as f:
            reader = csv.DictReader(f, delimiter=',')
            for row in reader:
                Datetime = row['Datetime']
                Open = row['Open']
                High = row['High']
                Low = row['Low']
                Close = row['Close']
                Adj_Close = row['Adj Close']
                Volume = row['Volume']
                tree.insert("", 0, values=(Datetime, Open, High, Low, Close, Volume, Adj_Close, Volume))

def ShutProgram(*args):
    app.destroy()                           # Graphical interface
    app.quit()                              # Kernel

def goToRealTime(*args):
    Trading_app.show_frame(app,Real_Time_data)

def goToStaticGraphs(*args):
    Trading_app.show_frame(app,StaticGraphsPage)

def goToPrices(*args):
    Trading_app.show_frame(app,Pricesdownloader)


if __name__ == "__main__":
    db.directory_check()
    db.dl_quote_intraday(intra_ticker)
    db.dl_index_intraday(index)
    app = Trading_app()
    app.iconbitmap(f'{os.path.dirname(os.path.realpath(__file__))}\\trade.ico')
    app.geometry("1400x700")
    ani = animation.FuncAnimation(f_real_time, animate, interval=13000) #milli ==> 1 sec
    update_job = app.after(13000, live_update)
    app.bind('<F1>', ShutProgram)
    app.bind('<F2>', goToRealTime)
    app.bind('<F3>', goToStaticGraphs)
    app.bind('<F4>', goToPrices)
    app.mainloop()


