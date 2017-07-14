#!/usr/bin/python2.7

"""

Stratified random sample generator for Betagov.
Author: S. Arango Franco - sarangof@nyu.edu.

Some of A. Caird's code (https://acaird.github.io/2016/02/07/simple-python-gui) is used for the interface.

2017.

"""

import Tkinter as tk
import tkFileDialog
import tkMessageBox
import pandas as pd 
import datetime as dt
from beta_functions import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from Tkinter import BooleanVar
from Tkinter import StringVar

global data, strat_columns, filename, filename1, filename2, rct, data_rct, data_new
data = pd.DataFrame([])
rct = pd.DataFrame([])
data_rct = pd.DataFrame([])
data_new = pd.DataFrame([])
strat_columns = []
filename1, filename2, filename = "","",""

class gui(tk.Tk):

    data = pd.DataFrame([])
    filename = ""

    rct = []
    def __init__(self):
        tk.Tk.__init__(self)
        self.title = "TEST"
        container = tk.Frame(self)
        container.pack(side="top",fill="both",expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (main_frame, first_frame, second_frame, balance_frame, first_frame_existing, second_frame_existing):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(main_frame)

    def show_frame(self,sel_frame):
        frame = self.frames[sel_frame]
        frame.tkraise()

    def get_page(self, page_class):
        return self.frames[page_class]


class main_frame(tk.Frame):

    def __init__(self,parent,controller):
        print("Main frame initialized")
        tk.Frame.__init__(self,parent)
        self.parent = parent 
        self.controller = controller
        statusText = tk.StringVar(self)
        statusText.set("What would you like to do?")
        separator = tk.Frame(self, height=2, bd=1, relief=tk.SUNKEN)
        separator.pack(fill=tk.X, padx=5, pady=5)

        message = tk.Label(self, textvariable=statusText)
        message.pack()

        button_new = tk.Button(self,
                           text="New randomization scheme",
                           command=lambda: self.button_new_callback())

        button_existing = tk.Button(self,
                           text="Update existing randomization scheme",
                           command=lambda: self.button_existing_callback())

        button_exit = tk.Button(self,
                             text="Exit",
                             command=tk.sys.exit)
        button_new.pack()
        button_existing.pack()
        button_exit.pack()

    def button_new_callback(self,*args,**kwargs):
        self.controller.show_frame(first_frame)

    def button_existing_callback(self,*args,**kwargs):
        self.controller.show_frame(first_frame_existing)


class first_frame(tk.Frame):

    

    def __init__(self,parent,controller):
        #print("First frame initialized")
        tk.Frame.__init__(self,parent)
        self.controller = controller
        self.parent = parent

        self.raise_vble_warning = BooleanVar(self)
        self.raise_vble_warning.set(False)

        self.show_frame = controller.show_frame

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
                           command=lambda: self.button_go_callback(entry,statusText,message))
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
        global filename
        filename = tkFileDialog.askopenfilename()
        #self.controller.filename.set(self.filename)

        entry.delete(0, tk.END)
        entry.insert(0, filename)

    def button_go_callback(self,entry,statusText,message):
        global data
        """ what to do when the "Go" button is pressed """
        input_file = entry.get()
        if input_file.rsplit(".")[-1] not in ["csv","xlsx","xls"] :
            statusText.set("Filename must end in `.csv'")
            message.configure(fg="red")
        else:
            #try:     
                #try:
                    #data = pd.read_csv(filename)
                #except:
            data = pd.read_excel(filename)
            # delete empty columns
            data.dropna(axis=1,inplace=True)
            # remove upper case.
            data = data.apply(lambda x: x.astype(str).str.lower())
            # replace all special characters.
            data.replace(r'[,\"\']','', regex=True).replace(r'\s*([^\s]+)\s*', r'\1', regex=True)

            #self.controller.show_frame(second_frame)
            sf = second_frame(self.parent, self)
            sf.grid(row=0, column=0, sticky="nsew")
            sf.tkraise()
            #self.__firstFrame=first_frame(self,self.parent)
            #self.__firstFrame.data = data

            #except:
            #    statusText.set("Error reading file" + str(filename))
        pass


