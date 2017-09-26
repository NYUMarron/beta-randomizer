#!/usr/bin/python2.7

"""

Stratified random sample generator for BetaGov.
Author: S. Arango-Franco - sarangof@nyu.edu.
2017.

"""

import Tkinter as tk
import tkFileDialog
import tkMessageBox
import pandas as pd 
import datetime as dt
from beta_functions import *
import matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
#from matplotlib.figure import Figure

from Tkinter import BooleanVar
from Tkinter import StringVar

sns.set_style("whitegrid")

class gui(tk.Frame):

    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.master = master

        self.main_frame()
        self.first_frame()
        self.second_frame()
        self.balance_frame(self.rct)
        self.first_frame_existing()
        self.second_frame_existing()

        self.mainframe.tkraise()

    def main_frame(self):
        print("Main frame initialized")


        self.data, self.rct, self.data_rct, self.data_new, self.total_data = pd.DataFrame([]), pd.DataFrame([]), pd.DataFrame([]), pd.DataFrame([]), pd.DataFrame([])
        self.filename, self.filename1, self.filename2 = "","",""
        self.prefix = ''
        self.strat_columns = []
        self.sample_p = 0.
        self.raise_vble_warning = False

        self.mainframe = tk.Frame(self.master,width=300, height=350)
        self.mainframe.grid(row=0, column=0, sticky="nsew")
        
        self.statusText = tk.StringVar(self)
        self.statusText.set("What would you like to do?")

        tk.Frame(self, height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, padx=5, pady=5)
        self.message = tk.Label(self, textvariable=self.statusText)
        self.message.pack()

        tk.Button(self.mainframe, text="New randomization scheme", command=lambda: self.firstframe.tkraise()).pack(expand=True,side=tk.TOP)
        tk.Button(self.mainframe, text="Update existing randomization scheme", command=lambda: self.firstframeexisting.tkraise()).pack(expand=True,side=tk.TOP )
        tk.Button(self.mainframe, text="Exit",command=tk.sys.exit).pack(expand=True,side=tk.BOTTOM)

    def first_frame(self):

        self.firstframe = tk.Frame(self.master,width=300, height=350)
        self.firstframe.grid(row=0, column=0, sticky="nsew")

        self.raise_vble_warning = False

        self.statusText = tk.StringVar()
        self.statusText.set("Press Browse button or enter CSV filename, "
                        "then press the Go button")
        self.label = tk.Label(self.firstframe, text="Please load a file: ").pack(expand=True)

        self.first_frame_entry = tk.Entry(self.firstframe, width=50)
        self.first_frame_entry.pack(expand=True)

        tk.Frame(self, height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, padx=5, pady=5)

        tk.Button(self.firstframe, text="Browse", command=lambda: self.button_browse_callback()).pack(expand=True)
        tk.Button(self.firstframe, text="Go", command=lambda: self.button_go_callback()).pack(expand=True)
        tk.Button(self.firstframe, text="Return", command=lambda: self.mainframe.tkraise()).pack(expand=True)
        tk.Button(self.firstframe, text="Exit", command=tk.sys.exit).pack(expand=True,side=tk.BOTTOM)

        tk.Frame(self.firstframe, height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, padx=5, pady=5)

        self.message = tk.Label(self, textvariable=self.statusText)
        self.message.pack(expand=True)

    def button_browse_callback(self):
        self.filename = tkFileDialog.askopenfilename()
        self.first_frame_entry.delete(0, tk.END)
        self.first_frame_entry.insert(0, self.filename)

    def button_go_callback(self):

        """ what to do when the "Go" button is pressed """
        print("Go callback")
        input_file = self.first_frame_entry.get()

        if input_file.rsplit(".")[-1] not in ["csv","xlsx","xls"] :
            self.statusText.set("Filename must end in `.xlsx', '.csv' or '.xls'")
            self.message.configure(fg="red")
        else:
            #try:     
                #try:
                    #data = pd.read_csv(filename)
                #except:
            data = pd.read_excel(self.filename) # delete empty columns
            data.dropna(axis=1,inplace=True,how='all') # remove upper case.
            data.dropna(axis=0,inplace=True,how='all')
            data = data.apply(lambda x: x.astype(str).str.lower()) # replace all special characters.
            data.replace(r'[,\"\']','', regex=True).replace(r'\s*([^\s]+)\s*', r'\1', regex=True)
            data.columns = map(str, data.columns)
            data.columns = map(str.lower, data.columns)
            data.columns = data.columns.str.replace(' ','')

            self.data = data
            
            print(self.data.head())
            #self.secondframe.tkraise()
            self.second_frame()

            #except:
            #    statusText.set("Error reading file" + str(filename))
            #pass

    def second_frame(self):

        print("Second frame initialized")

        self.secondframe = tk.Frame(self.master,width=300, height=350)
        self.secondframe.grid(row=0, column=0, sticky="nsew")

        tk.Frame(self.secondframe, height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, padx=5, pady=5)

        self.warnings=0
        self.var_dict = {}
        self.statusText = tk.StringVar(self)
        self.statusText.set(" ")

        # Create explanatory label
        tk.Label(self.secondframe, text="Please enter the desired percentage of individuals to be assigned to the control group").pack()
        self.second_frame_entry = tk.Entry(self.secondframe, width=50)
        self.second_frame_entry.pack()
        
        for col in self.data.columns:
            print("something is happening")
            if "ccis" in col:
                pass
            elif ("name" in col) or ("Name" in col) or ("Surname" in col):
                pass
            else:
                var_temp = tk.IntVar(value=0)   
                l = tk.Checkbutton(self.secondframe, text=col, variable=var_temp) 
                l.pack()  
                self.var_dict[col] = var_temp

        tk.Button(self.secondframe,text="Generate sample",command=lambda: self.button_stratify_callback()).pack()
        tk.Button(self.secondframe,text="See resulting balance",command=lambda: self.button_balance_callback()).pack()
        tk.Button(self.secondframe,text="Return",command=lambda: self.mainframe.tkraise()).pack()
        tk.Button(self.secondframe,text="Exit",command=tk.sys.exit).pack()

        self.message = tk.Label(self.secondframe, textvariable=self.statusText, fg="black")
        self.message.configure(fg="black")
        self.message.pack()        

    def button_stratify_callback(self):

        for cols,vs in self.var_dict.iteritems():
            if vs.get():
                if "dob" in cols.lower():
                    temp_dates = []
                    for dob in self.data[cols]:
                        try:
                            birth_year = int(dt.datetime.strptime(dob,'%d/%M/%y').year)
                            if birth_year > 2000:
                                birth_year -= 100
                            age = dt.datetime.now().year - birth_year
                        except ValueError:
                            pass
                    del(self.data[cols])
                    self.data["Age"] = age
                    self.strat_columns.append(cols)
                elif (cols == "PO") or (cols=="Judge"):
                    self.controller.raise_vble_warning = True
                    if self.warnings>0:    
                        self.strat_columns.append(cols)
                else:
                    self.strat_columns.append(cols)
        
        if self.raise_vble_warning and (self.warnings<1):
            self.warning_1(self.var_dict,self.second_frame_entry,self.statusText,self.message)
        else:
            #try:
            self.sample_p = int(self.second_frame_entry.get())
            n = len(self.data)
            min_n = len(self.strat_columns)*2

            if min_n >= n:
                self.statusText.set("Too many columns selected for the sample size. Try selecting less columns for stratification.")
                self.message.configure(fg="red")
            
            if 0 <= self.sample_p <= 100:
                print(self.strat_columns)
                prefix = stratify(self) 
                if prefix is None:
                    self.statusText.set("Error creating random sample.")
                    self.message.configure(fg="red")
                else:
                    self.statusText.set("Output is in file {}".format(prefix))
                    # Consider adding a timestamp.
                    self.message.configure(fg="black")
            else: 
                self.statusText.set("Please enter a number between 0 and 100")
                self.message.configure(fg="red")
            #except ValueError:
            #    statusText.set("Please enter a whole number.")
            #    message.configure(fg="red")
        

    def button_balance_callback(self):
        try:
            self.rct = pd.read_excel(self.filename.rsplit(".")[0]+","+",".join(self.strat_columns)+'-'+str(self.sample_p)+'_RCT'+'.xlsx')
            self.balance_frame(base_data=self.rct)
        except:
            self.statusText.set("It is first necessary to create a randomized sample.")
            self.message.configure(fg="red")

    def warning_1(self):
        self.tkMessageBox.showinfo("Warning","We suggest not to randomize based on parole officers or judges.")
        self.warnings += 1
        print("At prompt function: "+str(self.warnings))
        self.statusText.set("Select columns.")
        self.message.configure(fg="Black")
        self.button_stratify_callback(self)

    def balance_frame(self,base_data,new_data=pd.DataFrame([])):
        self.balanceframe = tk.Frame(self.master,width=666, height=950)
        self.balanceframe.grid(row=0, column=0, sticky="nsew")
        #self.master.minsize(width=666, height=950)

        self.label = tk.Label(self.balanceframe, text="Balance of the selected covariates")
        self.label.config(font=("Arial", 34))
        self.label.pack()

        tk.Label(self.balanceframe, text="Control group size: ")
        tk.Label(self.balanceframe, text="Intervention group size: ")

        print("Balance frame initiated")
        i = 0
        if len(self.strat_columns)>0:
            print("Has length")
            fig, axes = plt.subplots(len(self.strat_columns),1) 
            #if hasattr(axes, '__iter__'):
            try:
                for row in axes:
                    print("Tried here")
                    ax_curr = axes[i]
                    if self.strat_columns[i] != 'age':
                        df = (100*(pd.crosstab(base_data['group-rct'],base_data[self.strat_columns[i]],normalize='columns')))
                        df = df.stack().reset_index().rename(columns={0:'Percentage'}) 
                        ax_curr.axhline(y=self.sample_p,c="darkred",linewidth=1,zorder=3)
                        sns.barplot(hue=df['group-rct'], y=df['Percentage'], x=df[self.strat_columns[i]], ax=ax_curr,zorder=1)
                        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
                        ax_curr.set_ylabel('Percentage [%]')
                        if not new_data.empty:
                            df_pos = (100*(pd.crosstab(new_data['group-rct'],new_data[self.strat_columns[i]],normalize='columns')))
                            df_pos = df_pos.stack().reset_index().rename(columns={0:'Percentage'}) 
                            sns.barplot(hue=df_pos['group-rct'], y=df_pos['Percentage'], x=df_pos[self.strat_columns[i]], ax=ax_curr, ls='dashed', lw = 30, zorder=2)
                    else:
                        sns.boxplot(base_data['group-rct'],base_data[self.strat_columns[i]],ax=ax_curr,zorder=1)
                        if not new_data.empty:
                            sns.boxplot(new_data['group-rct'],new_data[self.strat_columns[i]],ax=ax_curr, ls='dashed', lw = 30, zorder=2)
                            plt.ylim([new_data[self.strat_columns[i]].min(),new_data[self.strat_columns[i]].max()])
                    #plt.ylim([0,100])
                    plt.tight_layout()
                    i+=1
            except:
                print("Tried there")
                ax_curr = axes
                if self.strat_columns[i] != 'age':
                    df = (100*(pd.crosstab(base_data['group-rct'], base_data[self.strat_columns[i]], normalize='columns')))
                    df = df.stack().reset_index().rename(columns={0:'Percentage'}) 
                    print("DATA FRAME PLOTTING - PRE")
                    print(df)
                    ax_curr.axhline(y=self.sample_p,c="darkred",linewidth=1,zorder=3)
                    sns.barplot(hue=df['group-rct'], y=df['Percentage'], x=df[self.strat_columns[i]], ax=ax_curr, zorder=1)
                    ax_curr.set_ylabel('Percentage [%]')
                    if not new_data.empty:
                        df_pos = (100*(pd.crosstab(new_data['group-rct'], new_data[self.strat_columns[i]], normalize='columns')))
                        df_pos = df_pos.stack().reset_index().rename(columns={0:'Percentage'}) 
                        print("DATA FRAME PLOTTING - POS")
                        print(df_pos)
                        sns.barplot(hue=df_pos['group-rct'], y=df_pos['Percentage'],x=df_pos[self.strat_columns[i]],ax=ax_curr,ls='dashed',lw=30,zorder=2)
                        plt.ylabel('Percentage [%]')
                else:
                    print("BASE DATA")
                    print(base_data)
                    print("TYPE OF DATA")
                    print(type(base_data))
                    sns.boxplot(base_data['group-rct'],base_data[self.strat_columns[i]].astype('float'),zorder=1,ax=ax_curr)
                    ax_curr.set_ylabel('Percentage [%]')
                    if not new_data.empty:
                        sns.boxplot(new_data['group-rct'],new_data[self.strat_columns[i]],ax=ax_curr,ls='dashed',lw=30,zorder=2)
                        plt.ylim([new_data[self.strat_columns[i]].min(),new_data[self.strat_columns[i]].max()])
                #plt.ylim([0,100])
                plt.tight_layout()

            self.canvas = FigureCanvasTkAgg(fig, self.balanceframe)
            self.canvas.show()
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            self.toolbar = NavigationToolbar2TkAgg(self.canvas, self.balanceframe)
            self.toolbar.update()
            self.canvas._tkcanvas.pack(fill=tk.BOTH, expand=True)

        #except:
            #pass
        tk.Button(self.balanceframe, text="Return to main window",command=lambda:self.main_frame()).pack()
        tk.Button(self.balanceframe,text="Exit",command=tk.sys.exit).pack()
        

    def first_frame_existing(self):
        
        self.firstframeexisting = tk.Frame(self.master)
        self.firstframeexisting.grid(row=0, column=0, sticky="nsew")
        #self.firstframeexisting.pack(fill="both", expand=True)

        self.var_dict = {}

        self.statusText_ffe = tk.StringVar(self.firstframeexisting)
        self.statusText_ffe.set("")

        self.label = tk.Label(self.firstframeexisting, text="Please load the _RCT file that was already randomized: ")
        self.label.pack()
        self.entry1 = tk.Entry(self.firstframeexisting, width=50)
        self.entry1.pack()
        
        tk.Button(self.firstframeexisting, text="Browse", command=lambda: self.button_browse_callback_1()).pack()
        tk.Label(self.firstframeexisting, text="Please load a file with new individuals to randomize: ").pack()
    
        self.entry2 = tk.Entry(self.firstframeexisting, width=50)
        self.entry2.pack()

        tk.Frame(self.firstframeexisting, height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, padx=5, pady=5)

        tk.Button(self.firstframeexisting,text="Browse",command=lambda: self.button_browse_callback_2()).pack()    
        tk.Button(self.firstframeexisting, text="Go", command=lambda: self.button_go_callback_2()).pack()
        tk.Button(self.firstframeexisting, text="Return", command=lambda: self.mainframe.tkraise()).pack()
        tk.Button(self.firstframeexisting,text="Exit",command=tk.sys.exit).pack()    

        tk.Frame(self.firstframeexisting, height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, padx=5, pady=5)

        self.message_ffe = tk.Label(self.firstframeexisting, textvariable=self.statusText_ffe)
        self.message_ffe.pack()
        
        
    def button_browse_callback_1(self):
        self.filename1 = tkFileDialog.askopenfilename()
        self.entry1.delete(0, tk.END)
        self.entry1.insert(0, self.filename1)
        return self.filename1

    def button_browse_callback_2(self):
        self.filename2 = tkFileDialog.askopenfilename()
        self.entry2.delete(0, tk.END)
        self.entry2.insert(0, self.filename2)
        return self.filename2

    def button_go_callback_2(self):
        input_file_1 = self.entry1.get()
        input_file_2 = self.entry2.get()

        print("Go 2 callback")

        if (input_file_1.rsplit(".")[-1] not in ["xlsx"]) or (input_file_2.rsplit(".")[-1] not in ["csv","xlsx","xls"]):
            self.statusText_ffe.set("RCT file must end in xlsx and new file must be in a valid format csv,xlsx,xls.")
            self.message_ffe.configure(fg="red")
            print("Case 1")
        else:
            if input_file_1.rsplit(".")[0].rsplit("_")[-1] not in ["RCT"] :
                self.statusText_ffe.set("RCT file must have been generated by this program. Its name should end in _RCT")
                self.message_ffe.configure(fg="red")
                print("Case 2")
            else:    
                print("Case 3")
                data_rct = pd.read_excel(self.filename1)
                # delete empty columns
                data_rct.dropna(axis=1,how='all',inplace=True)
                data_rct.dropna(axis=0,how='all',inplace=True)
                #data_rct.columns = map(str.lower, map(str, data_rct.columns)).str.replace(' ','')

                data_rct.columns = map(str, data_rct.columns)
                data_rct.columns = map(str.lower, data_rct.columns)
                data_rct.columns=data_rct.columns.str.replace(' ','')

                # remove upper case.
                try:
                    data_rct = data_rct.apply(lambda x: x.astype(str).str.lower())
                except UnicodeEncodeError:
                # replace all special characters.
                    data_rct.replace(r'[,\"\']','', regex=True).replace(r'\s*([^\s]+)\s*', r'\1', regex=True, inplace=True)
                self.data_rct = data_rct

                data_new = pd.read_excel(self.filename2)
                # delete empty columns
                data_new.dropna(axis=1,how='all',inplace=True)
                data_new.dropna(axis=0,how='all',inplace=True,subset=data_new.columns[2:])
                # remove upper case.
                data_new = data_new.apply(lambda x: x.astype(str).str.lower())
                # replace all special characters.
                data_new.replace(r'[,\"\']','', regex=True).replace(r'\s*([^\s]+)\s*', r'\1', regex=True, inplace=True)
                
                data_new.columns = map(str, data_new.columns)
                data_new.columns = map(str.lower, data_new.columns)
                data_new.columns = data_new.columns.str.replace(' ','')
                self.data_new = data_new 
                print(data_rct.head())
                print(data_new.head())
                if 'group-rct' in data_rct.columns:
                    print("And we got in")
                    if set(data_rct.columns)-set(['group-rct','date']) ==  set(data_new.columns):
                        self.sample_p = self.filename1.rsplit("-")[-1].rsplit("_")[0]
                        try:
                            strat_columns = self.filename1.rsplit("-")[-2].rsplit(",")[1:]
                            self.strat_columns = [''.join(c.lower() for c in x if not c.isspace()) for x in strat_columns]
                        except IndexError:
                            self.strat_columns = []
                            pass
                        print("Second window should pop")
                        self.prefix = update_stratification(self)
                        if self.prefix is None:
                            self.statusText_ffe.set("Error updating sample.")
                            self.message_ffe.configure(fg="red")
                        else:
                            self.second_frame_existing()                
                    else:
                        print("Message should appear")
                        self.statusText_ffe.set("Files must have the same structure (columns).")
                        self.message_ffe.configure(fg="red")
                else:                    
                    self.statusText_ffe.set("The file should have been generated by this own program and thus have a Group-RCT column.")
                    self.message_ffe.configure(fg="red")
                #pass
            #pass

    def second_frame_existing(self):

        self.secondframeexisting = tk.Frame(self.master)
        self.secondframeexisting.grid(row=0, column=0, sticky="nsew")
        #fill="both", expand=True
        self.warnings=0
        self.var_dict = {}

        self.statusText = tk.StringVar(self.secondframeexisting)
        self.statusText.set("What would you like to do?")

        tk.Label(self.secondframeexisting, textvariable=self.statusText).pack()
        
        tk.Button(self.secondframeexisting, text="See resulting balance", command=lambda: self.balance_frame(base_data=self.data_rct,new_data=self.total_data)).pack()
        tk.Button(self.secondframeexisting, text="Return", command=lambda: self.mainframe.tkraise()).pack()
        tk.Button(self.secondframeexisting, text="Exit", command=tk.sys.exit).pack()

        self.statusText_up = tk.StringVar(self.secondframeexisting)
        self.statusText_up.set("Output is in file {}".format(self.prefix))

        self.message_sf = tk.Label(self.secondframeexisting, textvariable=self.statusText_up)
        self.message_sf.configure(fg="black")
        self.message_sf.pack() 

    def warning_1(self):
        tkMessageBox.showinfo("Warning","We suggest not to randomize based on parole officers or judges.")
        self.warnings += 1
        print("At prompt function: "+str(self.warnings))
        self.statusText.set("Select columns.")
        self.message.configure(fg="Black")
        self.button_stratify_callback(self)

        
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Beta-randomizer")
    
    my_gui = gui(root)
    root.mainloop()