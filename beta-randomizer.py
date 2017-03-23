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

class gui(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title = "TEST"
        self.container = tk.Frame(self)
        self.container.pack(side="top",fill="both",expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}


        self.show_frame("main_frame")

    def show_frame(self,sel_frame,data=[]):

        for F in (main_frame, second_frame):
            page_name = F.__name__
            try:
                frame = F(parent=self.container, controller=self)
            except:
                frame = F(parent=self.container, controller=self,data=data)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        frame = self.frames[sel_frame]
        frame.tkraise()

class main_frame(tk.Frame):

    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller

        statusText = tk.StringVar(self)
        statusText.set("Press Browse button or enter CSV filename, "
                        "then press the Go button")

        label = tk.Label(self, text="Please load a CSV file: ")
        label.pack()
        entry = tk.Entry(self, width=50)
        entry.pack()
        separator = tk.Frame(self, height=2, bd=1, relief=tk.SUNKEN)
        separator.pack(fill=tk.X, padx=5, pady=5)

        button_go = tk.Button(self,
                           text="Go",
                           command=lambda: self.button_go_callback(entry,statusText,message,controller))
        button_browse = tk.Button(self,
                               text="Browse",
                               command=lambda: self.button_browse_callback(entry))
        button_exit = tk.Button(self,
                             text="Exit",
                             command=tk.sys.exit)
        button_go.pack()
        button_browse.pack()
        button_exit.pack()

        separator = tk.Frame(self, height=2, bd=1, relief=tk.SUNKEN)
        separator.pack(fill=tk.X, padx=5, pady=5)

        message = tk.Label(self, textvariable=statusText)
        message.pack()

    def button_browse_callback(self,entry):
        """ What to do when the Browse button is pressed """
        #global filename
        global filename
        filename = tkFileDialog.askopenfilename()
        entry.delete(0, tk.END)
        entry.insert(0, filename)
        return filename

    def button_go_callback(self,entry,statusText,message,controller):
        """ what to do when the "Go" button is pressed """
        global data
        data = None
        input_file = entry.get()
        if input_file.rsplit(".")[-1] != "csv":
            statusText.set("Filename must end in `.csv'")
            message.configure(fg="red")
        else:
            try:     
                data = pd.read_csv(filename)
                controller.show_frame("second_frame",data=data)
                sf = second_frame(parent=container,controller=self,data=data)
                sf.grid(row=0, column=0, sticky="nsew")
                sf.tkraise()
            except:
                self.statusText.set("Error reading file" + self.filename)
        pass


class second_frame(tk.Frame):

    """ 
    Description of this second frame 
    """

    def __init__(self,parent,controller,data):
        
        # Declare variables and set initial values'
        tk.Frame.__init__(self, parent)
        self.controller = controller
        warnings=0
        strat_columns = []
        var_dict = {}
        statusText = tk.StringVar(self)
        statusText.set("An empty selection with result in randomizing by Risk, Sex and Race, if possible.")

        # Create explanatory label
        label = tk.Label(self, text="Please enter choose a size for the test population that is lower than "+str(len(data)))
        label.pack()
        entry = tk.Entry(self, width=50)
        entry.pack()


        for col in list(data):
            if "CCIS" in col:
                pass
            elif ("name" in col) or ("Name" in col) or ("Surname" in col):
                pass
            else:
                var_temp = tk.StringVar()   
                l = tk.Checkbutton(self, text=col, variable=var_temp)
                l.pack()  
                var_dict[col] = var_temp

        button_stratify = tk.Button(self,
           text="Generate sample",
           command=lambda: self.button_stratify_callback(var_dict,entry,statusText,message))

        button_exit = tk.Button(self,
                     text="Exit",
                     command=tk.sys.exit)

        button_return = tk.Button(self, text="Return",
                           command=lambda: controller.show_frame("main_frame"))
     
        
        button_stratify.pack()
        button_return.pack()
        button_exit.pack()

        message = tk.Label(self, textvariable=statusText)
        message.configure(fg="black")
        message.pack()

    def button_stratify_callback(self,var_dict,entry,statusText,message,warnings=0,*args,**kwargs):
        
        """ what to do when the "Go" button is pressed """
        global strat_columns, raise_vble_warning
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
            self.warning_1(var_dict,entry,statusText,message,warnings)
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
                        statusText.set("Output is in {}".format(prefix+'_RCT.csv'))
                        # Consider adding a timestamp.
                        message.configure(fg="black")
                else: 
                    statusText.set("Please enter a number between 1 and "+str(n))
                    message.configure(fg="red")   
            except ValueError:
                statusText.set("Please enter a whole number.")
                message.configure(fg="red")

    def warning_1(self,var_dict,entry,statusText,message,warnings):

        tkMessageBox.showinfo("Warning","We suggest not to randomize based on parole officers or judges.")
        warnings += 1
        statusText.set("Select columns.")
        message.configure(fg="Black")
        self.button_stratify_callback(var_dict=var_dict,entry=entry,statusText=statusText,message=message,warnings=warnings)
    


if __name__ == "__main__":

    my_gui = gui()
    my_gui.mainloop()
    my_gui.title("TEST")
