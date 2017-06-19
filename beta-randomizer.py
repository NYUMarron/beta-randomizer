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
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

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

    def show_frame(self,sel_frame,data=[],filename=None,rct=pd.DataFrame([])):

        for F in (main_frame, second_frame, balance_frame):
            page_name = F.__name__
            if F==main_frame:
                frame = F(parent=self.container,controller=self)
            if F==second_frame:
                frame = F(parent=self.container,controller=self,data=data,filename=filename)
            if F==balance_frame:
                frame = F(parent=self.container,controller=self,data=data,filename=filename,rct=rct)
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
        global data, filename
        #data = None
        #filename = None
        input_file = entry.get()
        if input_file.rsplit(".")[-1] not in ["csv","xlsx","xls"] :
            statusText.set("Filename must end in `.csv'")
            message.configure(fg="red")
        else:
            try:     
                try:
                    data = pd.read_csv(filename)
                except:
                    data = pd.read_excel(filename)
                controller.show_frame("second_frame",data=data)
                sf = second_frame(parent=container,controller=self,data=data,filename=filename)
                sf.grid(row=0, column=0, sticky="nsew")
                sf.tkraise()
            except:
                statusText.set("Error reading file" + str(filename))
        pass


class second_frame(tk.Frame):

    """ 
    Description of this second frame 
    """

    def __init__(self,parent,controller,data,filename):
        
        # Declare variables and set initial values'

        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.warnings=0
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
                var_temp = tk.IntVar(value=0)#tk.StringVar()   
                l = tk.Checkbutton(self, text=col, variable=var_temp)#var_temp) #self.checkbutton = Checkbutton(..., variable = self.CheckVar)
                l.pack()  
                var_dict[col] = var_temp

        button_stratify = tk.Button(self,
           text="Generate sample",
           command=lambda: self.button_stratify_callback(var_dict,entry,statusText,message))

        button_exit = tk.Button(self,
                     text="Exit",
                     command=tk.sys.exit)

        button_balance = tk.Button(self,
            text="See resulting balance",
            command=lambda: self.button_balance_callback(statusText,message))

        button_return = tk.Button(self, text="Return",
                           command=lambda: controller.show_frame("main_frame"))
     
        
        # IDEA: BUTTON TO CLEAR SELECTION.

        button_stratify.pack()
        button_return.pack()
        button_balance.pack()
        button_exit.pack()

        message = tk.Label(self, textvariable=statusText)
        message.configure(fg="black")
        message.pack()

    def button_stratify_callback(self,var_dict,entry,statusText,message,*args,**kwargs):

        """ what to do when the "Go" button is pressed """
        global strat_columns, raise_vble_warning
        strat_columns = []
        raise_vble_warning = False
        #print("At the beginning of callback: "+str(self.warnings))
        for cols,vs in var_dict.iteritems():
            if vs.get():
                print(cols)
                if "dob" in cols.lower():
                    temp_dates = []
                    for dob in data[cols]:
                        try:
                            birth_year = int(dt.datetime.strptime(dob,'%d/%M/%y').year)
                            if birth_year > 2000:
                                birth_year -= 100
                            age = dt.datetime.now().year - birth_year
                        except ValueError:
                            pass
                    del(data[cols])
                    data["Age"] = age
                    strat_columns.append(cols)
                elif (cols == "PO") or (cols=="Judge"):
                    raise_vble_warning = True
                    if self.warnings>0:    
                        strat_columns.append(cols)
                elif ('age' in cols.lower()):
                    data[cols].astype('int64').quantile([0.,0.25,0.5,0.75])
                    age_bins = {#PLACE HOLDER IN THIS FUNCTION}
                else:
                    strat_columns.append(cols)
        #if strat_columns == []:
        #    strat_columns = ['Sex','Risk','Race']
        
        if raise_vble_warning and (self.warnings<1):
            self.warning_1(var_dict,entry,statusText,message)
        else:
            #try:
            sample_size = int(entry.get())
            n = len(data)
            
            if 1 <= sample_size <= n:
                print(data.head())
                prefix = stratify(data_set=data,n=sample_size,selected_columns=strat_columns,filename=filename) 
                if prefix is None:
                    statusText.set("Error creating random sample.")
                    message.configure(fg="red")
                else:
                    statusText.set("Output is in file {}".format(prefix))
                    # Consider adding a timestamp.
                    message.configure(fg="black")
            else: 
                statusText.set("Please enter a number between 1 and "+str(n))
                message.configure(fg="red")   
            #except ValueError:
            #    statusText.set("Please enter a whole number.")
            #    message.configure(fg="red")

    def button_balance_callback(self,statusText,message,*args,**kwargs):
        global rct
        try:
            print("filename")
            print(filename)
            rct = pd.read_excel(filename.rsplit(".")[0]+'_RCT'+'.xlsx')
            self.controller.show_frame("balance_frame",rct=rct)
        except:
            statusText.set("It is first necessary to create a randomized sample.")
            message.configure(fg="red")

    def warning_1(self,var_dict,entry,statusText,message):
        tkMessageBox.showinfo("Warning","We suggest not to randomize based on parole officers or judges.")
        self.warnings += 1
        print("At prompt function: "+str(self.warnings))
        statusText.set("Select columns.")
        message.configure(fg="Black")
        self.button_stratify_callback(var_dict=var_dict,entry=entry,statusText=statusText,message=message)
    

class balance_frame(tk.Frame):
    def __init__(self,parent,controller,data,filename,rct,*args,**kwargs):
        tk.Frame.__init__(self,parent)
        self.controller = controller
        label = tk.Label(self, text="Hello world")
        label.pack()

        button_exit = tk.Button(self,
             text="Exit",
             command=tk.sys.exit)

        button_return = tk.Button(self, text="Return to main window",
                           command=lambda: controller.show_frame("main_frame"))
     
        

        try:
            #rct['Group-RCT'].hist()
            print('yes')
            print(rct[strat_columns[0]])

            
            f = Figure(figsize=(5,5), dpi=100)
            a = f.add_subplot('111')
            #a.plot([1,2,3,4,5,6,7,8],[5,6,1,3,8,9,3,5])
            df = pd.crosstab(rct['Group-RCT'],rct[strat_columns[0]])
            print(df)
            
            ind = np.arange(len(df.transpose()))
            a.bar(ind,df.values[0][:],0.25)
            a.bar(ind+0.5,df.values[1][:],0.25)
            #a.title(strat_columns[0])
            #a.plot(rct[strat_columns[0]].value_counts(),kind='bar')

            canvas = FigureCanvasTkAgg(f, self)
            canvas.show()
            canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

            toolbar = NavigationToolbar2TkAgg(canvas, self)
            toolbar.update()
            canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)


            
            """
            f = Figure(figsize=(5,5), dpi=100)
            a = f.add_subplot(111)
            a.plot([1,2,3,4,5,6,7,8],[5,6,1,3,8,9,3,5])

            

            canvas = FigureCanvasTkAgg(f, self)
            canvas.show()
            canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

            """

        except:
            pass

        button_return.pack()
        button_exit.pack()
        
        
if __name__ == "__main__":

    my_gui = gui()
    my_gui.mainloop()
    my_gui.title("TEST")