class second_frame(tk.Frame):

    """ 
    Description of this second frame 
    """
    
    def __init__(self,parent,controller):
        # Declare variables and set initial values'
        #print("Second frame initialized")
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.parent = parent
        self.warnings=0

        self.show_frame = controller.show_frame

        #self.__firstFrame=first_frame(self,parent)
        #print(self.__firstFrame.data)
        #data = first_frame.data
        #data = pd.DataFrame([])

        var_dict = {}
        statusText = tk.StringVar(self)
        statusText.set(" ")

        # Create explanatory label
        label = tk.Label(self, text="Please enter the desired percentage of individuals to be assigned to the control group")
        label.pack()
        entry = tk.Entry(self, width=50)
        entry.pack()

        for col in data.columns:
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
                           command=lambda: controller.show_frame(main_frame))
     
        
        # IDEA: BUTTON TO CLEAR SELECTION.

        button_stratify.pack()
        button_return.pack()
        button_balance.pack()
        button_exit.pack()

        message = tk.Label(self, textvariable=statusText)
        message.configure(fg="black")
        message.pack()



    def button_stratify_callback(self,var_dict,entry,statusText,message,*args,**kwargs):
        global strat_columns, sample_p
        """ what to do when the "Go" button is pressed """
        #print("At the beginning of callback: "+str(self.warnings))
        for cols,vs in var_dict.iteritems():
            if vs.get():
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
                    self.controller.raise_vble_warning.clear() 
                    self.controller.raise_vble_warning.update(True)
                    if self.warnings>0:    
                        strat_columns.append(cols)
                elif ('age' in cols.lower()):
                    qtile = data[cols].astype('int64').quantile([0.,0.25,0.5,0.75]).values.astype('int')
                    data[cols] = data[cols].astype('int64')
                    data.loc[data[cols] > qtile[len(qtile)-1], cols] = '['+str(qtile[len(qtile)-1])+'-'+str(data[cols].max())+']'
                    for i in range(len(qtile)-1):
                        data.loc[(data[cols]>=qtile[i]) & (data[cols]<qtile[i+1]),cols] = '['+str(qtile[i])+'-'+str(qtile[i+1])+')'
                    strat_columns.append(cols)

                    #{str()}#PLACE HOLDER IN THIS FUNCTION}
                else:
                    strat_columns.append(cols)
        #if strat_columns == []:
        #    strat_columns = ['Sex','Risk','Race']
        
        if self.controller.raise_vble_warning.get() and (self.warnings<1):
            self.warning_1(var_dict,entry,statusText,message)
        else:
            #try:
            sample_p = int(entry.get())
            n = len(data)

            min_n = len(strat_columns)*2

            if min_n >= n:
                statusText.set("Too many columns selected for the sample size. Try selecting less columns for stratification.")
                message.configure(fg="red")
            
            if 0 <= sample_p <= 100:
                #print(data.head())
                prefix = stratify(data_set=data,p=sample_p,selected_columns=strat_columns,filename=filename) 
                if prefix is None:
                    statusText.set("Error creating random sample.")
                    message.configure(fg="red")
                else:
                    statusText.set("Output is in file {}".format(prefix))
                    # Consider adding a timestamp.
                    message.configure(fg="black")
            else: 
                statusText.set("Please enter a number between 0 and 100")
                message.configure(fg="red")
            #except ValueError:
            #    statusText.set("Please enter a whole number.")
            #    message.configure(fg="red")

    def button_balance_callback(self,statusText,message,*args,**kwargs):
        global rct
        #try:
        rct = pd.read_excel(filename.rsplit(".")[0]+'_RCT'+'.xlsx')
        #print(rct)
        #self.controller.show_frame(balance_frame,rct=rct)

        #sf = balance_frame(self.parent, self)
        #sf.grid(row=0, column=0, sticky="nsew")
        #sf.tkraise()

        #self.controller.show_frame(balance_frame)

        sf = balance_frame(self.parent, self)
        sf.grid(row=0, column=0, sticky="nsew")
        sf.tkraise()
        #except:
        #    statusText.set("It is first necessary to create a randomized sample.")
        #    message.configure(fg="red")

    def warning_1(self,var_dict,entry,statusText,message):
        tkMessageBox.showinfo("Warning","We suggest not to randomize based on parole officers or judges.")
        self.warnings += 1
        print("At prompt function: "+str(self.warnings))
        statusText.set("Select columns.")
        message.configure(fg="Black")
        self.button_stratify_callback(var_dict=var_dict,entry=entry,statusText=statusText,message=message)
    

