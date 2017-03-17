#!/usr/bin/python2.7

"""Convert CSV to reStructuredText tables
#source https://acaird.github.io/2016/02/07/simple-python-gui

A command-line and PythonTk GUI program to do a simple conversion from
CSV files to reStructuredText tables

A. Caird (acaird@gmail.com)
2016

"""

import tkFileDialog
import Tkinter as tk
import pandas as pd 
from sklearn.model_selection import StratifiedShuffleSplit, StratifiedKFold
import numpy as np


def gui():
    """make the GUI version of this command that is run if no options are
    provided on the command line"""

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
        try:
            sample_size = int(entry.get())
            n = len(data)
            if 1 <= sample_size <= n:
                prefix = stratify(sample_size,strat_columns)
                if prefix is None:
                    statusText.set("Error creating random sample.")
                    message.configure(fg="red")
                else:
                    statusText.set("Output is in {}".format(prefix + '_RCT.csv'))
                    message.configure(fg="black")
            else: 
                statusText.set("Please enter a number between 1 and "+str(n))
                message.configure(fg="red")   
        except ValueError:
            statusText.set("Please enter a whole number.")
            message.configure(fg="red")


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
                # data['fake'] = 'CONTROL'
                # data['fake'][[5, 0, 7, 8]] = 'TEST'
                # data_list = []
                # for cols in strat_columns:
                #     data_pre = data[data[cols].isin(data[cols].value_counts()[data[cols].value_counts()<2].index)]
                #     data_list.append(data_pre)
                #     del(data_pre)
                # data_pre = pd.concat(data_list)
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
        global sample_size, strat_columns, statusText, message, entry
        statusText = tk.StringVar(frame_B)
        statusText.set("An empty selection with result in randomizing by Risk, Sex and Race, if possible.")
        var_list = []
        strat_columns = []

        # Create explanatory label
        label = tk.Label(frame_B, text="Please enter choose a size for the test population that is lower than "+str(len(data)))
        label.pack()
        entry = tk.Entry(frame_B, width=50)
        entry.pack()

        

        for col in list(data):
            var_temp = tk.Variable()   
            var_list.append(var_temp)
            l = tk.Checkbutton(frame_B, text=col, variable=var_temp)
            l.pack()  

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


def get_parser():
    """ The argument parser of the command-line version """
    parser = argparse.ArgumentParser(description=('convert csv to rst table'))

    parser.add_argument('--input', '-F',
                        help='name of the intput file')

    parser.add_argument('--output', '-O',
                        help=("name of the output file; " +
                              "defaults to <inputfilename>.rst"))
    return parser


if __name__ == "__main__":
    """ Run as a stand-alone script """

    gui()                   # otherwise run the GUI version
