import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
import electric_field as ef
import numpy as np
from matplotlib import cm
import time
from scipy.integrate import ode as ode
from itertools import product
from tkinter import ttk
#import file dialog
from tkinter import filedialog
from sub_ui import EntryPopup, EditChargeWindow
from tkinter import messagebox
#Webbrowser
import webbrowser
import json
import os
#The path to .exe file when using pyinstaller, not the temp folder
import sys


if getattr(sys, 'frozen', False):
    basedir = os.path.dirname(sys.executable)
elif __file__:
    basedir = os.path.dirname(__file__)
print(basedir)
LANG = 0
new_lang = 0
ver = "1.2-alpha"
#Create a class, act as main window, inherit from tk.Tk this windows can resize and the element
#inside will resize too.

'''
The main windows have 2 part, the left is the control panel, the right is the plot panel.

'''
#electric_field_cmap= ["RdBu_r",cm.jet,] 
try:
    from ctypes import windll  # Only exists on Windows.

    myappid = "dtungpka.EFLIS." + ver  # arbitrary string
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

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
    #Dropdown menu values
    field_cmap = "RdBu_r"
    field_line_color = "k"

    #Perfermance settings
    border_limit_percent = 5
    potential_line_density = 10
    electric_field_density = 200
    field_line_count = 5
    field_line_arrow_density = 0.5
    potential_density = 100

    #Plot parameters
    electric_field_brightness = 4
    charge_size = 20
    default_plot_scale = .8
    field_lines_scale = 0.01
    electric_potential_line_thickness = .5
    field_line_thickness = .5

    #View settings
    show_charge_value = False
    show_field_line = True
    show_potential_line = True
    show_electric_field = True
    show_grid = True

        
def settings_to_json():
    settings_dict = {key:value for key,value in settings.__dict__.items() if not key.startswith("__") and not callable(key)}
    return settings_dict
def json_to_settings(json_dict):
    for key,value in json_dict.items():
        if key in settings.__dict__:
            setattr(settings,key,value)
    return settings.__dict__

    
