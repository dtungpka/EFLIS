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
        self.array = np.array([self.q,self.pos[0],self.pos[1]])
    def E(self, x, y):
        #base on E_point_charge
        return self.q*(x-self.pos[0])/((x-self.pos[0])**2+(y-self.pos[1])**2)**(1.5), \
            self.q*(y-self.pos[1])/((x-self.pos[0])**2+(y-self.pos[1])**2)**(1.5)
    def V(self, x, y):
        #base on V_point_charge
        return self.q/((x-self.pos[0])**2+(y-self.pos[1])**2)**(0.5)
    
class Field:
    eps0 = 1
    def __init__(self):
        self.charges=[]
        self.min_charges= None
        self.charges_array = np.zeros((0,3))
    def add_charge(self, q, pos):
        self.charges.append(Charge(q, pos))
        if self.min_charges==None or abs(q)<self.min_charges:
            self.min_charges=abs(q)
        self.charges_array = np.append(self.charges_array,[[q,pos[0],pos[1]]],axis=0)
    def delete_charge(self, index):
        self.charges.pop(index)
        self.charges_array = np.delete(self.charges_array,index,axis=0)
    def E(self, x, y):
        # Ex, Ey=0, 0
        # for C in self.charges:
        #     E=C.E(x, y)
        #     Ex=Ex+E[0]
        #     Ey=Ey+E[1]
        # return [ Ex, Ey ]

        Ex = np.sum(self.charges_array[:,0]*(x-self.charges_array[:,1])/((x-self.charges_array[:,1])**2+(y-self.charges_array[:,2])**2)**(1.5),axis=0)
        Ey = np.sum(self.charges_array[:,0]*(y-self.charges_array[:,2])/((x-self.charges_array[:,1])**2+(y-self.charges_array[:,2])**2)**(1.5),axis=0)
        return [ Ex, Ey ]

    

    def V(self, x, y):
        #make x  from m array into shape mxn array with n is the number of charges
        #make y  from m array into shape mxn array with n is the number of charges
        
        X = np.tile(x,(self.charges_array.shape[0],1))
        Y = np.tile(y,(self.charges_array.shape[0],1))

        c = self.charges_array[:,0].reshape(self.charges_array.shape[0],1)
        x_ = self.charges_array[:,1].reshape(self.charges_array.shape[0],1)
        y_ = self.charges_array[:,2].reshape(self.charges_array.shape[0],1)

        V = np.sum(c/((X-x_)**2+(Y-y_)**2)**(0.5),axis=0)
        return V
    def E_dir(self, t, y,charge):
        Ex, Ey=self.E(y[0], y[1])
        n=np.sqrt(Ex**2+Ey*Ey)
        return [Ex/n, Ey/n]
    def get_positons(self):
        #return the last 2 columns of the charges_array, in list
        return self.charges_array[:,1:].tolist()
    def get_dict(self):
        #Return a dictionary containing the charges and their positions
        d = []
        for C in self.charges:
            d.append({'q':C.q,'pos':C.pos})
        return d
    def from_dict(self,d):
        #Load the charges and their positions from a dictionary
        self.charges = []
        for C in d:
            self.add_charge(C['q'],C['pos'])
    def get_min_charges(self):
        self.min_charges= None
        for C in self.charges:
            if self.min_charges==None or abs(C.q)<self.min_charges:
                self.min_charges=abs(C.q)
    def field_lines(self,scale, x_min, x_max, y_min, y_max, num_lines=16):
        R= scale
        self.xs,self.ys = [],[]
        self.start_charge = []
        self.get_min_charges()
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
    def electric_potential(self,x_min,x_max,y_min,y_max,density=300,brightness=1.2):
        numcalcv = density
        # calculate electric potential
        self.vvs = []
        self.xxs = []
        self.yys = []
        #if no charges, return 0
        if len(self.charges)==0:
            return self.xxs,self.yys,self.vvs
        x,y = np.linspace(x_min,x_max,numcalcv),np.linspace(y_min,y_max,numcalcv)
        self.xxs = np.tile(x,(y.shape[0],1)).reshape(-1)
        self.yys = np.tile(y,(x.shape[0],1)).T.reshape(-1)
        
        self.vvs = self.V(self.xxs,self.yys)



        #Normalize the potential
        #self.vvs = self.vvs - np.min(self.vvs)
        self.vvs = self.vvs / np.max(self.vvs) * brightness
        #convert all to list
        self.xxs,self.yys,self.vvs = self.xxs.tolist(),self.yys.tolist(),self.vvs.tolist()

        return self.xxs,self.yys,self.vvs
    

def float_to_metric_prefix(x, unit='C'):
    x = Quantity(x, unit)
    return x
def metric_prefix_to_float(x):
    x = Quantity(x, 'C')
    return x.real



class NetForce:
    def __init__(self,charge,field,epsilon=1):
        self.charge=charge
        self.field=field
        self.epsilon=epsilon
    def get_distance(self,charge1,charge2):
        dis = np.sqrt((charge1.pos[0]-charge2.pos[0])**2+(charge1.pos[1]-charge2.pos[1])**2)
        return  dis
    def get_force(self,charge1,charge2):
        return 9e9*abs(charge1.q*charge2.q)/((self.get_distance(charge1,charge2)**2)*self.epsilon)
    def get_theta(self, charge1, charge2):
        '''
        Return the angle between the line connecting two charges and the x axis in radians.
        If the charges have opposite signs, the angle points towards charge2, otherwise it opposes it.
        '''
        delta_x = charge2.pos[0] - charge1.pos[0]
        delta_y = charge2.pos[1] - charge1.pos[1]
        if delta_x == 0:
            return np.pi / 2 if delta_y > 0 else -np.pi / 2
        theta = np.arctan(delta_y / delta_x)
        if charge1.q * charge2.q < 0:
            theta += np.pi if delta_x < 0 else 0
        else:
            theta += np.pi if delta_x > 0 else 0
        return theta
    def get_force_axis(self,charge1,charge2):
        '''
        return the force in x and y axis
        '''
        theta=self.get_theta(charge1,charge2)
        force=self.get_force(charge1,charge2)
        return force*np.cos(theta),force*np.sin(theta)
    def get_net_force(self):
        '''
        return the net force on the charge
        '''
        net_force_x=0
        net_force_y=0
        charges=self.field.charges
        min_pos = 0
        for charge in charges:
            if min_pos < -abs(charge.pos[0]):
                min_pos = abs(charge.pos[0]) + 1
            if min_pos < -abs(charge.pos[1]):
                min_pos = abs(charge.pos[1]) + 1
        for charge in charges:
            if charge!=self.charge:
                temp_charge_1 = Charge(self.charge.q, [self.charge.pos[0] + min_pos, self.charge.pos[1] + min_pos])
                temp_charge_2 = Charge(charge.q, [charge.pos[0] + min_pos, charge.pos[1] + min_pos])
                force_x,force_y=self.get_force_axis(temp_charge_1,temp_charge_2)
                net_force_x+=force_x
                net_force_y+=force_y
        return net_force_x,net_force_y
    def get_net_force_magnitude(self):
        return np.sqrt(self.get_net_force()[0]**2+self.get_net_force()[1]**2)
    def get_net_force_theta(self):
        nf = self.get_net_force()
        if nf[0]==0:
            return (np.pi/2 if nf[1]>0 else -np.pi/2)
        if nf[1]==0:
            return (0 if nf[0]>0 else np.pi )
        return np.arctan(nf[1]/nf[0])

    