class balance_frame(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller
        self.parent = parent
        label = tk.Label(self, text="Hello world")
        label.pack()

        button_exit = tk.Button(self,
             text="Exit",
             command=tk.sys.exit)

        button_return = tk.Button(self, text="Return to main window",
                           command=lambda: controller.show_frame(main_frame))
     
        #print(rct)

        try:
            #rct['Group-RCT'].hist()
            #print('yes')
            #print(rct[strat_columns[0]])

            
            f = Figure(figsize=(5,5), dpi=100)
            a = f.add_subplot('111')
            #a.plot([1,2,3,4,5,6,7,8],[5,6,1,3,8,9,3,5])
            df = pd.crosstab(rct['Group-RCT'],rct[strat_columns[0]],normalize='columns')
            #print(df)
            
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



            b = f.add_subplot('112')
            #a.plot([1,2,3,4,5,6,7,8],[5,6,1,3,8,9,3,5])
            df = pd.crosstab(rct['Group-RCT'],rct[strat_columns[0]],normalize='columns')
            print(df)
            
            ind = np.arange(len(df.transpose()))
            b.bar(ind,df.values[0][:],0.25)
            b.bar(ind+0.5,df.values[1][:],0.25)
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
        

class first_frame_existing(tk.Frame):

    def __init__(self,parent,controller):
        global sample_p
        tk.Frame.__init__(self,parent)
        self.controller = controller
        self.parent = parent

        self.show_frame = controller.show_frame

        var_dict = {}

        statusText = tk.StringVar(self)
        statusText.set("Press Browse button or enter CSV filename, "
                        "It must end in _RCT"
                        "then press the Go button")

        label = tk.Label(self, text="Please load the _RCT file that was already randomized: ")
        label.pack()
        entry1 = tk.Entry(self, width=50)
        entry1.pack()

        button_browse_1 = tk.Button(self,
                               text="Browse",
                               command=lambda: self.button_browse_callback_1(entry1))
        button_browse_1.pack()

        label = tk.Label(self, text="Please load a file with new individuals to randomize: ")
        label.pack()
        entry2 = tk.Entry(self, width=50)
        entry2.pack()

        separator = tk.Frame(self, height=2, bd=1, relief=tk.SUNKEN)
        separator.pack(fill=tk.X, padx=5, pady=5)


        button_browse_2 = tk.Button(self,
                               text="Browse",
                               command=lambda: self.button_browse_callback_2(entry2))

        button_exit = tk.Button(self,
                             text="Exit",
                             command=tk.sys.exit)
        
        button_go = tk.Button(self,
                           text="Go",
                           command=lambda: self.button_go_callback(entry1,entry2,statusText,message,self.controller))

        button_browse_2.pack()

        button_go.pack()
        
        button_exit.pack()

        separator = tk.Frame(self, height=2, bd=1, relief=tk.SUNKEN)
        separator.pack(fill=tk.X, padx=5, pady=5)

        message = tk.Label(self, textvariable=statusText)
        message.pack()

    def button_browse_callback_1(self,entry):
        global filename1
        filename1 = tkFileDialog.askopenfilename()
        entry.delete(0, tk.END)
        entry.insert(0, filename1)
        return filename1

    def button_browse_callback_2(self,entry):
        global filename2
        filename2 = tkFileDialog.askopenfilename()
        entry.delete(0, tk.END)
        entry.insert(0, filename2)
        return filename2

    def button_go_callback(self,entry1,entry2,statusText,message,controller):
        global data_new, data_rct
        #data = None
        #filename = None
        input_file_1 = entry1.get()
        input_file_2 = entry2.get()

        name_clean_1 = input_file_1.rsplit(".")[0]
        file_type_1 = input_file_1.rsplit(".")[-1]

        name_clean_2 = input_file_2.rsplit(".")[0]
        file_type_2 = input_file_2.rsplit(".")[-1]

        if (file_type_1 not in ["xlsx"]) or (file_type_2 not in ["csv","xlsx","xls"]):
            statusText.set("RCT file must end in xlsx and new file must be in a valid format csv,xlsx,xls.")
            message.configure(fg="red")
        else:
            if name_clean_1.rsplit("_")[-1] not in ["RCT"] :
                statusText.set("RCT file must have been generated by this program. Its name should end in _RCT")
                message.configure(fg="red")
            else:  
                
                data_rct = pd.read_excel(filename1)
                # delete empty columns
                data_rct.dropna(axis=1,inplace=True)
                # remove upper case.
                data_rct = data_rct.apply(lambda x: x.astype(str).str.lower())
                # replace all special characters.
                data_rct.replace(r'[,\"\']','', regex=True).replace(r'\s*([^\s]+)\s*', r'\1', regex=True)



                data_new = pd.read_excel(filename2)
                # delete empty columns
                data_new.dropna(axis=1,inplace=True)
                # remove upper case.
                data_new = data_new.apply(lambda x: x.astype(str).str.lower())
                # replace all special characters.
                data_new.replace(r'[,\"\']','', regex=True).replace(r'\s*([^\s]+)\s*', r'\1', regex=True)

                #print(set(data_rct.columns)-set(['Group-RCT']))
                #print(set(data_new.columns))
                #print(set(data_rct.columns)-set(['Group-RCT']) ==  set(data_new.columns))

                if 'Group-RCT' in data_rct.columns:
                    #controller.show_frame("second_frame_existing")
                    if set(data_rct.columns)-set(['Group-RCT']) ==  set(data_new.columns):
                        sf = second_frame_existing(self.parent, self)
                        sf.grid(row=0, column=0, sticky="nsew")
                        sf.tkraise()
                    else:
                        statusText.set("Files must have the same structure (columns).")
                        message.configure(fg="red")
                else:                    
                    statusText.set("The file should have been generated by this own program and thus have a Group-RCT column.")
                    message.configure(fg="red")
                
                pass
        pass

    

class second_frame_existing(tk.Frame):

    """ 
    Description of this second frame 
    """

    def __init__(self,parent,controller):
        
        # Declare variables and set initial values

        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.parent = parent
        self.warnings=0
    

        strat_columns = []
        var_dict = {}
        statusText = tk.StringVar(self)
        statusText.set(" ")

        message = tk.Label(self, textvariable=statusText)

        message.pack()




        button_exit = tk.Button(self,
                     text="Exit",
                     command=tk.sys.exit)

        button_return = tk.Button(self, text="Return",
                           command=lambda: controller.show_frame(main_frame))
     
        button_balance = tk.Button(self, text="Return",
                           command=lambda: 1)
        
        # IDEA: BUTTON TO CLEAR SELECTION.


        #button_return.pack()
        button_balance.pack()
        button_exit.pack()

        message = tk.Label(self, textvariable=statusText)
        message.configure(fg="black")
        message.pack()

        sample_p = filename1.rsplit("-")[-1].rsplit("_")[0]
        #print("filename")
        #print(filename1)

        button_stratify = tk.Button(self,text="Randomize new individuals",command=lambda: self.button_stratify_callback(data_rct,data_new,sample_p,strat_columns,filename1))
        button_stratify.pack()
    def button_stratify_callback(self,data_rct,data_new,sample_p,strat_columns,filename1,*args,**kwargs):
        prefix = update_stratification(data_rct=data_rct,data_new=data_new,sample_p=sample_p,selected_columns=strat_columns,filename1=filename1) 



        #statusText.set("Please enter a number between "+str(min_n)+" and "+str(n))
        #message.configure(fg="red")   


    def warning_1(self,var_dict,entry,statusText,message):
        tkMessageBox.showinfo("Warning","We suggest not to randomize based on parole officers or judges.")
        self.warnings += 1
        print("At prompt function: "+str(self.warnings))
        statusText.set("Select columns.")
        message.configure(fg="Black")
        self.button_stratify_callback(var_dict=var_dict,entry=entry,statusText=statusText,message=message)


if __name__ == "__main__":

    my_gui = gui()
    my_gui.mainloop()
    my_gui.title("TEST")
