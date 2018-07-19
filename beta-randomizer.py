#!/usr/bin/python2.7

"""

Stratified random sample generator for BetaGov.
Author: S. Arango-Franco - sarangof@nyu.edu.
2017.

"""

[u'Trial #', u'Date Consent Signed', u'Sentenced or Detained', u'Risk Level', u'Age', u'Sex', u'Race', u'Hispanic', u'Mentoring']

import Tkinter as tk
from Tkinter import BooleanVar,StringVar
import tkFileDialog
import tkMessageBox
import pandas as pd 
import datetime as dt
from beta_functions import *
import matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import ImageTk, Image
#from matplotlib.figure import Figure


#from datetime import datetime

sns.set_style("whitegrid")

def standardize_columns(data):
    df_str_columns = data.select_dtypes(exclude=[np.datetime64,np.number])
    for cols in df_str_columns.columns:
        data[cols] = data[cols].str.strip()
        data[cols] = data[cols].map(lambda x: str(x).replace('-', ''))
    return data

def clear_variables(self):
    self.strat_columns = []

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
        #print("Main frame initialized")

        self.data, self.rct, self.data_rct, self.data_new, self.total_data = pd.DataFrame([]), pd.DataFrame([]), pd.DataFrame([]), pd.DataFrame([]), pd.DataFrame([])
        self.filename, self.filename1, self.filename2 = "","",""
        self.prefix = ''
        self.strat_columns = []
        self.sample_p = 0
        self.raise_vble_warning = False
        self.name = None
        self.pure_randomization_text = 'Pure randomization'
        self.pure_randomization_boolean = False

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
        self.statusText.set("Press Browse or enter CSV filename, "
                        "then press Next")
        self.label = tk.Label(self.firstframe, text = "Please load a file: ").pack(expand=True)

        self.first_frame_entry = tk.Entry(self.firstframe, width=50)
        self.first_frame_entry.pack(expand=True)

        tk.Frame(self, height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, padx=5, pady=5)

        tk.Button(self.firstframe, text="Browse", command=lambda: self.button_browse_callback()).pack(expand=True)
        tk.Button(self.firstframe, text="Next", command=lambda: self.button_go_callback()).pack(expand=True)
        tk.Button(self.firstframe, text="Back", command=lambda: self.mainframe.tkraise()).pack(expand=True)
        tk.Button(self.firstframe, text="Exit", command=tk.sys.exit).pack(expand=True, side=tk.BOTTOM)

        tk.Frame(self.firstframe, height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, padx=5, pady=5)

        self.message = tk.Label(self, textvariable=self.statusText)
        self.message.pack(expand=True)

    def button_browse_callback(self):
        self.filename = tkFileDialog.askopenfilename()
        self.first_frame_entry.delete(0, tk.END)
        self.first_frame_entry.insert(0, self.filename)

    def button_go_callback(self):

        """ what to do when the "Go" button is pressed """
        
        #print("Go callback")
        input_file = self.first_frame_entry.get()

        if input_file.rsplit(".")[-1] not in ["csv","xlsx","xls"] :
            self.statusText.set("Filename must end in `.xlsx', '.csv' or '.xls'")
            self.message.configure(fg="red")
        else:
            data = pd.read_excel(self.filename) 
            data.dropna(axis=1,inplace=True,how='all') # delete empty columns.
            data.dropna(axis=0,inplace=True,how='all') # delete empty rows.
            data = data.apply(lambda x: x.astype(str).str.lower()) # lower caps.
            data.replace(r'[,\"\']','', regex=True).replace(r'\s*([^\s]+)\s*', r'\1', regex=True) # replace all special characters.
            data.columns = map(str, data.columns) 
            data.columns = [''.join(str.lower(e) for e in string if e.isalnum()) for string in data.columns] # replace all special characters in columns.
            data = data.apply(lambda x: x.astype(str).str.lower()) # perhaps redundant.
            data = standardize_columns(data) # make sure values have no spaces
            self.data = data
            
            self.second_frame()
            #print(self.data.head())
            #self.secondframe.tkraise()

    def second_frame(self):        
        #print("Second frame initialized")

        def cb(self):
            #print("came in")
            for it in self.var_dict:
                it.config(state=DISABLED)
            self.refresh()

        self.secondframe = tk.Frame(self.master,width=300, height=350)
        self.secondframe.grid(row=0, column=0, sticky="nsew")

        tk.Frame(self.secondframe, height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, padx=5, pady=5)

        self.warnings = 0
        self.var_dict = {}
        self.statusText = tk.StringVar(self)
        self.statusText.set(" ")

        # Create explanatory label
        tk.Label(self.secondframe, text="Please enter a desired percentage of individuals to be assigned to the control group").pack()
        self.second_frame_entry = tk.Entry(self.secondframe, width=50)
        self.second_frame_entry.pack()
        
        tk.Label(self.secondframe, text="Please select features from the following list to create a randomization").pack()

        #var_PR = tk.IntVar(value=0)  
        #li = tk.Checkbutton(self.secondframe,text='Pure randomization',variable=var_PR,command=cb(self))
        #li.pack()
        #self.var_PureRand = var_PR
        if not self.data.empty:
            col_possibilities = [self.pure_randomization_text]+list(self.data.columns[1:].values)
            #print(list(self.data.columns[1:].values))
            #print(col_possibilities)
            for col in col_possibilities:
                #print("something is happening")
                if ("ccis" in col) or ("name" in col) or ("Name" in col) or ("Surname" in col):
                    pass
                else:
                    var_temp = tk.IntVar(value=0)   
                    l = tk.Checkbutton(self.secondframe, text=col, variable=var_temp) 
                    self.var_dict[col] = var_temp
                    l.pack()  

        tk.Button(self.secondframe,text="Generate sample",command=lambda: self.button_stratify_callback()).pack()
        tk.Button(self.secondframe,text="See resulting balance",command=lambda: self.button_balance_callback()).pack()
        tk.Button(self.secondframe,text="Back",command=lambda: self.mainframe.tkraise()).pack()
        tk.Button(self.secondframe,text="Exit",command=tk.sys.exit).pack()

        self.message = tk.Label(self.secondframe, textvariable=self.statusText, fg="black")
        self.message.configure(fg="black")
        self.message.pack()        

    def button_stratify_callback(self):

        def set_stratifying_variables(self):
            for cols,vs in self.var_dict.iteritems():
                if vs.get():
                    if cols==self.pure_randomization_text:
                        self.pure_randomization_boolean = True
                    elif "dob" in cols.lower():
                        try:
                            self.data[cols] = pd.to_datetime(self.data[cols])
                        except:
                            pass
                        age_list = []
                        for dob in self.data[cols]:
                            try:
                                if isinstance(dob,datetime):
                                    birth_year = dob.year
                                else:
                                    try:
                                        birth_year = int(dt.datetime.strptime(dob,'%d/%M/%y').year)
                                    except ValueError:
                                        pass
                                if birth_year > 2000:
                                    birth_year -= 100
                                age_list.append(dt.datetime.now().year - birth_year)
                            except ValueError:
                                pass
                        del(self.data[cols])
                        # I SHOULD HAVE AN ERROR MESSAGE HERE
                        self.data["age"] = age_list
                        self.strat_columns.append("age")
                    elif (cols == "PO") or (cols=="Judge"):
                        self.controller.raise_vble_warning = True
                        if self.warnings > 0:    
                            self.strat_columns.append(cols)
                    else:
                        self.strat_columns.append(cols)

        clear_variables(self)
        set_stratifying_variables(self)
        
        if self.raise_vble_warning and (self.warnings<1):
            self.warning_1(self)
        else:
            #try:
            if ((not self.strat_columns) and (not self.pure_randomization_boolean)):
                self.empty_strat_variables()
            else:
                self.sample_p = 100.-int(self.second_frame_entry.get())
                n = len(self.data)
                min_n = len(self.strat_columns)*2
                #print(self.sample_p)
                if 0 <= self.sample_p <= 100:
                    #print(self.strat_columns)
                    if min_n >= n:
                        self.warning_toomanycolumns()
                    else:
                        prefix = stratify(self) 
                        if ((self.pure_randomization_boolean) and (self.strat_columns)):
                            self.conflicting_randomizations_warning()
                        else:
                            if prefix is None:
                                self.warning_errorrandomsample()
                            else:
                                self.statusText.set("Output is in file {}".format(prefix))
                                self.message.configure(fg="black")
                else:
                    self.warning_wrongnumber()

            #except ValueError:
            #    self.warning_wrongnumber()


                
            #except ValueError:
            #    statusText.set("Please enter a whole number.")
            #    message.configure(fg="red")
        
    def warning_1(self):
        tkMessageBox.showinfo("Warning","We suggest not to randomize based on parole officers or judges.")
        self.warnings += 1
        #print("At prompt function: "+str(self.warnings))
        self.statusText.set("Select columns.")
        self.message.configure(fg="Black")
        #self.second_frame.tkraise()
        self.second_frame()

    def warning_errorrandomsample(self):
        tkMessageBox.showinfo("Error","Error creating random sample.")
        #print("At prompt function: "+str(self.warnings))
        self.message.configure(fg="Black")
        self.second_frame()

    def warning_toomanycolumns(self):
        tkMessageBox.showinfo("Error","Too many columns to randomize.")
        #print("At prompt function: "+str(self.warnings))
        self.message.configure(fg="Black")
        self.second_frame()

    def warning_wrongnumber(self):
        tkMessageBox.showinfo("Error","Please enter a number between 0 and 100.")
        #print("At prompt function: "+str(self.warnings))
        self.message.configure(fg="Black")
        self.second_frame()

    def empty_strat_variables(self):
        tkMessageBox.showinfo("Error","Please enter at least one stratifying variable.")
        self.message.configure(fg="Black")
        self.second_frame()

    def conflicting_randomizations_warning(self):
        tkMessageBox.showinfo("Error","Please choose between either Pure Randomization or a set of variables to stratify.")
        self.message.configure(fg="Black")
        self.pure_randomization_boolean = False
        self.strat_columns = []
        self.second_frame()

    def button_balance_callback(self):
        if self.name:
            self.rct = pd.read_excel(self.name)
            self.balance_frame(base_data=self.rct)
        else:
            self.statusText.set("It is first necessary to create a randomized sample.")
            self.message.configure(fg="red")

    def balance_frame(self,base_data,new_data=pd.DataFrame([])):
        self.balanceframe = tk.Frame(self.master,width=666, height=950)
        self.balanceframe.grid(row=0, column=0, sticky="nsew")
        #self.master.minsize(width=666, height=950)

        self.label = tk.Label(self.balanceframe, text="Balance of the selected covariates")
        self.label.config(font=("Arial", 34))
        self.label.pack()

        try:
            tk.Label(self.balanceframe, text="").pack()
            tk.Label(self.balanceframe, text="Target control group size: "+str(int(self.sample_p))+"% of population").pack()
            tk.Label(self.balanceframe, text="Control group size: "+str(base_data['group-rct'].value_counts().loc['control'])+'('+str(round(100*base_data['group-rct'].value_counts(normalize=True).loc['control'],2))+'%)').pack()
            tk.Label(self.balanceframe, text="Intervention group size: "+str(base_data['group-rct'].value_counts().loc['intervention'])+ '('+ str(round(100*base_data['group-rct'].value_counts(normalize=True).loc['intervention'],2))+'%)').pack()
            if not new_data.empty:
                tk.Label(self.balanceframe, text="New Control group size: "+str(new_data['group-rct'].value_counts().loc['control'])+ '('+ str(round(100*new_data['group-rct'].value_counts(normalize=True).loc['control'],2))+'%)').pack()
                tk.Label(self.balanceframe, text="New Intervention group size: "+str(new_data['group-rct'].value_counts().loc['intervention'])+ '('+ str(round(100*new_data['group-rct'].value_counts(normalize=True).loc['intervention'],2))+'%)').pack()
            tk.Label(self.balanceframe, text="").pack()
        except KeyError:
            pass

        #print("Balance frame initiated")
        #print(self.strat_columns)
        
        if len(self.strat_columns)>0:
            #print("Has length")
            #print(hasattr(axes, '__iter__'))
            new_legends = 0
            fig, axes = plt.subplots(len(self.strat_columns),1,figsize=(10,5)) 
            if not new_data.empty:
                
                for i in range(len(self.strat_columns)):
                    try:
                        ax_curr = axes[i]
                    except TypeError:
                        ax_curr = axes 
                    if self.strat_columns[i]!='age':
                        df = (100*(pd.crosstab(base_data['group-rct'], base_data[self.strat_columns[i]], normalize='columns')))
                        df = df.stack().reset_index().rename(columns={0:'Percentage'}) 
                        bpt = sns.barplot(hue=df['group-rct'], y=df['Percentage'], x=df[self.strat_columns[i]], linewidth=2.5, 
                                    facecolor=(1, 1, 1, 0.2), edgecolor=[".1",".1",".1"], errcolor=".2", ls = 'dashed',zorder=2, ax=ax_curr)

                        df_pos = (100*(pd.crosstab(new_data['group-rct'], new_data[self.strat_columns[i]], normalize ='columns')))
                        df_pos = df_pos.stack().reset_index().rename(columns={0:'Percentage'}) 
                        sns.barplot(hue=df_pos['group-rct'], y=df_pos['Percentage'], x=df_pos[self.strat_columns[i]], zorder=1,ax=ax_curr)#,

                        bpt.set_ylabel('Percentage',fontsize='18');
                        #bpt.set_title(self.strat_columns[i], horizontalalignment='center', verticalalignment='top',fontsize=22);
                        bpt.xaxis.label.set_size(18);
                        #bpt.set_xlabel('');
                        #print(self.sample_p)
                        bpt.axhline(y=100.-float(self.sample_p), c="darkred", linewidth=2, zorder=3)
                        handles, labels = bpt.get_legend_handles_labels();
                        if new_legends < 1:
                            lgd_a = bpt.legend(handles[1:],['Previous batch']+labels[2:],loc='center left', bbox_to_anchor=(1, 0.5), fontsize=14);
                        else:
                            lgd = bpt.legend([],[], loc='upper left', bbox_to_anchor=(1, 0.5), fontsize=14)
                        plt.ylim([0,100]);
                        new_legends += 1


                        #plt.show()
                    else:
                        total_data = pd.concat([base_data.copy(),new_data])
                        total_data.loc[:,'Randomization'] = 'Update'
                        base_data.loc[:,'Randomization'] = 'Previous'
                        total_data = pd.concat([total_data,base_data])
                        #print("total data")
                        #print(total_data)
                        total_data[self.strat_columns[i]] = total_data[self.strat_columns[i]].astype(float)
                        ax_bp = sns.boxplot(hue ='group-rct', 
                                            y = self.strat_columns[i],
                                            x = 'Randomization',
                                            data = total_data,
                                            order = ['Previous','Update'],
                                            hue_order = ['control','intervention'],
                                            ax = ax_curr)
                        for patch in ax_bp.artists:
                            r, g, b, a = patch.get_facecolor()
                            #patch.set_facecolor((r, g, b, .3))
                            #patch.set_linestyle('dashed')
                        ax_bp.xaxis.label.set_size(18);
                        ax_bp.yaxis.label.set_size(18);
                        ax_bp.set_xlabel('');
                        plt.legend([]);
                        plt.ylim([new_data[self.strat_columns[i]].astype('float').min(), new_data[self.strat_columns[i]].astype('float').max()+1])
                        handles,labels = ax_bp.get_legend_handles_labels()
                        lgd = ax_bp.legend([],[], loc='upper left', bbox_to_anchor=(1, 0.5), fontsize=14)

            else:
                for i in range(len(self.strat_columns)):
                    try:
                        ax_curr = axes[i]
                    except TypeError:
                        ax_curr = axes
                    if self.strat_columns[i]!='age':
                        df = (100*(pd.crosstab(base_data['group-rct'], base_data[self.strat_columns[i]], normalize='columns')))
                        df = df.stack().reset_index().rename(columns={0:'Percentage'}) 

                        bpt = sns.barplot(hue=df['group-rct'], y=df['Percentage'], x=df[self.strat_columns[i]], ax=ax_curr)
                        bpt.set_ylabel('Percentage',fontsize='18');
                        bpt.axhline(y=100.-self.sample_p, c="darkred", linewidth=2, zorder=3)
                        handles, labels = bpt.get_legend_handles_labels();
                        if new_legends < 1:
                            lgd_a = bpt.legend(handles,labels, loc='upper left', bbox_to_anchor=(1, 0.5), fontsize=14)
                        else:
                            lgd = bpt.legend([],[], loc='upper left', bbox_to_anchor=(1, 0.5), fontsize=14)

                        bpt.xaxis.label.set_size(18);
                        plt.ylim([0,100]);
                        new_legends += 1
                    else:
                        ax_bp = sns.boxplot(x='group-rct', 
                                            y = self.strat_columns[i],
                                            data = base_data,
                                            ax=ax_curr)
                        plt.ylim([base_data[self.strat_columns[i]].astype('float').min(), base_data[self.strat_columns[i]].astype('float').max()+1])
                        lgd = ax_bp.legend([],[], loc='upper left', bbox_to_anchor=(1, 0.5), fontsize=14)
                        ax_bp.set_xlabel('');
                        ax_bp.xaxis.label.set_size(18);
                        ax_bp.yaxis.label.set_size(18);
            
            plt.tight_layout()
            try:
                plt.savefig('Randomization.png', bbox_extra_artists=(lgd_a,), bbox_inches='tight')
            except UnboundLocalError:
                plt.savefig('Randomization.png', bbox_inches='tight')

            path = 'Randomization.png'

            #image_pil = .resize((100,100)) #<-- resize images here    
            img = ImageTk.PhotoImage(Image.open(path))

            self.plot = tk.Label(self.balanceframe, image = img)
            self.plot.image = img
            self.plot.pack()#side = "bottom", fill = "both", expand = "yes")

        else:
            tk.Label(self.balanceframe, text="Pure randomization selected. No variables to compare.",font=(26)).pack()

        tk.Button(self.balanceframe, text="Back to main window",command=lambda:self.main_frame()).pack()#.mainframe.tkraise()).pack()
        tk.Button(self.balanceframe,text="Exit",command=tk.sys.exit).pack()

    def first_frame_existing(self):
        
        self.firstframeexisting = tk.Frame(self.master)
        self.firstframeexisting.grid(row=0, column=0, sticky="nsew")

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
        tk.Button(self.firstframeexisting, text="Browse", command=lambda: self.button_browse_callback_2()).pack()    
        tk.Button(self.firstframeexisting, text="Next", command=lambda: self.button_go_callback_2()).pack()
        tk.Button(self.firstframeexisting, text="Back", command=lambda: self.mainframe.tkraise()).pack()
        tk.Button(self.firstframeexisting, text="Exit", command=tk.sys.exit).pack()    
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

        #print("Go 2 callback")

        if (input_file_1.rsplit(".")[-1] not in ["xlsx"]) or (input_file_2.rsplit(".")[-1] not in ["csv","xlsx","xls"]):
            self.statusText_ffe.set("RCT file must end in xlsx and new file must be in a valid format csv, xlsx or xls.")
            self.message_ffe.configure(fg="red")
            #print("Case 1")
        else:
            if input_file_1.rsplit(".")[0].rsplit("_")[-1] not in ["RCT"] :
                self.statusText_ffe.set("RCT file must have been generated by this program. Its name should end in _RCT")
                self.message_ffe.configure(fg="red")
                #print("Case 2")
            else:    
                #print("Case 3")
                data_rct = pd.read_excel(self.filename1)
                # delete empty columns
                data_rct.dropna(axis=1,how='all',inplace=True)
                data_rct.dropna(axis=0,how='all',inplace=True)

                data_rct.columns = map(str, data_rct.columns)
                #print("data_rct")
                #print(data_rct.columns)
                available_columns = []
                try:
                    available_columns = list(set(data_rct.columns.values) - set(['group-rct','date','batch']))
                except:
                    pass

                data_rct = data_rct.rename(columns={string:''.join(str.lower(e) for e in string if e.isalnum()) for string in available_columns}) #remove all special characters

                # remove upper case.
                try:
                    data_rct = data_rct.apply(lambda x: x.astype(str).str.lower())
                    data_rct = standardize_columns(data_rct)
                    
                except UnicodeEncodeError:
                    # replace all special characters.
                    data_rct.replace(r'[,\"\']','', regex=True).replace(r'\s*([^\s]+)\s*', r'\1', regex=True, inplace=True)

                self.data_rct = data_rct
                #print(data_rct)

                data_new = pd.read_excel(self.filename2)
                # delete empty columns
                data_new.dropna(axis=1,how='all',inplace=True)
                data_new.dropna(axis=0,how='all',inplace=True,subset=data_new.columns[2:])
                # remove upper case.
                #print("data_new")
                #print(data_new)
                data_new = standardize_columns(data_new)
                data_new = data_new.apply(lambda x: x.astype(str).str.lower())
                

                data_new.columns = [''.join(str.lower(str(e)) for e in string if e.isalnum()) for string in data_new.columns]
                # replace all special characters.
                data_new.replace(r'[,\"\']','', regex=True).replace(r'\s*([^\s]+)\s*', r'\1', regex=True, inplace=True)
                
                data_new.columns = map(str, data_new.columns)
                data_new.columns = map(str.lower, data_new.columns)
                data_new.columns = data_new.columns.str.replace(' ','')
                self.data_new = data_new 
                #print(data_rct.head())
                #print(data_new.head())
                if 'group-rct' in data_rct.columns:
                    #print("And we got in")
                    if set(data_rct.columns)-set(['group-rct','date','batch']) ==  set(data_new.columns):
                        self.sample_p = float(self.filename1.rsplit("_")[-2])
                        try:
                            if len(self.filename1.rsplit("|")) <=1:
                                self.statusText_ffe.set("Please check the naming structure of the mother file.")
                            else:
                                strat_columns = self.filename1.rsplit("|")[-1].rsplit("_")[0].rsplit(",")
                            if strat_columns[0] != self.pure_randomization_text:
                                self.strat_columns = [''.join(c.lower() for c in x if not c.isspace()) for x in strat_columns]
                            else:
                                #print("PURE RANDOMIZATION IDENTIFIED")
                                self.pure_randomization_boolean=True
                        except IndexError:
                            self.strat_columns = []
                            pass
                        #print("Second window should pop")
                        common_columns = list(set(data_rct.columns[1:]) & set(data_new.columns[1:]))
                        new_categories = {}
                        for col in self.strat_columns:
                            if col!='age':
                                new_values = set(data_new[col]) - set(data_rct[col])

                                if new_values:
                                    #print("NEW VALUES")
                                    new_categories[col] = new_values

                        if bool(new_categories):
                            self.warning_new_words(new_categories)
                        else:
                            #print("Before second frame existing")
                            #print(self.pure_randomization_boolean)
                            self.prefix = update_stratification(self)
                            if self.prefix is None:
                                self.statusText_ffe.set("Error updating sample.")
                                self.message_ffe.configure(fg="red")
                            else:
                                self.second_frame_existing()                
                    else:
                        #print("Message should appear")
                        available_columns = list(set(data_rct.columns.values) - set(['group-rct','date','batch']))
                        self.statusText_ffe.set("Files must have the same structure (columns). \n Previous column names: "+ str([x.encode('utf-8') for x in data_rct[available_columns].columns.values]) +"\n New column names: "+str([x.encode('utf-8') for x in data_new.columns.values]))
                        self.message_ffe.configure(fg="red")
                else:                    
                    self.statusText_ffe.set("The file should have been generated by this own program and thus have a Group-RCT column.")
                    self.message_ffe.configure(fg="red")
                #pass
            #pass

    def warning_new_words(self,new_categories):
        #print(new_categories)
        for k,value in new_categories.iteritems():
            for nvals in value:
                result = tkMessageBox.askyesno("Warning","The column '"+str(k)+"' has a new value "+str(nvals)+'. Do you accept it?')
                if result == False:
                    tkMessageBox.showinfo("Attention","Please update your file and input it again.")
                    break
            else:
                continue
            self.first_frame_existing()
            break
        else:
            self.prefix = update_stratification(self)
            if self.prefix is None:
                self.statusText_ffe.set("Error updating sample.")
                self.message_ffe.configure(fg="red")
            else:
                self.second_frame_existing()         

    def second_frame_existing(self):

        self.secondframeexisting = tk.Frame(self.master)
        self.secondframeexisting.grid(row=0, column=0, sticky="nsew")
        self.warnings=0
        self.var_dict = {}

        self.statusText = tk.StringVar(self.secondframeexisting)
        self.statusText.set("What would you like to do?")

        tk.Label(self.secondframeexisting, textvariable=self.statusText).pack()
        
        tk.Button(self.secondframeexisting, text="See resulting balance", command=lambda: self.balance_frame(base_data=self.data_rct,new_data=self.total_data)).pack()
        tk.Button(self.secondframeexisting, text="Back", command=lambda: self.mainframe.tkraise()).pack()
        tk.Button(self.secondframeexisting, text="Exit", command=tk.sys.exit).pack()

        self.statusText_up = tk.StringVar(self.secondframeexisting)
        self.statusText_up.set("Output is in file {}".format(self.prefix))

        self.message_sf = tk.Label(self.secondframeexisting, textvariable=self.statusText_up)
        self.message_sf.configure(fg="black")
        self.message_sf.pack() 

        
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Beta-randomizer")
    
    my_gui = gui(root)
    root.mainloop()