import numpy as np
import tkinter as tk
#using matplotlib with tkinker as backend
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class CONSTANTS:
    # Permittivity constant
    EPSILON_0 = 8.8541878128e-12
class Particle:
    #Contain position and charge, color.
    def __init__(self, position, charge, color) -> None:
        self.position = np.array(position)
        self.charge = charge
        self.color = color
        pass
    def E(self,pos):
        '''
        Calculate the electric field at a point from a particle

        Parameters
        ----------
        pos : np.ndarray
            The position of the point (x, y)

        Returns
        -------
        np.ndarray
            The electric field at the point (Ex, Ey)
        
        '''
        # Calculate the electric field at the point from the particle
        toPos = pos - self.position
        k = 1/(4*np.pi*CONSTANTS.EPSILON_0)
        len2 = np.linalg.norm(toPos)**2
        #TODO: Need review
        E = k*self.charge*toPos/(len2 * np.sqrt(len2))
        return E
    def potential(self,pos):
        '''
        Calculate the electric potential at a point from a particle

        Parameters
        ----------
        pos : np.ndarray
            The position of the point (x, y)

        Returns
        -------
        float
            The electric potential at the point
        '''
        # Calculate the electric potential at the point from the particle
        return self.charge/(4*np.pi*CONSTANTS.EPSILON_0*np.linalg.norm(pos-self.position))



class Field:
    def __init__(self) -> None:
        #Setup matrix containing the field, which is a list of particles
        self.particles = []
        pass
    def E(self, pos):
        '''
        Calculate the electric field at a point from the field

        Parameters
        ----------
        pos : np.ndarray
            The position of the point (x, y)

        Returns
        -------
        np.ndarray
            The electric field at the point (Ex, Ey)
        '''
        # Calculate the electric field at the point from the field
        #Loop through all particles in the field, and calculate the field at the point from each one
        #Add all the fields together to get the net field
        result = np.array([0,0])
        for particle in self.particles:
            result += particle.E(pos)
        return result
    def potential(self, pos):
        '''
        Calculate the electric potential at a point from the field

        Parameters
        ----------
        pos : np.ndarray
            The position of the point (x, y)

        Returns
        -------
        float
            The electric potential at the point
        '''
        # Calculate the electric potential at the point from the field
        #Loop through all particles in the field, and calculate the potential at the point from each one
        #Add all the potentials together to get the net potential
        result = 0
        for particle in self.particles:
            result += particle.potential(pos)
        return result

        


class ParticlesPlotter:
    def __init__(self) -> None:
        #make a resizable window, with content proportionally resizing
        self.root = tk.Tk()
        self.root.title("Particles Plotter")
        self.root.geometry("800x600")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        #create a figure and add it to the window
        self.fig = matplotlib.figure.Figure(figsize=(5, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlim(-10, 10)
        self.ax.set_ylim(-10, 10)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")



        #Setup matrix containing the field, which is a list of particles
        self.particles = []




        pass