class SettingsWindow(tk.Toplevel):
    def __init__(self, master=None) -> None:
        super().__init__(master=master)
        self.title("Settings")
        #icon
        self.iconbitmap(os.path.join(basedir,"data","icon.ico"))
        self.geometry("1000x800")
        self.resizable(False, False)
        self.create_widgets()
        pass
    def create_widgets(self):
        #The settings window have 2 part, the upper is the Visual settings,lower is  Perfermance settings.
        #The Visual settings have 2 part, the left is the color settings, the right is the Plot parameters.
        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True)
        
        # Create the Visual settings tab
        visual_tab = ttk.Frame(notebook)
        notebook.add(visual_tab, text='Visual')
        
        # Add widgets to the Visual settings tab
        #visual_label = ttk.Label(visual_tab, text='Visual settings')
        #visual_label.pack(pady=10)
        
        # Create the Performance settings tab
        performance_tab = ttk.Frame(notebook)
        notebook.add(performance_tab, text='Performance')

        other_tab = ttk.Frame(notebook)
        notebook.add(other_tab, text='Other')
        
        # Add widgets to the Performance settings tab
        #performance_label = ttk.Label(performance_tab, text='Performance settings')
        #performance_label.pack(pady=10)
        #The Visual settings is a frame with label "Visual settings"
        self.visual_settings_frame = ttk.LabelFrame(visual_tab, text="Visual settings")
        self.visual_settings_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        #The Peromfermance settings is a frame with label "Performance settings"
        self.performance_settings_frame = ttk.LabelFrame(performance_tab, text="Performance settings")
        self.performance_settings_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)


        self.other_settings_frame = ttk.LabelFrame(other_tab, text="Other settings")
        self.other_settings_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        #The color settings is a frame with label "Color settings" inside the Visual settings frame
        self.color_settings_frame = ttk.LabelFrame(self.visual_settings_frame, text="Color settings")
        #Pack the color settings frame to the left
        self.color_settings_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        #The plot parameters is a frame with label "Plot parameters" inside the Visual settings frame
        self.plot_parameters_frame = ttk.LabelFrame(self.visual_settings_frame, text="Plot parameters")
        #Pack the plot parameters frame to the right
        self.plot_parameters_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        #Add 2 dropdown menu to the color settings frame
        #The first dropdown menu is for the electric field color
        self.electric_field_color_label = ttk.Label(self.color_settings_frame, text="Electric field color:")
        self.electric_field_color_label.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.electric_field_color_dropdown = ttk.Combobox(self.color_settings_frame, values=list(electric_field_cmap.keys()), state="readonly")
        self.electric_field_color_dropdown.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.electric_field_color_dropdown.current(list(electric_field_cmap.values()).index(settings.field_cmap))
        #The second dropdown menu is for the field line color
        self.field_line_color_label = ttk.Label(self.color_settings_frame, text="Field line color:")
        self.field_line_color_label.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.field_line_color_dropdown = ttk.Combobox(self.color_settings_frame, values=list(field_line_colors.keys()), state="readonly")
        self.field_line_color_dropdown.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.field_line_color_dropdown.current(list(field_line_colors.values()).index(settings.field_line_color))

        #Add sliders to the plot parameters frame, which is total 6 sliders
        #The first slider is for the electric field brightness
        self.electric_field_brightness_label = ttk.Label(self.plot_parameters_frame, text="Electric field brightness:")
        self.electric_field_brightness_label.pack(side=tk.TOP, fill=tk.X, expand=True)
        #Step of the slider is 0.1, from 0.1 to 10
        self.electric_field_brightness_slider = ttk.Scale(self.plot_parameters_frame, from_=0.1, to=10, orient=tk.HORIZONTAL)
        self.electric_field_brightness_slider.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.electric_field_brightness_slider.set(settings.electric_field_brightness)
        #The second slider is for the charge size
        self.charge_size_label = ttk.Label(self.plot_parameters_frame, text="Charge size:")
        self.charge_size_label.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.charge_size_slider = ttk.Scale(self.plot_parameters_frame, from_=1, to=100, orient=tk.HORIZONTAL)
        self.charge_size_slider.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.charge_size_slider.set(settings.charge_size)
        #The third slider is for the default plot scale
        self.default_plot_scale_label = ttk.Label(self.plot_parameters_frame, text="Default plot scale:")
        self.default_plot_scale_label.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.default_plot_scale_slider = ttk.Scale(self.plot_parameters_frame, from_=.2, to=3, orient=tk.HORIZONTAL)
        self.default_plot_scale_slider.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.default_plot_scale_slider.set(settings.default_plot_scale)
        #The fourth slider is for the field line scale
        self.field_line_scale_label = ttk.Label(self.plot_parameters_frame, text="Field line scale:")
        self.field_line_scale_label.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.field_line_scale_slider = ttk.Scale(self.plot_parameters_frame, from_=0.01, to=2, orient=tk.HORIZONTAL)
        self.field_line_scale_slider.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.field_line_scale_slider.set(settings.field_lines_scale)
        #The fifth slider is for the electric_potential_line_thickness
        self.electric_potential_line_thickness_label = ttk.Label(self.plot_parameters_frame, text="Electric potential line thickness:")
        self.electric_potential_line_thickness_label.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.electric_potential_line_thickness_slider = ttk.Scale(self.plot_parameters_frame, from_=0.1, to=10, orient=tk.HORIZONTAL)
        self.electric_potential_line_thickness_slider.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.electric_potential_line_thickness_slider.set(settings.electric_potential_line_thickness)
        #The sixth slider is for the field line thickness
        self.field_line_thickness_label = ttk.Label(self.plot_parameters_frame, text="Field line thickness:")
        self.field_line_thickness_label.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.field_line_thickness_slider = ttk.Scale(self.plot_parameters_frame, from_=0.1, to=10, orient=tk.HORIZONTAL)
        self.field_line_thickness_slider.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.field_line_thickness_slider.set(settings.field_line_thickness)

        #Add sliders to the performence settings frame, which is total 6 sliders
        #The first slider is for the border_limit_percent
        self.border_limit_percent_label = ttk.Label(self.performance_settings_frame, text="Border limit:")
        self.border_limit_percent_label.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.border_limit_percent_slider = ttk.Scale(self.performance_settings_frame, from_=1, to=10, orient=tk.HORIZONTAL)
        self.border_limit_percent_slider.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.border_limit_percent_slider.set(settings.border_limit_percent)
        #The second slider is for the potential_line_density
        self.potential_line_density_label = ttk.Label(self.performance_settings_frame, text="Potential line density:")
        self.potential_line_density_label.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.potential_line_density_slider = ttk.Scale(self.performance_settings_frame, from_=1, to=1000, orient=tk.HORIZONTAL)
        self.potential_line_density_slider.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.potential_line_density_slider.set(settings.potential_line_density)
        #The third slider is for the potential_density
        self.potential_density_label = ttk.Label(self.performance_settings_frame, text="Potential density:")
        self.potential_density_label.pack(side=tk.TOP, fill=tk.X, expand=True)  
        self.potential_density_slider = ttk.Scale(self.performance_settings_frame, from_=1, to=600, orient=tk.HORIZONTAL)
        self.potential_density_slider.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.potential_density_slider.set(settings.potential_density)
        #The fourth slider is for the electric_field_density
        self.electric_field_density_label = ttk.Label(self.performance_settings_frame, text="Electric field density:")
        self.electric_field_density_label.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.electric_field_density_slider = ttk.Scale(self.performance_settings_frame, from_=1, to=1000, orient=tk.HORIZONTAL)
        self.electric_field_density_slider.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.electric_field_density_slider.set(settings.electric_field_density)
        #The fifth slider is for the field_line_count
        self.field_line_count_label = ttk.Label(self.performance_settings_frame, text="Number of field lines:")
        self.field_line_count_label.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.field_line_count_slider = ttk.Scale(self.performance_settings_frame, from_=1, to=10, orient=tk.HORIZONTAL)
        self.field_line_count_slider.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.field_line_count_slider.set(settings.field_line_count)
        #The sixth slider is for the field_line_arrow_density
        self.field_line_arrow_density_label = ttk.Label(self.performance_settings_frame, text="Field line arrow density:")
        self.field_line_arrow_density_label.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.field_line_arrow_density_slider = ttk.Scale(self.performance_settings_frame, from_=0.01, to=0.99, orient=tk.HORIZONTAL)
        self.field_line_arrow_density_slider.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.field_line_arrow_density_slider.set(settings.field_line_arrow_density)
         

        #Add a entry Epson for the Epson value in other settings frame
        self.epson_label = ttk.Label(self.other_settings_frame, text="Permittivity of free space:")
        self.epson_label.pack(side=tk.TOP, fill=tk.X)
        self.epson_entry = ttk.Entry(self.other_settings_frame)
        self.epson_entry.pack(side=tk.TOP, fill=tk.X)
        self.epson_entry.insert(0, self.master.EF.eps0)





        #Add a button to the settings frame, which is for saving the settings, put it at the bottom, alongwith the reset button
        #Create a frame for the save button
        self.save_button_frame = ttk.Frame(self)
        self.save_button_frame.pack(side=tk.BOTTOM, fill=tk.X, expand=False)
        #Create the save button
        self.save_button = ttk.Button(self.save_button_frame, text="Save", command=self.save_settings)
        self.save_button.pack(side=tk.BOTTOM, fill=tk.X, expand=False, padx=5, pady=5)

        #Add a button to the settings frame, which is for resetting the settings, put it at the bottom, alongwith the save button
        #Create a frame for the reset button
        self.reset_button_frame = ttk.Frame(self)
        self.reset_button_frame.pack(side=tk.BOTTOM, fill=tk.X, expand=False)
        #Create the reset button
        self.reset_button = ttk.Button(self.reset_button_frame, text="Reset", command=self.reset_settings)
        self.reset_button.pack(side=tk.BOTTOM, fill=tk.X, expand=False, padx=5, pady=5)




    def save_settings(self):
        #Save the settings to the settings.py file
        settings.border_limit_percent = round(self.border_limit_percent_slider.get(),2)
        settings.potential_line_density = int(self.potential_line_density_slider.get())
        settings.potential_density = int(self.potential_density_slider.get())
        settings.electric_field_density = int(self.electric_field_density_slider.get())
        settings.field_line_count = int(self.field_line_count_slider.get())
        settings.field_line_arrow_density = round(self.field_line_arrow_density_slider.get(),2)
        settings.electric_field_brightness = round(self.electric_field_brightness_slider.get(),2)
        settings.charge_size = round(self.charge_size_slider.get(),2)
        settings.default_plot_scale = round(self.default_plot_scale_slider.get(),2)
        settings.field_lines_scale = round(self.field_line_scale_slider.get(),2)
        settings.electric_potential_line_thickness = round(self.electric_potential_line_thickness_slider.get(),2)
        settings.field_line_thickness = round(self.field_line_thickness_slider.get(),2)

        #Color from dropdown menu
        settings.field_cmap = electric_field_cmap[self.electric_field_color_dropdown.get()]
        settings.field_line_color = field_line_colors[self.field_line_color_dropdown.get()]


        self.master.EF.eps0 = float(self.epson_entry.get())
        self.master.refresh_plot()
        self.close_settings()

    def reset_settings(self):
        #read the settings from the data/default_settings.et file
        try:
            d = json.load(open("data/default_settings.et"))
            json_to_settings(d['Settings'])
            self.master.EF.eps0 = d['eps0']
        except:
            messagebox.showerror("Error", "Unable to load default settings")
        #Update the sliders
        self.electric_field_color_dropdown.current(list(electric_field_cmap.values()).index(settings.field_cmap))
        self.field_line_color_dropdown.current(list(field_line_colors.values()).index(settings.field_line_color))
        self.electric_field_brightness_slider.set(settings.electric_field_brightness)
        self.charge_size_slider.set(settings.charge_size)
        self.default_plot_scale_slider.set(settings.default_plot_scale)
        self.field_line_scale_slider.set(settings.field_lines_scale)
        self.electric_potential_line_thickness_slider.set(settings.electric_potential_line_thickness)
        self.field_line_thickness_slider.set(settings.field_line_thickness)
        self.border_limit_percent_slider.set(settings.border_limit_percent)
        self.potential_line_density_slider.set(settings.potential_line_density)
        self.potential_density_slider.set(settings.potential_density)
        self.electric_field_density_slider.set(settings.electric_field_density)
        self.field_line_count_slider.set(settings.field_line_count)
        self.field_line_arrow_density_slider.set(settings.field_line_arrow_density)
        self.epson_entry.delete(0, tk.END)
        self.epson_entry.insert(0, self.master.EF.eps0) #set the entry to the current value of eps0


            


    def close_settings(self):
        self.master.settings_window = None
        self.destroy()


    
