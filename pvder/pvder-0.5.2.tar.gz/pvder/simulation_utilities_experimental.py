""" Manage simulation results and ODE solver."""

from __future__ import division
import sys
import six
import time

import numpy as np
import math
import cmath
from scipy.integrate import odeint,ode

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from pvder.utility_classes import Utilities
from pvder import defaults
from pvder.logutil import LogUtil


from diffeqtorch import DiffEq

#ODE specified in Julia as a string, see DifferentialEquations.jl for documentation
lotka_volterra_string =""" 
function f(du,u,p,t)

    du[1] = p[1]*u[1] - p[2]*u[1]*u[2]
    du[2] = p[3]*u[1]*u[2] - p[4]*u[2]
   
end
"""
dummy_julia = DiffEq(lotka_volterra_string, saveat=0.1,debug=False)  #For making diffeqpy work

tic = time.perf_counter()
from diffeqpy import de
toc = time.perf_counter()
print('Time taken to import "diffeqpy":',toc - tic)


class SimulationUtilitiesExperimental():
	# Utility class for dynamic simulations.

	def call_diffeq_solver(self,integrator):
		#Use the Julia DifferentialEquations.jl solver package.
		try:
			#t_t.append(integrator.t+self.del_t)  
            #LogUtil.logger.info(f'Solving for interval:{integrator.t} to {integrator.t+self.tInc}')
			de.step_b(integrator,self.tInc,True)  
			
			LogUtil.logger.debug(f'Final state:{integrator.u}')
			LogUtil.logger.debug(f'Final time:{integrator.t}')
			#u_t = np.array(integrator.sol)#.reshape(-1,self.n_ODE*self.n_pairs)
			
			return integrator.u,integrator.t
		except:
			LogUtil.exception_handler()

	def initialize_diffeq_solver(self,ODE_model_diffeq,y0,solver_type = de.Tsit5(),t0=0.0):
		#Initialize an integrator
		try:
			julia_ode = de.ODEProblem(ODE_model_diffeq, y0, (t0, 1.0),[])              
			julia_integrator = de.init(julia_ode,solver_type,saveat=self.tInc)#
			LogUtil.logger.debug('{}:{} solver initialized.'.format(self.name,'Julia'))
			
			return julia_integrator
		except:
			LogUtil.exception_handler()

	def ODE_model_diffeq1(self,y,p,t):
		 #Combine all derivatives when using ode method
		try:
			#print(len(y))
			y1 = y[0:self.PV_model.n_ODE]
			if self.PV_model.standAlone:
				self.grid_model.steady_state_model(t)
			print('y1:',len(y1))
			dy = self.PV_model.ODE_model(y1,t)
			print(dy,len(dy))
			return dy
		except:
			LogUtil.exception_handler()
