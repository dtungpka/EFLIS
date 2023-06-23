import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
import electric_field as ef
import numpy as np
from matplotlib import cm
from scipy.integrate import ode as ode
from itertools import product
from tkinter import ttk



LANG = 0
new_lang = 0
ver = "0.1"
#Create a class, act as main window, inherit from tk.Tk this windows can resize and the element
#inside will resize too.

'''
The main windows have 2 part, the left is the control panel, the right is the plot panel.

'''
#electric_field_cmap= ["RdBu_r",cm.jet,] 
electric_field_cmap = {"Red and Blue":"RdBu_r",
                       "Jet":"jet",
                       "YlOrBr":"YlOrBr",
                       "YlOrRd":"YlOrRd",
                       "OrRd":"OrRd",
                       "PuRd":"PuRd",
                       "RdPu":"RdPu",
                       "BuPu":"BuPu",
                       "GnBu":"GnBu",
                       "PuBu":"PuBu",
                       "YlGnBu":"YlGnBu",
                       "PuBuGn":"PuBuGn",
                       "BuGn":"BuGn",
                       "YlGn":"YlGn",
                       "viridis":"viridis",
                       "plasma":"plasma",
                       "inferno":"inferno",
                       "magma":"magma",
                       "cividis":"cividis",
                       "twilight":"twilight",
                       "twilight_shifted":"twilight_shifted",
                       "turbo":"turbo",
                       "rainbow":"rainbow",
                       "Spectral":"Spectral",
                       "coolwarm":"coolwarm",
                       "bwr":"bwr","seismic":"seismic",
                       "twilight_r":"twilight_r",
                       "twilight_shifted_r":"twilight_shifted_r",
                       "turbo_r":"turbo_r","rainbow_r":"rainbow_r",
                       "Spectral_r":"Spectral_r","coolwarm_r":"coolwarm_r",
                       "bwr_r":"bwr_r","seismic_r":"seismic_r"}


field_line_colors = {"Black":"k","Blue":"b","Green":"g","Red":"r","Cyan":"c","Magenta":"m","Yellow":"y","White":"w"}
class settings:
    border_limit_percent = 1
    default_plot_scale = .8
    field_lines_scale = 0.01
    electric_potential_line_thickness = .5
    field_line_thickness = .5
    field_line_count = 5
    field_line_arrow_density = 0.5
    potential_line_density = 8
    field_cmap = "RdBu_r"
    field_line_color = "k"


    show_charge_value = True
    show_field_line = True
    show_potential_line = False
    show_electric_field = True
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
        if len(self.Field.charges) == 0 or self.index >= len(self.Field.charges):
            self.Field.add_charge(ef.metric_prefix_to_float(vals[2]),[float(vals[0]),float(vals[1])])
        else:
            self.Field.charges[self.index].pos = [float(vals[0]),float(vals[1])]
            self.Field.charges[self.index].q = ef.metric_prefix_to_float(vals[2])
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
        self.title("Edit Charge")
        self.geometry("600x400")
        self.resizable(False,True)
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
        self.table.heading("x",text="x")
        self.table.heading("y",text="y")
        self.table.heading("q",text="q")
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

        self.table_button_frame = tk.Frame(self)
        self.table_button_frame.pack(side=tk.BOTTOM,fill=tk.X)
        self.table_button_frame.grid_columnconfigure(0,weight=1)
        self.table_button_frame.grid_columnconfigure(1,weight=1)

        self.show_field_button = tk.Button(self.table_button_frame,text="Apply",command=self.close)
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
        self.selected_charge_index = self.table.index(self.table.focus())
        self.selected_charge_id = self.table.focus()
        if self.selected_charge[0] != "(new)":
            #Allow delete
            self.table.bind("<Delete>",self.delete_charge)
            self.table.bind("<BackSpace>",self.delete_charge)
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
    def show_field(self):
        pass
    def close(self):
        self.master.setup_plot()
        self.master.setup_ef()
        self.master.update_plot()
        self.master.refresh_plot()
        self.destroy()
        

        


    



