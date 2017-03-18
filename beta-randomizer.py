#!/usr/bin/python2.7

"""

Stratified random sample generator for Betagov.
Author: S. Arango Franco - sarangof@nyu.edu.

Some of A. Caird's code (https://acaird.github.io/2016/02/07/simple-python-gui) is used for the interface.

2017.

"""

import tkFileDialog
import Tkinter as tk
import pandas as pd 
from sklearn.model_selection import StratifiedShuffleSplit, StratifiedKFold
import numpy as np


def gui():
    """Build the gui"""

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
        for cols,vs in var_dict.iteritems():
            if vs.get():
                strat_columns.append(cols)
        print(strat_columns)
        """ what to do when the "Go" button is pressed """
        # try:
        #     sample_size = int(entry.get())
        #     n = len(data)
        #     if 1 <= sample_size <= n:
        #         prefix = stratify(sample_size,candidate_vbles(strat_columns))
        #         if prefix is None:
        #             statusText.set("Error creating random sample.")
        #             message.configure(fg="red")
        #         else:
        #             statusText.set("Output is in {}".format(prefix + '_RCT.csv'))
        #             message.configure(fg="black")
        #     else: 
        #         statusText.set("Please enter a number between 1 and "+str(n))
        #         message.configure(fg="red")   
        # except ValueError:
        #     statusText.set("Please enter a whole number.")
        #     message.configure(fg="red")

    def candidate_vbles(list_columns):
        """
        Transform the initial set of columns into valid potential strata.
        """
        for col in list_columns:
            if "DOB" in col:
                pass
            if "CCIS" in col:
                list_columns = list_columns.remove(col)
            if (col == "PO") or (col=="Judge"):
                print("Wrong!")
                #statusText.set("We suggest not to randomize based on parole officers or judges.")
                #message.configure(fg="red")   
            if ("name" in col) or ("Name" in col) or ("Surname" in col): #regex are a good thing.
                list_columns = list_columns.remove(col)

        return list_columns


    def stratify(sample_size,strat_columns=['Sex']):
        """ 
        Stratified random sampling
        SPECIAL CASE, WHEN THERE IS ONLY ONE STRATUM PER INDIVIDUAL.
        RAISE MANY ERRORS.
        - The test_size = 1 should be greater or equal to the number of classes = 5
        - 
        """
        if data is not None:
            try:    

                sss = StratifiedShuffleSplit(n_splits=1, test_size=sample_size, random_state=2)
                #y = np.array(data[~data.isin(data_pre).T.any()][strat_columns])
                y = np.array(data[strat_columns])
                X = np.array([0] * y.shape[0])

                for train_index, test_index in sss.split(X, y):
                    print("TRAIN:", train_index, "TEST:", test_index)
                    X_train, X_test = X[train_index], X[test_index]
                    y_train, y_test = y[train_index], y[test_index]

                X = X.astype("string")
                X[train_index] = "Control"
                X[test_index] = "Test"
                data['Trial'] = X
                (prefix, sep, suffix) = filename.rpartition('.')
                data.to_csv(prefix + '_RCT.csv')

            except:
                return None

            return prefix

    def first_frame():

        global root, frame_A, statusText, label, entry, message, button_go, button_exit, button_browse
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

        """ 
        Description of this second frame 
        """

        # Destroy previous window and create a new one
        frame_A.destroy()
        frame_B = tk.Toplevel(root)

        # Declare variables and set initial values
        global sample_size, strat_columns, statusText, message, entry, var_dict, strat_columns
        statusText = tk.StringVar(frame_B)
        statusText.set("An empty selection with result in randomizing by Risk, Sex and Race, if possible.")
        strat_columns = []
        var_dict = {}

        # Create explanatory label
        label = tk.Label(frame_B, text="Please enter choose a size for the test population that is lower than "+str(len(data)))
        label.pack()
        entry = tk.Entry(frame_B, width=50)
        entry.pack()

        for col in list(data):
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
        
        button_stratify.pack()
        button_exit.pack()

        message = tk.Label(frame_B, textvariable=statusText)
        message.configure(fg="black")
        message.pack()

     
    first_frame()
    tk.mainloop()


if __name__ == "__main__":
    """ Run as a stand-alone script """

    gui() 