class ProggresBarWindow(tk.Toplevel):
    #This window is for showing the proggres bar when calculating the field lines and electric field
    # The proggres bar is a ttk.Progressbar
    # The proggres bar is in a frame, which is in the window       
    def __init__(self, master=None) -> None:
        super().__init__(master=master)
        self.title("Calculating")
        #icon
        self.iconbitmap(os.path.join(basedir,"data","icon.ico"))
        self.geometry("300x100")
        self.resizable(False, False)
        #position the window at the center of the screen
        self.update_idletasks()
        w = self.winfo_screenwidth()
        h = self.winfo_screenheight()
        size = tuple(int(_) for _ in self.geometry().split('+')[0].split('x'))
        x = w/2 - size[0]/2
        y = h/2 - size[1]/2
        self.geometry("%dx%d+%d+%d" % (size + (x, y)))
        #Create the widgets

        self.create_widgets()
        pass
    def create_widgets(self):
        #A timer label on top
        #A frame for the proggres bar, containing the proggres bar and the label
        #A cancel button

        #Create a frame for the proggres bar
        self.proggres_bar_frame = ttk.Frame(self)
        self.proggres_bar_frame.pack(side=tk.TOP, fill=tk.X, expand=False)
        #Create a time elapsed label
        self.time_elapsed_label = ttk.Label(self, text="Time elapsed: 0s")
        self.time_elapsed_label.pack(side=tk.TOP, fill=tk.X, expand=False)
        #Create the proggres bar
        self.proggres_bar = ttk.Progressbar(self.proggres_bar_frame, orient=tk.HORIZONTAL, length=300, mode='determinate')
        self.proggres_bar.pack(side=tk.TOP, fill=tk.X, expand=False)
        #Create the label
        self.proggres_bar_label = ttk.Label(self.proggres_bar_frame, text="Calculating...")
        self.proggres_bar_label.pack(side=tk.TOP, fill=tk.X, expand=False)
    
        pass
    def set_time_elapsed(self, time_elapsed):
        self.time_elapsed_label.config(text=f"Time elapsed: {time_elapsed}s")
        #update the window
        self.update()
        pass
    def set_proggres(self, proggres):
        self.proggres_bar['value'] = proggres
        self.update()
        pass
    def set_label(self, label):
        self.proggres_bar_label.config(text=label)
        self.update()
        pass
    def close(self):
        self.destroy()
        pass