class MainWindow(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Electric Field Line Interactive Simulator (EFLIS) v" + ver)
        self.geometry("800x600")
        self.resizable(True, True)
        self.view_setting_buffer = [tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar()]
        #set the view settings to the default value
        self.view_setting_buffer[0].set(settings.show_potential_line)
        self.view_setting_buffer[1].set(settings.show_electric_field)
        self.view_setting_buffer[2].set(settings.show_charge_value)
        self.view_setting_buffer[3].set(settings.show_charge_value)
        self.create_widgets()
        self.EF = ef.Field()
        self.setup_plot()
        self.setup_ef()
        self.update_plot()
        self.update()
        pass
    def setup_ef(self):
        
        ##TODO: Need review
        #self.EF.add_charge(1, [0,0])
        #self.EF.add_charge(-2, [2,0])
        self.set_border()
        self.EF.field_lines(settings.field_lines_scale,self.x_min, self.x_max, self.y_min, self.y_max, settings.field_line_count)
        self.EF.electric_potential(self.x_min, self.x_max, self.y_min, self.y_max)
    def setup_plot(self):
        #self.fig = plt.figure(figsize=(5.5, 4.5),facecolor="w")
        #self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel('$x$')
        self.ax.set_ylabel('$y$')
        #self.ax.set_aspect('equal','datalim')
        #self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        #self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=1)
        pass
    def update_plot(self):

        #Clear the plot
        self.ax.clear()
        if len(self.EF.charges) == 0:
            return
        # plot field line
        if settings.show_field_line:
            for c ,x, y in zip(self.EF.start_charge,self.EF.xs,self.EF.ys):
                c = c/self.EF.min_charges
                #self.ax.plot(x, y, color="k", lw=settings.field_line_thickness)
                #plot with arrow
                #if the charge is positive, the arrow is from begin to end, else the arrow is from end to begin
                if c < 0:
                    #reverse the array
                    x = x[::-1]
                    y = y[::-1]
                self.ax.plot(x, y, color=settings.field_line_color, lw=settings.field_line_thickness)
                #plot arrow at the middle of the line
                for i in range(int(len(x)*settings.field_line_arrow_density),len(x),int(len(x)*settings.field_line_arrow_density)):
                    if i >= len(x)-1 or i == 0:
                        continue
                    dx = x[i] - x[i-1]
                    dy = y[i] - y[i-1]
                    #using annotate to plot arrow
                    self.ax.annotate("", xy=(x[i], y[i]), xytext=(x[i-1], y[i-1]), arrowprops=dict(arrowstyle="->", color=settings.field_line_color, lw=1.5))

                

            

        # plot point charges
        for C in self.EF.charges:
            c = C.q/self.EF.min_charges
            size = 8*np.sqrt(abs(c))
            self.ax.plot(C.pos[0], C.pos[1], 'ro' if c > 0 else 'bo', ms=size)
            if settings.show_charge_value:
                #plot to make the text in the middle of the point
                offset = -0.03 * size/8
                x = C.pos[0] - offset if c < 0 else C.pos[0] + offset
                y = C.pos[1] - offset if c < 0 else C.pos[1] + offset
                self.ax.text(x, y, str(ef.float_to_metric_prefix(C.q)).replace(' ',''), va="center", ha="center", size=size*.8, color="w")
        
        
        
        
        vvs = self.EF.vvs
        xxs = self.EF.xxs
        yys = self.EF.yys
        # plot electric potential
        clim0,clim1 = -settings.potential_line_density,settings.potential_line_density
        vvs[np.where(vvs<clim0)] = clim0*0.999999 # to avoid error
        vvs[np.where(vvs>clim1)] = clim1*0.999999 # to avoid error
        if settings.show_potential_line:
            self.ax.tricontour(xxs,yys,vvs,10,linewidths=settings.electric_potential_line_thickness,colors="0.3")
        if settings.show_electric_field:
            self.ax.tricontourf(xxs,yys,vvs,100,cmap= settings.field_cmap) #TODO:cm.jet
        #cbar = self.ax.figure.colorbar(self.ax.collections[0])
        #cbar.set_ticks(np.linspace(clim0,clim1,5))
        #cbar.set_label("Electric Potential")
        self.ax.set_xlim(self.default_x_min, self.default_x_max)
        self.ax.set_ylim(self.default_y_min, self.default_y_max)
   
    def set_border(self):  
        #Limit the plot area
        default_value = 0.001
        #Loop through all the particles to find the border, which is the max and min of x and y,
        #Calculate by example: x_max = x + x * 0.1
        positions = self.EF.get_positons() # [[x1,y1],[x2,y2]...]
        per = settings.border_limit_percent
        for pos in positions:
            if abs(pos[0])  > default_value:
                default_value = abs(pos[0]) 
            if abs(pos[1])  > default_value:
                default_value = abs(pos[1])
        self.x_min = -default_value * (1 + per)
        self.x_max = default_value * (1 + per)
        self.y_min = -default_value * (1 + per)
        self.y_max = default_value * (1 + per)
        self.default_x_min = -default_value * (1 + settings.default_plot_scale)
        self.default_x_max = default_value * (1 + settings.default_plot_scale)
        self.default_y_min = -default_value * (1 + settings.default_plot_scale)
        self.default_y_max = default_value * (1 + settings.default_plot_scale)
        
        pass

    def refresh_plot(self):
        #clear the plot and redraw it
        self.ax.clear()
        self.setup_ef()
        self.update_plot()
        self.canvas.draw()
        self.canvas.flush_events()
        pass



    def create_widgets(self):
        
        #Create a frame to contain the control panel and the plot panel
        self.frame = tk.Frame(self)
        self.frame.pack(fill=tk.BOTH, expand=True)

        #Create a Menu bar, which contains theL File, View, Help
        self.menu_bar = tk.Menu(self)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        #New, Open, Save,Export, Exit

        self.file_menu.add_command(label="New", command=self.new)
        self.file_menu.add_command(label="Open", command=self.open)
        self.file_menu.add_command(label="Save", command=self.save)
        self.file_menu.add_command(label="Export", command=self.export)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.quit)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        #View
        self.view_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.view_menu.add_checkbutton(label="Potential Line", onvalue=1, offvalue=0, variable=self.view_setting_buffer[0], command=self.view_toggle)
        self.view_menu.add_checkbutton(label="Electric Field", onvalue=1, offvalue=0, variable=self.view_setting_buffer[1], command=self.view_toggle)
        self.view_menu.add_checkbutton(label="Charge Value", onvalue=1, offvalue=0, variable=self.view_setting_buffer[2], command=self.view_toggle)
        self.view_menu.add_checkbutton(label="Field Line", onvalue=1, offvalue=0, variable=self.view_setting_buffer[3], command=self.view_toggle)
        self.menu_bar.add_cascade(label="View", menu=self.view_menu)
        #Help
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label="About", command=self.about)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        self.config(menu=self.menu_bar)
        





        #Create a frame to contain the control panel
        self.control_panel = tk.Frame(self.frame )
        self.control_panel.pack(side=tk.LEFT, fill=tk.Y)
        #Create a frame to contain the plot panel
        self.plot_panel = tk.Frame(self.frame)
        self.plot_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        #create a frame in the control panel to contain all view settings
        self.view_settings_frame = tk.LabelFrame(self.control_panel, text="View Settings")
        #This frame control all toggle buttons, including show_potential_line, show_electric_field, show_charge_value
        self.view_settings_frame.pack(fill=tk.X)
        #Create a toggle button to show/hide the electric potential line, call self.view_toggle when clicked
        self.show_potential_line_button = tk.Checkbutton(self.view_settings_frame, text="Show Potential Line", variable= self.view_setting_buffer[0], command=self.view_toggle)
        self.show_potential_line_button.pack(fill=tk.X)
        #Create a toggle button to show/hide the electric field, call self.view_toggle when clicked
        self.show_electric_field_button = tk.Checkbutton(self.view_settings_frame, text="Show Electric Field", variable= self.view_setting_buffer[1], command=self.view_toggle)
        self.show_electric_field_button.pack(fill=tk.X)
        #Create a toggle button to show/hide the charge value, call self.view_toggle when clicked
        self.show_charge_value_button = tk.Checkbutton(self.view_settings_frame, text="Show Charge Value", variable= self.view_setting_buffer[2], command=self.view_toggle)
        self.show_charge_value_button.pack(fill=tk.X)
        #Create a toggle button to show/hide the Field line, call self.view_toggle when clicked
        self.show_field_line_button = tk.Checkbutton(self.view_settings_frame, text="Show Field Line",  variable= self.view_setting_buffer[3], command=self.view_toggle)
        self.show_field_line_button.pack(fill=tk.X)
        #Create a button to update the plot, put it in the view_settings_frame
        self.update_plot_button = tk.Button(self.view_settings_frame, text="Update Plot", command=self.refresh_plot)
        self.update_plot_button.pack()
        

        #Create a Charges button to open the charge setting window
        self.charges_button = tk.Button(self.control_panel, text="Charges", command=self.open_charge_setting_window)
        self.charges_button.pack(fill=tk.X)



        #Create a canvas to draw the plot
        self.fig = plt.figure(figsize=(5.5, 5.5),facecolor="w")
        self.ax = self.fig.add_subplot(111)
        self.ax.set_aspect("equal", adjustable="box")
        
        self.canvas = FigureCanvasTkAgg(self.fig, self.plot_panel)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas.draw()
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_panel,)
        self.toolbar.update()
        pass
    
    




    def view_toggle(self):
        print(self.view_setting_buffer)
        #get the value of the toggle button, if it is 1, then show the corresponding plot, if it is 0, then hide the corresponding plot
        
        settings.show_potential_line = self.view_setting_buffer[0].get() == 1
        settings.show_electric_field = self.view_setting_buffer[1].get() == 1
        settings.show_charge_value = self.view_setting_buffer[2].get() == 1
        settings.show_field_line = self.view_setting_buffer[3].get() == 1
        pass
    def open_charge_setting_window(self):
        charge_window = EditChargeWindow(self,self.EF)
    def new(self):
        pass
    def open(self):
        pass
    def save(self):
        pass
    def export(self):
        pass
    def about(self):
        pass
    


if __name__ == "__main__":
    window = MainWindow()
    window.mainloop()
    pass