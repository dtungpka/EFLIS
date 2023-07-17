import tkinter as tk
import electric_field as ef
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk
#import file dialog
from tkinter import filedialog
import matplotlib.pyplot as plt
import math
import os

basedir = os.getcwd()
class EntryPopup(ttk.Entry):
    def __init__(self, parent, iid, column, text,index,Field, **kw):
        ttk.Style().configure('pad.TEntry', padding='1 1 1 1')
        super().__init__(parent, style='pad.TEntry', **kw)
        self.tv = parent
        self.iid = iid
        self.column = column
        self.Field = Field
        self.index = index
        self.insert(0, text) 
        # self['state'] = 'readonly'
        # self['readonlybackground'] = 'white'
        # self['selectbackground'] = '#1BA1E2'
        self['exportselection'] = False

        self.focus_force()
        self.select_all()
        self.bind("<Return>", self.on_return)
        self.bind("<Control-a>", self.select_all)
        self.bind("<Escape>", lambda *ignore: self.destroy())
        self.bind("<FocusOut>", self.on_return)



    def on_return(self, event):
        rowid = self.tv.focus()
        vals = self.tv.item(rowid, 'values')
        vals = list(vals)
        print(self.index)
        try:
            vals[self.column] = float(self.get())
        except ValueError:
            vals[self.column] = 0
            self.tv.item(rowid, values=vals)
            self.destroy()
        
        if vals[2] == '0' or vals[2] == '1 C':
            vals[2] = ef.float_to_metric_prefix(1)
        #if len(self.Field.charges) == 0 or self.index >= len(self.Field.charges):
            #self.Field.add_charge(ef.metric_prefix_to_float(vals[2]),[float(vals[0]),float(vals[1])])
        #else:
        #self.Field.charges[self.index].
        pos = [float(vals[0]),float(vals[1])]
        
        if ef.metric_prefix_to_float(vals[2]) != 0:
            q = ef.metric_prefix_to_float(vals[2]) 
        else:
            q = self.Field.charges[self.index].q
        self.Field.modify_charge(self.index,q=q,pos=pos)
        if self.column == 2:
            vals[self.column] = ef.float_to_metric_prefix(vals[self.column])
        self.tv.item(rowid, values=vals)
        self.destroy()


    def select_all(self, *ignore):
        ''' Set selection on the whole text '''
        self.selection_range(0, 'end')

        # returns 'break' to interrupt default key-bindings
        return 'break'
