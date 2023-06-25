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
#import file dialog
from tkinter import filedialog
from sub_ui import EntryPopup, EditChargeWindow, SettingsWindow



LANG = 0
new_lang = 0
ver = "0.91"
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
    border_limit_percent = 5
    default_plot_scale = .8
    field_lines_scale = 0.01
    electric_potential_line_thickness = .5
    field_line_thickness = .5
    field_line_count = 5
    field_line_arrow_density = 0.5
    potential_density = 400
    field_cmap = "RdBu_r"
    field_line_color = "k"
    charge_size = 20

    potential_line_density = 10
    electric_field_density = 200

    electric_field_brightness = 4


    show_charge_value = True
    show_field_line = True
    show_potential_line = True
    show_electric_field = True
    show_grid = True

        


    
class SettingsWindow(tk.Toplevel):
    def __init__(self, master=None) -> None:
        super().__init__(master=master)
        self.title("Settings")
        self.geometry("400x300")
        self.resizable(False, False)
        self.create_widgets()
        pass
    def create_widgets(self):
        #The settings window have 2 part, the upper is the Visual settings,lower is  Perfermance settings.
        #The Visual settings have 2 part, the left is the color settings, the right is the view settings.
        pass


class MainWindow(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Electric Field Line Interactive Simulator (EFLIS) v" + ver)
        #set icon to icon.ico
        self.iconbitmap("icon.ico")
        self.geometry("860x600")
        self.resizable(True, True)
        self.view_setting_buffer = [tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar()]
        #set the view settings to the default value
        self.view_setting_buffer[0].set(settings.show_potential_line)
        self.view_setting_buffer[1].set(settings.show_electric_field)
        self.view_setting_buffer[2].set(settings.show_charge_value)
        self.view_setting_buffer[3].set(settings.show_charge_value)
        self.view_setting_buffer[4].set(settings.show_grid)
        self.create_widgets()
        self.EF = ef.Field()
        self.EF.add_charge(2, [0,0])
        self.EF.add_charge(-2, [2,0])
        self.setup_plot()
        self.setup_ef()
        self.update_plot()
        self.update()
        pass
    def setup_ef(self):
        
        ##TODO: Need review
        
        self.set_border()
        self.EF.field_lines(settings.field_lines_scale,self.x_min, self.x_max, self.y_min, self.y_max, settings.field_line_count)
        self.EF.electric_potential(self.x_min, self.x_max, self.y_min, self.y_max, settings.potential_density, settings.electric_field_brightness)
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
        
        #if show grid is true, plot the grid
        if settings.show_grid:
            self.ax.grid(True)
        else:
            self.ax.grid(False)


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
            size = settings.charge_size*np.sqrt(abs(c))
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
        vvs[np.where(vvs<=-1)] = -0.999999 # to avoid error
        vvs[np.where(vvs>=1)] = 0.999999 # to avoid error
        if settings.show_potential_line:
            self.ax.tricontour(xxs,yys,vvs,settings.potential_line_density,linewidths=settings.electric_potential_line_thickness,colors="0.3")
        if settings.show_electric_field:
            self.ax.tricontourf(xxs,yys,vvs,settings.electric_field_density,cmap= settings.field_cmap) #TODO:cm.jet
        #cbar = self.ax.figure.colorbar(self.ax.collections[0])
        #cbar.set_ticks(np.linspace(clim0,clim1,5))
        #cbar.set_label("Electric Potential")
        self.ax.set_xlim(1.75*self.default_x_min, 1.75*self.default_x_max)
        self.ax.set_ylim(self.default_y_min,self.default_y_max)
   
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
        self.view_menu.add_checkbutton(label="Show Grid", onvalue=1, offvalue=0, variable=self.view_setting_buffer[4], command=self.view_toggle)
        self.menu_bar.add_cascade(label="View", menu=self.view_menu)

        #Settings
        self.settings_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.settings_menu.add_command(label="Settings", command=self.settings)
        self.menu_bar.add_cascade(label="Settings", menu=self.settings_menu)



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
        #Create a toggle button to show/hide the grid, call self.view_toggle when clicked
        self.show_grid_button = tk.Checkbutton(self.view_settings_frame, text="Show Grid", variable= self.view_setting_buffer[4], command=self.view_toggle)
        self.show_grid_button.pack(fill=tk.X)
        #Create a button to update the plot, put it in the view_settings_frame
        self.update_plot_button = tk.Button(self.view_settings_frame, text="Update Plot", command=self.refresh_plot)
        self.update_plot_button.pack()
        
        #Padding it with a separator
        self.separator = ttk.Separator(self.control_panel, orient="horizontal")
        self.separator.pack(fill=tk.X, pady=20, padx=5)
        
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
        settings.show_grid = self.view_setting_buffer[4].get() == 1
        pass
    def open_charge_setting_window(self):
        charge_window = EditChargeWindow(self,self.EF)
    def new(self):
        pass
    def open(self):
        pass
    def save(self):
        pass
    def settings(self):
        pass
    def export(self):
        #export the plot as a png file, choose the file name and location
        file_name = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG file", "*.png")])
        if file_name:
            self.fig.savefig(file_name)
        pass

    def about(self):
        pass
    


if __name__ == "__main__":
    window = MainWindow()
    window.mainloop()
    pass