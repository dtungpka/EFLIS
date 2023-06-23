import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import ode as ode
from matplotlib import cm
from itertools import product
from quantiphy import Quantity
class Charge:
    def __init__(self, q, pos):
        self.q=q
        self.pos=pos
    def E(self, x, y):
        #base on E_point_charge
        return self.q*(x-self.pos[0])/((x-self.pos[0])**2+(y-self.pos[1])**2)**(1.5), \
            self.q*(y-self.pos[1])/((x-self.pos[0])**2+(y-self.pos[1])**2)**(1.5)
    def V(self, x, y):
        #base on V_point_charge
        return self.q/((x-self.pos[0])**2+(y-self.pos[1])**2)**(0.5)
    
class Field:
    def __init__(self):
        self.charges=[]
        self.min_charges= None
    def add_charge(self, q, pos):
        self.charges.append(Charge(q, pos))
        if self.min_charges==None or abs(q)<self.min_charges:
            self.min_charges=abs(q)
    def delete_charge(self, index):
        self.charges.pop(index)
    def E(self, x, y):
        Ex, Ey=0, 0
        for C in self.charges:
            E=C.E(x, y)
            Ex=Ex+E[0]
            Ey=Ey+E[1]
        return [ Ex, Ey ]
    def V(self, x, y):
        V=0
        for C in self.charges:
            Vp=C.V(x, y)
            V = V+Vp
        return V
    def E_dir(self, t, y,charge):
        Ex, Ey=self.E(y[0], y[1])
        n=np.sqrt(Ex**2+Ey*Ey)
        return [Ex/n, Ey/n]
    def get_positons(self):
        pos=[]
        for C in self.charges:
            pos.append(C.pos)
        return pos
    def field_lines(self,scale, x_min, x_max, y_min, y_max, num_lines=16):
        R= scale
        self.xs,self.ys = [],[]
        self.start_charge = []
        for C in self.charges:
            # plot field lines starting in current charge
            dt=0.8*R
            if C.q<0:
                dt=-dt
            # loop over field lines starting in different directions 
            # around current charge
            lines_per_charge=int(num_lines * abs(C.q)/self.min_charges)
            for alpha in np.linspace(0, 2*np.pi*(lines_per_charge-1)/lines_per_charge , lines_per_charge):
                r=ode(self.E_dir)
                r.set_integrator('vode')
                r.set_f_params(self.charges)
                x=[ C.pos[0] + np.cos(alpha)*R ]
                y=[ C.pos[1] + np.sin(alpha)*R ]

                r.set_initial_value([x[0], y[0]], 0)
                while r.successful():
                    r.integrate(r.t+dt)
                    x.append(r.y[0])
                    y.append(r.y[1])
                    hit_charge=False
                    # check if field line left drwaing area or ends in some charge
                    for C2 in self.charges:
                        if np.sqrt((r.y[0]-C2.pos[0])**2+(r.y[1]-C2.pos[1])**2)<R:
                            hit_charge=True
                    if hit_charge or (not (x_min<r.y[0] and r.y[0]<x_max)) or \
                            (not (y_min<r.y[1] and r.y[1]<y_max)):
                        break
                self.xs.append(x)
                self.ys.append(y)
                self.start_charge.append(C.q)
        return self.xs,self.ys
    def electric_potential(self,x_min,x_max,y_min,y_max):
        # calculate electric potential
        vvs = []
        xxs = []
        yys = []
        numcalcv = 300
        for xx,yy in product(np.linspace(x_min,x_max,numcalcv),np.linspace(y_min,y_max,numcalcv)):
            xxs.append(xx)
            yys.append(yy)
            vvs.append(self.V(xx,yy))
        self.xxs = np.array(xxs)
        self.yys = np.array(yys)
        self.vvs = np.array(vvs)

def float_to_metric_prefix(x, unit='C'):
    x = Quantity(x, unit)
    return x
def metric_prefix_to_float(x):
    x = Quantity(x, 'C')
    return x.real




