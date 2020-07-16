import pandas as pd
import sqlite3
import yfinance as yf
from datetime import date, timedelta, datetime
import tkinter as tk
from tkinter import *

import os
os.chdir('C:\\Users\\alexa\\OneDrive\\Desktop\\SN Dimensions\\')

from datetime import date

def dl_quotes(self, boxL2, entry_stock, period):
    """
    Downloads quotes for a given period and given stock AND inserts result into adequate DB
    """
    self.prompt = ttk.Label(boxL2, text=f"Starting a new HTTPS connection to yahoofinance.com",justify=LEFT)
    self.prompt.pack(anchor=W)

    today = date.today()
    today_str = today.strftime("%Y-%m-%d")

    beginning =""
    if period == "60 Days":
        beginning = today - timedelta(60)
    elif period == "1 Week":
        beginning = today - timedelta(7)
    elif period == "5 Years":
        beginning = today - timedelta(1825)

    try:   
        df = yf.download(entry_stock, start = f"{beginning}", end = f"{today_str}", period="1d")
        print(df)
        self.prompt = ttk.Label(boxL2, text=f"{entry_stock.upper()} found and downloaded!",justify=LEFT)
        self.prompt.pack(anchor=W)
    except:
        self.prompt = ttk.Label(boxL2, text=f"{entry_stock.upper()} not found!",justify=LEFT)
        self.prompt.pack(anchor=W)
        print(f"{entry_stock.upper()} not found!")

    # Inserting data (and overwritting it) into the new table
    conn = sqlite3.connect(f'C:\\Users\\alexa\\OneDrive\\Desktop\\SN Dimensions\\Data\\{period}.db3')  
    df.to_sql(f'{entry_stock}',conn, if_exists='replace')
    conn.close()

    return df

def dl_quote_intraday(intra_ticker):
    df = yf.download(f"{intra_ticker}", period = "1d", interval = "1m")
    df= df.reset_index()
    df['Datetime'] = df['Datetime'].astype('datetime64[ns]') 
    df['Datetime'] = df['Datetime'].dt.tz_localize(None)
    df['Datetime'] = df['Datetime'].astype(str)
    df = df.set_index(['Datetime'])

    df.to_csv(f'C:\\Users\\alexa\\OneDrive\\Desktop\\SN Dimensions\\Data\\{intra_ticker}_intra.csv', index="false")

index='^GSPC'

def dl_index_intraday(index):
    df_index = yf.download(f"{index}", period = "1d", interval = "1m")
    df_index= df_index.reset_index()
    df_index['Datetime'] = df_index['Datetime'].astype('datetime64[ns]') 
    df_index['Datetime'] = df_index['Datetime'].dt.tz_localize(None)
    df_index['Datetime'] = df_index['Datetime'].astype(str)
    df_index = df_index.set_index(['Datetime'])
    
    df_index.to_csv(f'C:\\Users\\alexa\\OneDrive\\Desktop\\SN Dimensions\\Data\\{index}_intra.csv', index="false")

def dl_f_statements(entry_stock):
    """
    Downloads fundamentals for a given period and given stock AND inserts result into adequate DB
    """
    try:
        print("Starting a new HTTPS connection to yahoofinance.com")
        fin = yf.Ticker("MSFT")
        financials = fin.financials
        print(f"{entry_stock} found! Downloading...")
    except:
        print(f"{entry_stock} not found!")

    try:
        # Inserting data (and overwritting it) into the new table
        conn = sqlite3.connect(f'C:\\Users\\alexa\\OneDrive\\Desktop\\SN Dimensions\\Data\\financials.db3')  
        financials.to_sql(f'{entry_stock}',conn, if_exists='replace')
        conn.close()
        print(f"Successfuly added {entry_stock}to the sqlite3 database")
    except:
        print("Problem encountered with the sqlite3 database")  


def read_db(entry_stock,period):
    """
    Pulls data from sqlite3 DB
    """
    conn = sqlite3.connect(f'C:\\Users\\alexa\\OneDrive\\Desktop\\SN Dimensions\\Data\\{period}.db3')
    df = pd.read_sql_query(f"SELECT * FROM {entry_stock}", conn)
    conn.close()

    return df

def get_available_symbols(period):
    """
    Returns a list of already downloaded symbols
    """
    con = sqlite3.connect(f'C:\\Users\\alexa\\OneDrive\\Desktop\\SN Dimensions\\Data\\{period}.db3')
    mycur = con.cursor() 
    mycur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    available_table=(mycur.fetchall())
    test = available_table[0][0]
    con.close()

    stocks_list = []
    
    for i in range(len(available_table)):
        test = available_table[i][0]
        stocks_list.append(test)
    
    return stocks_list