class MainWindow(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Electric Field Line Interactive Simulator (EFLIS) v" + ver)
        #set icon to icon.ico
        self.iconbitmap(os.path.join(basedir,"data","icon.ico"))
        self.geometry("860x800")
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
        #self.EF.add_charge(2, [0,0])
        #self.EF.add_charge(-2, [2,0])
        self.refresh_plot()
        self.update()
        pass
    def setup_ef(self):
        
        self.set_border()
        self.EF.field_lines(settings.field_lines_scale,self.x_min, self.x_max, self.y_min, self.y_max, settings.field_line_count)
        print(f"Time to calculate field lines: {time.time()-self.t}s")
        self.proggres_bar_window.set_time_elapsed(round(time.time()-self.t,2))
        self.proggres_bar_window.set_proggres(30)
        self.proggres_bar_window.set_label("Calculating electric field...")
        t = time.time()
        self.EF.electric_potential(self.x_min, self.x_max, self.y_min, self.y_max, settings.potential_density, settings.electric_field_brightness)
        print(f"Time to calculate electric field: {time.time()-t}s")
        self.proggres_bar_window.set_time_elapsed(round(time.time()-self.t,2))
        self.proggres_bar_window.set_proggres(60)
        
        #self.fig = plt.figure(figsize=(5.5, 4.5),facecolor="w")
        #self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel('$x$')
        self.ax.set_ylabel('$y$')
        #self.ax.set_aspect('equal','datalim')
        #self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        #self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=1)
        pass
    def update_plot(self):
        self.proggres_bar_window.set_label("Drawing plot...")
        t = time.time()
        #Clear the plot
        self.ax.clear()
        if len(self.EF.charges) == 0:
            return
        
        #if show grid is true, plot the grid
        if settings.show_grid:
            self.ax.grid(True)
        else:
            self.ax.grid(False)
        print(f"Time to clear plot: {time.time()-t}s")

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
        print(f"Time to plot field line: {time.time()-t}s")
        self.proggres_bar_window.set_time_elapsed(round(time.time()-self.t,2))
        self.proggres_bar_window.set_proggres(80)
        self.proggres_bar_window.set_label("Drawing point charges...")


            

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
        print(f"Time to plot point charges: {time.time()-t}s")
        self.proggres_bar_window.set_time_elapsed(round(time.time()-self.t,2))
        self.proggres_bar_window.set_proggres(90)
        self.proggres_bar_window.set_label("Drawing electric potential...")
        
        
        vvs = self.EF.vvs
        xxs = self.EF.xxs
        yys = self.EF.yys
        # plot electric potential
        #vvs[np.where(vvs<=-1)] = -0.999999 # to avoid error
        #vvs[np.where(vvs>=1)] = 0.999999 # to avoid error

        vvs = np.clip(vvs,-0.999999,0.999999)



        print(f"Time before plot electric potential: {time.time()-t}s")
        if settings.show_potential_line:
            self.ax.tricontour(xxs,yys,vvs,settings.potential_line_density,linewidths=settings.electric_potential_line_thickness,colors="0.3")
        if settings.show_electric_field:
            self.ax.tricontourf(xxs,yys,vvs,settings.electric_field_density,cmap= settings.field_cmap)
        #cbar = self.ax.figure.colorbar(self.ax.collections[0])
        #cbar.set_ticks(np.linspace(clim0,clim1,5))
        #cbar.set_label("Electric Potential")
        print(f"Time to plot electric potential: {time.time()-t}s")
        self.proggres_bar_window.set_time_elapsed(round(time.time()-self.t,2))
        self.proggres_bar_window.set_proggres(100)
        self.proggres_bar_window.set_label("Done")
        self.ax.set_xlim(1.75*self.default_x_min, 1.75*self.default_x_max)
        self.ax.set_ylim(self.default_y_min,self.default_y_max)
        print(f"Time to plot: {time.time()-t}s")

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

    def refresh_plot(self,recalculate=True):
        self.proggres_bar_window = ProggresBarWindow(self)
        self.proggres_bar_window.set_time_elapsed(0)
        self.proggres_bar_window.set_proggres(0)
        self.proggres_bar_window.set_label("Calculating field lines...")
        self.t = time.time()
        #clear the plot and redraw it
        self.ax.clear()
        if recalculate:
            self.setup_ef()
        self.update_plot()
        self.canvas.draw()
        self.canvas.flush_events()
        self.proggres_bar_window.close()
        self.proggres_bar_window = None
        pass

    def update_plt_(self):
        self.refresh_plot(recalculate=False)

    def create_widgets(self):
        
        #Create a frame to contain the control panel and the plot panel
        self.frame = tk.Frame(self)
        self.frame.pack(fill=tk.BOTH, expand=True)

        #Create a Menu bar, which contains theL File, View, Help
        self.menu_bar = tk.Menu(self)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        #New, Open, Save,Export, Exit

        self.file_menu.add_command(label="New", command=self.new)
        self.file_menu.add_command(label="Open", command=self.ask_open)
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
        self.update_plot_button = tk.Button(self.view_settings_frame, text="Update Plot", command=self.update_plt_)
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
        print(basedir)
        charge_window = EditChargeWindow(self,self.EF,basedir)
    def new(self):
        #Clear all charges
        self.EF.charges = []
        self.EF.charges_array = np.zeros((0,3))
        #self.setup_plot()
        self.update_plot()
        self.refresh_plot()
        pass
    def ask_open(self):
        file_name = filedialog.askopenfilename(filetypes=[("EFLIS Template", "*.et")])
        if file_name:
            with open(file_name, 'r') as f:
                d = json.load(f)
                self.EF.from_dict(d['Charges'])
                json_to_settings(d['Settings'])
                self.EF.eps0 = d['eps0']
                self.refresh_plot()
    def open(self, file_name):
        if os.path.isfile(file_name):
            with open(file_name, 'r') as f:
                d = json.load(f)
                self.EF.from_dict(d['Charges'])
                json_to_settings(d['Settings'])
                self.EF.eps0 = d['eps0']
                self.refresh_plot()
        else:
            messagebox.showerror("Error", "File not found")
        
    def save(self):
        d = {'Charges':self.EF.get_dict(), 'Settings':settings_to_json(),'eps0':self.EF.eps0}
        file_name = filedialog.asksaveasfilename(defaultextension=".et", filetypes=[("EFLIS Template", "*.et")])
        if file_name:
            with open(file_name, 'w') as f:
                json.dump(d, f)

    def settings(self):
        settings_window = SettingsWindow(self)

    def export(self):
        #export the plot as a png file, choose the file name and location
        file_name = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG file", "*.png")])
        if file_name:
            self.fig.savefig(file_name)
        pass

    def about(self):
        #show the about window
        #This window contains the information of the program
        #Frame on the left contains the logo of the program, frame on the right contains the information of the program and the author
        about_window = tk.Toplevel(self)
        about_window.title("About")
        about_window.geometry("600x280")
        about_window.resizable(False, False)
        about_window.iconbitmap(os.path.join(basedir,"data","icon.ico"))
        about_window_frame = tk.Frame(about_window)
        about_window_frame.pack(fill=tk.BOTH, expand=True)
        about_window_logo_frame = tk.Frame(about_window_frame)
        about_window_logo_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        about_window_info_frame = tk.Frame(about_window_frame)
        about_window_info_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        about_window_logo = tk.PhotoImage(file=os.path.join(basedir,"data","e.png"))

        about_window_logo_label = tk.Label(about_window_logo_frame, image=about_window_logo)
        about_window_logo_label.image = about_window_logo
        about_window_logo_label.pack(fill=tk.BOTH, expand=True)
        about_window_info_label = tk.Label(about_window_info_frame, text="Electric Field Lines Interaction Simulator (EFLIS)\nVersion "+ver+"\nAuthor: Duong Tung \nEmail: 21010294@st.phenikaa-uni.edu.vn\nCoAuthor: Do Duc Anh \nEmail: 21012329@st.phenikaa-uni.edu.vn", justify=tk.LEFT)
        about_window_info_label.pack(fill=tk.BOTH, expand=True)
        #Add a link to github
        about_window_info_label.bind("<Button-1>", lambda e: webbrowser.open_new("https://github.com/dtungpka/EFLIS"))
                                                                                 


    


if __name__ == "__main__":
    #Get sys arguments, example of regedit: python "C:\<whatever>\fooOpener.py" %1
    #sys.argv[0] is the path of the python file
    path = None
    print(sys.argv)
    
    window = MainWindow()
    if len(sys.argv) > 1:
        path = sys.argv[1]
        window.open(path)

    window.mainloop()
    pass