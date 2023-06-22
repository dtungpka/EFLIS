import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import electric_field as ef
import numpy as np
from scipy.integrate import ode as ode
from itertools import product

#Create a class, act as main window, inherit from tk.Tk this windows can resize and the element
#inside will resize too.

'''
The main windows have 2 part, the left is the control panel, the right is the plot panel.

'''
class settings:
    border_limit_percent = 0.1
    default_plot_scale = 0.1
    field_lines_scale = 0.01
    electric_potential_line_thickness = .5
    field_line_thickness = .5
    field_line_count = 4
    field_line_arrow_density = 0.5



class MainWindow(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Electric Field")
        self.geometry("800x600")
        self.resizable(True, True)
        self.create_widgets()
        self.EF = ef.Field()
        self.setup_plot()
        self.setup_ef()
        self.update_plot()
        self.update()
        pass
    def setup_ef(self):
        
        ##TODO: Need review
        self.EF.add_charge(1, [0,0])
        self.EF.add_charge(-4, [1,0])
        self.EF.add_charge(1, [0,1])
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
        # plot field line
        for c ,x, y in zip(self.EF.start_charge,self.EF.xs,self.EF.ys):
            #self.ax.plot(x, y, color="k", lw=settings.field_line_thickness)
            #plot with arrow
            #if the charge is positive, the arrow is from begin to end, else the arrow is from end to begin
            if c < 0:
                #reverse the array
                x = x[::-1]
                y = y[::-1]
            self.ax.plot(x, y, color="k", lw=settings.field_line_thickness)
            #plot arrow at the middle of the line

            i = len(x) // 2
            dx = x[i] - x[i-1]
            dy = y[i] - y[i-1]
            self.ax.arrow(x[i], y[i], dx, dy, color="k", lw=settings.field_line_thickness, head_width=2, head_length=1)

                

            

        # plot point charges
        for C in self.EF.charges:
            self.ax.plot(C.pos[0], C.pos[1], 'ro', ms=8*np.sqrt(abs(C.q)))
        vvs = self.EF.vvs
        xxs = self.EF.xxs
        yys = self.EF.yys
        # plot electric potential
        clim0,clim1 = -2,2
        vvs[np.where(vvs<clim0)] = clim0*0.999999 # to avoid error
        vvs[np.where(vvs>clim1)] = clim1*0.999999 # to avoid error
        self.ax.tricontour(xxs,yys,vvs,10,linewidths=settings.electric_potential_line_thickness,colors="0.3")
        self.ax.tricontourf(xxs,yys,vvs,100,cmap="RdBu_r") #TODO:cm.jet
        cbar = self.ax.figure.colorbar(self.ax.collections[0])
        #cbar.set_ticks(np.linspace(clim0,clim1,5))
        cbar.set_label("Electric Potential")
     
    def set_border(self):  
        #Limit the plot area
        self.x_min = -3
        self.x_max = 3
        self.y_min = -3
        self.y_max = 3
        self.default_x_min = -3
        self.default_x_max = 3
        self.default_y_min = -3
        self.default_y_max = 3
        

        #Loop through all the particles to find the border, which is the max and min of x and y,
        #Calculate by example: x_max = x + x * 0.1
        positions = self.EF.get_positons() # [[x1,y1],[x2,y2]...]
        per = settings.border_limit_percent
        for pos in positions:
            if pos[0] > self.x_max:
                self.x_max = pos[0] + pos[0] * per
                self.default_x_max = pos[0] + pos[0] * settings.default_plot_scale
            if pos[0] < self.x_min:
                self.x_min = pos[0] - pos[0] * per
                self.default_x_min = pos[0] - pos[0] * settings.default_plot_scale
            if pos[1] > self.y_max:
                self.y_max = pos[1] + pos[1] * per
                self.default_y_max = pos[1] + pos[1] * settings.default_plot_scale
            if pos[1] < self.y_min:
                self.y_min = pos[1] - pos[1] * per
                self.default_y_min = pos[1] - pos[1] * settings.default_plot_scale
        self.ax.set_xlim(self.default_x_min, self.default_x_max)
        self.ax.set_ylim(self.default_y_min, self.default_y_max)
        pass




    def create_widgets(self):
        #Create a frame to contain the control panel and the plot panel
        self.frame = tk.Frame(self)
        self.frame.pack(fill=tk.BOTH, expand=True)
        #Create a frame to contain the control panel
        self.control_panel = tk.Frame(self.frame)
        self.control_panel.pack(side=tk.LEFT, fill=tk.Y)
        #Create a frame to contain the plot panel
        self.plot_panel = tk.Frame(self.frame)
        self.plot_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        #Create a button to add a charge
        self.add_charge_button = tk.Button(self.control_panel, text="Add Charge", command=self.add_charge)
        self.add_charge_button.pack()
        #Create a button to clear all charge
        self.clear_charge_button = tk.Button(self.control_panel, text="Clear Charge", command=self.clear_charge)
        self.clear_charge_button.pack()
        #Create a button to clear all charge
        self.clear_plot_button = tk.Button(self.control_panel, text="Clear Plot", command=self.clear_plot)
        self.clear_plot_button.pack()
        #Create a button to clear all charge
        self.plot_button = tk.Button(self.control_panel, text="Plot", command=self.plot)
        self.plot_button.pack()
        #Create a button to clear all charge
        self.quit_button = tk.Button(self.control_panel, text="Quit", command=self.quit)
        self.quit_button.pack()
        #Create a canvas to draw the plot
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, self.plot_panel)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas.draw()
        pass
    def add_charge(self):
        pass
    def clear_charge(self):
        pass
    def clear_plot(self):
        pass
    def plot(self):
        pass
    pass

if __name__ == "__main__":
    window = MainWindow()
    window.mainloop()
    pass