class EditChargeWindow(tk.Toplevel):
    def __init__(self,master,Field: ef.Field):
        super().__init__(master)
        self.Field = Field
        self.title("Edit Charges")
        self.iconbitmap(os.path.join(basedir,"data","icon.ico"))
        self.geometry("600x500")
        self.resizable(False,False)
        self.protocol("WM_DELETE_WINDOW",self.close)
        


        #Create a frame to contain:
        #Below it is a table to show all charges, has 3 columns: x, y, q
        #Below is 2 button: Show Field force, Close
        #The table is scrollable
        #The table is editable,  when the user click on a row, the corresponding charge will be selected, and Delete button will be enabled
        #The first entry is (new), when user click on it, it create new charge

        self.table_frame = tk.Frame(self)
        self.table_frame.pack(side=tk.TOP,fill=tk.BOTH,expand=1)
        self.table_frame.grid_columnconfigure(0,weight=1)
        self.table_frame.grid_columnconfigure(1,weight=1)
        self.table_frame.grid_columnconfigure(2,weight=1)
        
        self.table = ttk.Treeview(self.table_frame,columns=("x","y","q"),show="headings")
        self.table.heading("x",text="x (m)")
        self.table.heading("y",text="y (m)")
        self.table.heading("q",text="q (C)")
        self.table.column("x",width=100)
        self.table.column("y",width=100)
        self.table.column("q",width=100)
        self.table.grid(row=0,column=0,columnspan=3,sticky=tk.NSEW)
        self.table.bind("<ButtonRelease-1>",self.table_click)
        self.table.bind("<Double-Button-1>",self.table_double_click)
        self.table.bind("<Return>",self.table_double_click)
        self.table.bind("<Delete>",self.delete_charge)
        self.table.bind("<BackSpace>",self.delete_charge)
        
        self.table_scrollbar = ttk.Scrollbar(self.table_frame,orient=tk.VERTICAL,command=self.table.yview)
        self.table_scrollbar.grid(row=0,column=3,sticky=tk.NS)
        self.table.configure(yscrollcommand=self.table_scrollbar.set)

       #Add a new charge, when user double click on it or press enter, a new charge will be added
        self.table.insert("",tk.END,values=["(new)"," "," "])
        self.table.focus(self.table.get_children()[-1])
        self.table.see(self.table.get_children()[-1])




        #Add new frame to contain 2 smaller frame beside each other.
        #On the left is a frame contain a label: To calculate the force on a charge, click on the charge in the table
        #- Down is 4 label: Fx, Fy, F, theta
        #On the right is a frame contain a matplotlib canvas to show the charge.
        # - The charge appear as a circle with radius proportional to the charge and a arrow to show the direction of the force

        self.info_frame = tk.Frame(self)
        self.info_frame.pack(side=tk.TOP,fill=tk.BOTH,expand=1)
        self.info_frame.grid_columnconfigure(0,weight=1)
        self.info_frame.grid_columnconfigure(1,weight=1)

        self.info_label_frame = tk.Frame(self.info_frame)
        self.info_label_frame.grid(row=0,column=0,sticky=tk.NSEW)
        self.info_label_frame.grid_columnconfigure(0,weight=1)
        self.info_label_frame.grid_columnconfigure(1,weight=1)
        self.info_label_frame.grid_columnconfigure(2,weight=1)
        self.info_label_frame.grid_columnconfigure(3,weight=1)

        self.info_label = tk.Label(self.info_label_frame,text="To calculate the force on a charge,\n click on the charge in the table")
        self.info_label.grid(row=0,column=0,columnspan=4,sticky=tk.NSEW)

        self.info_label_fx = tk.Label(self.info_label_frame,text="Fx: ")
        self.info_label_fx.grid(row=1,column=0,sticky=tk.NSEW)
        self.info_label_fy = tk.Label(self.info_label_frame,text="Fy: ")
        self.info_label_fy.grid(row=1,column=1,sticky=tk.NSEW)
        self.info_label_f = tk.Label(self.info_label_frame,text="F: ")
        self.info_label_f.grid(row=1,column=2,sticky=tk.NSEW)
        self.info_label_theta = tk.Label(self.info_label_frame,text="theta: ")
        self.info_label_theta.grid(row=1,column=3,sticky=tk.NSEW)

        self.info_canvas_frame = tk.Frame(self.info_frame)
        self.info_canvas_frame.grid(row=0,column=1,sticky=tk.NSEW)
        self.info_canvas_frame.grid_columnconfigure(0,weight=1)
        self.info_canvas_frame.grid_rowconfigure(0,weight=1)


        #Dont show the legend and the axis
        plt.rcParams["axes.spines.left"] = False
        plt.rcParams["axes.spines.right"] = False
        plt.rcParams["axes.spines.top"] = False
        plt.rcParams["axes.spines.bottom"] = False
        plt.rcParams["axes.grid"] = False
        plt.rcParams["legend.frameon"] = False
        plt.rcParams["xtick.bottom"] = False
        plt.rcParams["xtick.labelbottom"] = False
        plt.rcParams["ytick.left"] = False
        plt.rcParams["ytick.labelleft"] = False
        
        self.figure = plt.Figure(figsize=(2,2),dpi=100)
        self.axes = self.figure.add_subplot(111)
        self.axes.set_xlim(-1.5,1.5)
        self.axes.set_ylim(-1.5,1.5)
        self.axes.set_aspect("equal")
        self.info_canvas = FigureCanvasTkAgg(self.figure,self.info_canvas_frame)
        self.info_canvas.get_tk_widget().pack(side=tk.TOP,fill=tk.BOTH,expand=1)
        self.info_canvas.draw()


        self.table_button_frame = tk.Frame(self)
        self.table_button_frame.pack(side=tk.BOTTOM,fill=tk.X)
        self.table_button_frame.grid_columnconfigure(0,weight=1)
        self.table_button_frame.grid_columnconfigure(1,weight=1)

        self.show_field_button = tk.Button(self.table_button_frame,text="Apply",command=self.apply)
        self.show_field_button.grid(row=0,column=0,sticky=tk.NSEW)
        self.close_button = tk.Button(self.table_button_frame,text="Close",command=self.close)
        self.close_button.grid(row=0,column=1,sticky=tk.NSEW)


        self.selected_charge = None
        self.selected_charge_index = None
        self.selected_charge_id = None

        self.update_table()
    def update_table(self):
        datas = self.Field.charges
        self.table.delete(*self.table.get_children())
        for charge in datas:
            self.table.insert("",tk.END,values=[charge.pos[0],charge.pos[1],ef.float_to_metric_prefix(charge.q)])
        self.table.insert("",tk.END,values=["(new)"," "," "])

    def table_click(self,event):
        self.selected_charge = self.table.item(self.table.focus())["values"]
        
        self.selected_charge_id = self.table.focus()
        if self.selected_charge[0] != "(new)":
            #Allow delete
            self.selected_charge_index = self.table.index(self.table.focus())
            self.table.bind("<Delete>",self.delete_charge)
            self.table.bind("<BackSpace>",self.delete_charge)
            self.get_force()
        else:
            #Disallow delete
            self.table.unbind("<Delete>")
            self.table.unbind("<BackSpace>")
    def table_double_click(self,event):
        if self.selected_charge[0] == "(new)":
            #Create new charge
            self.table.item(self.selected_charge_id,values=[0,0,'1 C'])
            self.selected_charge = [0,0,0]
            self.selected_charge_index = self.table.index(self.selected_charge_id)
            self.selected_charge_id = self.table.focus()
            self.table.focus(self.selected_charge_id)
            self.table.see(self.selected_charge_id)
            self.table.bind("<Delete>",self.delete_charge)
            self.table.bind("<BackSpace>",self.delete_charge)

            #insert (new) again
            self.table.insert("",tk.END,values=["(new)"," "," "])
            self.Field.add_charge(1,[0,0])
        else:
            #Edit charge
            self.edit_charge(event)
    def delete_charge(self,event):
        if self.selected_charge[0] != "(new)":
            self.table.delete(self.selected_charge_id)
            self.Field.delete_charge(self.selected_charge_index)
            self.selected_charge = None
            self.selected_charge_index = None
            self.selected_charge_id = None
            self.table.unbind("<Delete>")
            self.table.unbind("<BackSpace>")
    def edit_charge(self,event):
        ''' Executed, when a row is double-clicked. Opens 
        read-only EntryPopup above the item's column, so it is possible
        to select text '''

        # close previous popups
        try:  # in case there was no previous popup
            self.entryPopup.destroy()
        except AttributeError:
            pass

        # what row and column was clicked on
        rowid = self.table.identify_row(event.y)
        column = self.table.identify_column(event.x)

        # handle exception when header is double click
        if not rowid:
            return

        # get column position info
        x,y,width,height = self.table.bbox(rowid, column)

        # y-axis offset
        pady = height // 2

        # place Entry popup properly
        text = self.table.item(rowid, 'values')[int(column[1:])-1]
        if int(column[1:])-1 == 2:
            text = str(ef.metric_prefix_to_float(text))
        self.table.entryPopup = EntryPopup(self.table, rowid, int(column[1:])-1, text,self.selected_charge_index,self.Field)
        self.table.entryPopup.place(x=x, y=y+pady, width=width, height=height, anchor='w')
    def get_force(self):
        #Get the force on the selected charge, show it in the info canvas
        if self.selected_charge[0] != "(new)":
            self.axes.clear()
            #get charge by index
            charge = self.Field.charges[self.selected_charge_index]
            #get epsilon from eps0 entry, convert to float
            try:
                eps0 = self.Field.eps0
            except ValueError:
                eps0 = 1
            NF = ef.NetForce(charge,self.Field,eps0)
            fx,fy = NF.get_net_force()
            F = NF.get_net_force_magnitude()
            self.info_label_fx["text"] = f"Fx:{ef.float_to_metric_prefix(fx,'N')}"
            self.info_label_fy["text"] = f"Fy:{ef.float_to_metric_prefix(fy,'N')}"
            self.info_label_f["text"] = f"F:{ef.float_to_metric_prefix(F,'N')}"

            theta = NF.get_net_force_theta()
            #Rad to deg
            theta = theta * 180 / math.pi
            self.info_label_theta["text"] = f"θ:{round(theta,2)}°"

            #Draw force vector
            #Clear the canvas   
            #self.info_canvas.delete("all")
            #Draw the force vector
            #Normalize the force vector, with F = 1, so the vector is 1 unit long
            fx = fx / F
            fy = fy / F

            if fx != 0:
                self.axes.annotate("", xy=(fx, 0), xytext=(0, 0),arrowprops=dict(arrowstyle="->",color="red"))
            if fy != 0:
                self.axes.annotate("", xy=(0, fy), xytext=(0, 0),arrowprops=dict(arrowstyle="->",color="red"))
            self.axes.annotate("", xy=(fx, fy), xytext=(0, 0),arrowprops=dict(arrowstyle="->"))
            self.Field.get_min_charges()
            size = 20 * math.sqrt(abs(charge.q/self.Field.min_charges))
            #Draw the charge, if the charge > 0, draw a +, else draw a -
            if charge.q > 0:
                #Draw a red circle and a + sign
                self.axes.plot(0,0,"ro" ,markersize=size)

            else:
                #Draw a blue circle and a - sign
                self.axes.plot(0,0,"bo" ,markersize=size)
            self.axes.set_xlim(-1,1)
            self.axes.set_ylim(-1,1)
            self.axes.set_aspect('equal')
            self.axes.axis('off')
            self.axes.figure.canvas.draw()


        else:
           #Clear the canvas
            self.info_label_fx["text"] = "Fx:"
            self.info_label_fy["text"] = "Fy:"
            self.info_label_f["text"] = "F:"
            self.info_label_theta["text"] = "θ:"
            self.axes.clear()
            self.axes.figure.canvas.draw()



            

    def close(self):
        self.destroy()
    def apply(self):
        self.master.refresh_plot()
        self.destroy()
