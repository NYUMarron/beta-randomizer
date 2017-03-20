#!/usr/bin/python2.7

"""

Stratified random sample generator for Betagov.
Author: S. Arango Franco - sarangof@nyu.edu.

Some of A. Caird's code (https://acaird.github.io/2016/02/07/simple-python-gui) is used for the interface.

2017.

"""

import tkFileDialog, tkMessageBox
import Tkinter as tk
import pandas as pd 
import datetime as dt
from beta_functions import *

def gui():

    if __name__ == "__main__":
        """Build the gui"""


        def first_frame():
            
            global statusText, message, entry, frame_B, root, frame_A, label, button_go, button_exit, button_browse
            
            root = tk.Tk()
            root.withdraw()
            frame_A = tk.Toplevel(root)

            statusText = tk.StringVar(frame_A)
            statusText.set("Press Browse button or enter CSV filename, "
                           "then press the Go button")

            label = tk.Label(frame_A, text="Please load a CSV file: ")
            label.pack()
            entry = tk.Entry(frame_A, width=50)
            entry.pack()
            separator = tk.Frame(frame_A, height=2, bd=1, relief=tk.SUNKEN)
            separator.pack(fill=tk.X, padx=5, pady=5)

            button_go = tk.Button(frame_A,
                               text="Go",
                               command=button_go_callback)
            button_browse = tk.Button(frame_A,
                                   text="Browse",
                                   command=button_browse_callback)
            button_exit = tk.Button(frame_A,
                                 text="Exit",
                                 command=tk.sys.exit)
            button_go.pack()
            button_browse.pack()
            button_exit.pack()

            separator = tk.Frame(frame_A, height=2, bd=1, relief=tk.SUNKEN)
            separator.pack(fill=tk.X, padx=5, pady=5)

            message = tk.Label(frame_A, textvariable=statusText)
            message.pack()

        def second_frame():

            global sample_size, entry, var_dict, frame_B, message, statusText, warnings

            """ 
            Description of this second frame 
            """

            # Declare variables and set initial values'
            warnings=0
            strat_columns = []
            var_dict = {}
            frame_A.destroy()
            frame_B = tk.Toplevel(root)
            statusText = tk.StringVar(frame_B)
            statusText.set("An empty selection with result in randomizing by Risk, Sex and Race, if possible.")

            # Create explanatory label
            label = tk.Label(frame_B, text="Please enter choose a size for the test population that is lower than "+str(len(data)))
            label.pack()
            entry = tk.Entry(frame_B, width=50)
            entry.pack()

            for col in list(data):
                if "CCIS" in col:
                    pass
                elif ("name" in col) or ("Name" in col) or ("Surname" in col):
                    pass
                else:
                    var_temp = tk.StringVar()   
                    l = tk.Checkbutton(frame_B, text=col, variable=var_temp)
                    l.pack()  
                    var_dict[col] = var_temp

            button_stratify = tk.Button(frame_B,
               text="Generate sample",
               command=button_stratify_callback)
        
            button_exit = tk.Button(frame_B ,
                         text="Exit",
                         command=tk.sys.exit)

            button_return = tk.Button(frame_B ,
                         text="Return",
                         command=button_return_callback)        
            
            button_stratify.pack()
            button_return.pack()
            button_exit.pack()

            message = tk.Label(frame_B, textvariable=statusText)
            message.configure(fg="black")
            message.pack()

        def button_browse_callback():
            """ What to do when the Browse button is pressed """
            global filename
            filename = tkFileDialog.askopenfilename()
            entry.delete(0, tk.END)
            entry.insert(0, filename)

        def button_go_callback():
            """ what to do when the "Go" button is pressed """
            global input_file, data
            data = None
            input_file = entry.get()
            if input_file.rsplit(".")[-1] != "csv":
                statusText.set("Filename must end in `.csv'")
                message.configure(fg="red")
            else:
                try:     
                    data = pd.read_csv(filename)
                    second_frame()
                except:
                    statusText.set("Error reading file" + filename)

        def button_stratify_callback():
            """ what to do when the "Go" button is pressed """
            global strat_columns, raise_vble_warning, var_dict
            strat_columns = []
            raise_vble_warning = False
            #print(var_dict)
            for cols,vs in var_dict.iteritems():
                if vs.get():
                    print(cols)
                    if "DOB" in cols:
                        temp_dates = []
                        for dob in data[cols]:
                            birth_year = int(dt.datetime.strptime(dob,'%d/%M/%y').year)
                            if birth_year > 2000:
                                birth_year -= 100
                            age = dt.datetime.now().year - birth_year
                            if 0 <= age <= 25:
                                temp_dates.append('Lower than 25')
                            elif 25 <= age <= 60:
                                temp_dates.append('Between 25 and 60')
                            elif 60 <= age <= 100:
                                temp_dates.append('Older than 60')
                            else:
                                temp_dates.append('')
                        del(data[cols])
                        data[cols] = temp_dates
                        strat_columns.append(cols)
                    elif (cols == "PO") or (cols=="Judge"):
                        raise_vble_warning = True
                        if warnings>=1:    
                            strat_columns.append(cols)
                    else:
                        strat_columns.append(cols)
            if strat_columns == []:
                strat_columns = ['Sex','Risk','Race']
            #print(strat_columns)
            
            if raise_vble_warning and (warnings<1):
                warning_1()
            else:
                try:
                    sample_size = int(entry.get())
                    n = len(data)
                    if 1 <= sample_size <= n:
                        prefix = stratify(data_set=data,n=sample_size,selected_columns=strat_columns) 
                        if prefix is None:
                            statusText.set("Error creating random sample.")
                            message.configure(fg="red")
                        else:
                            statusText.set("Output is in {}".format(prefix + '_RCT.csv'))
                            # Consider adding a timestamp.
                            message.configure(fg="black")
                    else: 
                        statusText.set("Please enter a number between 1 and "+str(n))
                        message.configure(fg="red")   
                except ValueError:
                    statusText.set("Please enter a whole number.")
                    message.configure(fg="red")

        def button_return_callback():
            frame_B.destroy()
            gui()

        def warning_1():
            global warnings, statusText, message
            tkMessageBox.showinfo("Warning","We suggest not to randomize based on parole officers or judges.")
            warnings += 1
            statusText.set("Select columns.")
            message.configure(fg="Black")
            button_stratify_callback()
    tk.mainloop()
     
gui()
