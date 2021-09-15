


#ma = ma_calc(self.Kp_GCC,self.ua,self.xa)
			#mb = mb_calc(self.Kp_GCC,self.ub,self.xb)
			#mc = mc_calc(self.Kp_GCC,self.uc,self.xc)



#self.vta = vta_calc(ma,self.Vdc)
			#self.vtb = vtb_calc(mb,self.Vdc)
			#self.vtc = vtc_calc(mc,self.Vdc)
#self.Vtrms = Vtrms_calc(self.vta,self.vtb,self.vtc)
			#self.Vrms = Vrms_calc(self.va,self.vb,self.vc)
			#self.Vrms_min = Vrms_min_calc(self.va,self.vb,self.vc)
			#self.Irms = Irms_calc(self.ia,self.ib,self.ic)

#self.Vtabrms = Vtabrms_calc(self.vta,self.vtb)
				#self.Vabrms = Vabrms_calc(self.va,self.vb)
				
#self.S = S_calc(self.vta,self.vtb,self.vtc,self.ia,self.ib,self.ic)
			#self.S_PCC = S_PCC_calc(self.va,self.vb,self.vc,self.ia,self.ib,self.ic)

    #self.iaload1 = self.iphload1_calc(self.va)
				#self.ibload1 = self.iphload1_calc(self.vb)
				#self.icload1 = self.iphload1_calc(self.vc)
				#self.S_G = self.S_G_calc()
				#self.S_load1 = self.S_load1_calc()

#self.ia_ref = self.ia_ref_calc()
			#self.ib_ref = self.ib_ref_calc()
			#self.ic_ref = self.ic_ref_calc()
        
#self.we = self.we_calc() #Calculate inverter frequency from PLL equation

"""
@numba.njit(debug=debug_flag,cache=cache_flag)
def ma_calc(Kp_GCC,ua,xa): #Average duty cycle - Phase A
	#Phase A duty cycle.
	#Returns:
		complex: Duty cycle.
	
	return Kp_GCC*ua + xa #PI controller equation
	#return utility_functions.m_calc(Kp_GCC,ua,xa)

@numba.njit(debug=debug_flag,cache=cache_flag)
def mb_calc(Kp_GCC,ub,xb): #Average duty cycle - Phase B
	#Phase B duty cycle.
	#Returns:
	#	complex: Duty cycle.
	
	return Kp_GCC*ub + xb #PI controller equation

@numba.njit(debug=debug_flag,cache=cache_flag)
def mc_calc(Kp_GCC,uc,xc): #Average duty cycle - Phase C
	#Phase C duty cycle.
	#Returns:
	#	complex: Duty cycle.
	
	return Kp_GCC*uc + xc #PI controller equation	

@numba.njit(debug=debug_flag,cache=cache_flag)
def vta_calc(ma,Vdc):
	#Inverter terminal voltage -  Phase A
	return ma*(Vdc/2)

@numba.njit(debug=debug_flag,cache=cache_flag)
def vtb_calc(mb,Vdc):
	#Inverter terminal voltage -  Phase B
	return mb*(Vdc/2)

@numba.njit(debug=debug_flag,cache=cache_flag)
def vtc_calc(mc,Vdc):
	#Inverter terminal voltage -  Phase C
	return mc*(Vdc/2)

@numba.njit(cache=cache_flag)
def S_calc(vta,vtb,vtc,ia,ib,ic): #Apparent power output at inverter terminal
	#Inverter apparent power output
	return (1/2)*(vta*ia.conjugate() + vtb*ib.conjugate() + vtc*ic.conjugate())
	#return utility_functions_numba.S_calc(vta,vtb,vtc,ia,ib,ic)

#Apparent power output at PCC - LV side
@numba.njit(cache=cache_flag)
def S_PCC_calc(va,vb,vc,ia,ib,ic):
	Power output at PCC LV side
	return (1/2)*(va*ia.conjugate() + vb*ib.conjugate() + vc*ic.conjugate())
	#return utility_functions_numba.S_calc(.va,.vb,.vc,.ia,.ib,.ic)

@numba.njit(cache=cache_flag)
def Vtrms_calc(vta,vtb,vtc):
	#Inverter terminal voltage -	RMS
	return utility_functions_numba.Urms_calc(vta,vtb,vtc)

@numba.njit(cache=cache_flag)
def Vrms_calc(va,vb,vc):
	#PCC LV side voltage - RMS
	return utility_functions_numba.Urms_calc(va,vb,vc)

@numba.njit(cache=cache_flag)
def Vrms_min_calc(va,vb,vc):
	#PCC LV side voltage - RMS
	
	return utility_functions_numba.Urms_min_calc(va,vb,vc)

@numba.njit(cache=cache_flag)		
def Irms_calc(ia,ib,ic):
	#nverter current - RMS
	return utility_functions_numba.Urms_calc(ia,ib,ic)

@numba.njit(cache=cache_flag)
def Vtabrms_calc(vta,vtb):
	#Inverter terminal voltage - line to line	RMS
		
	return abs(vta-vtb)/math.sqrt(2)

@numba.njit(cache=cache_flag)	
def Vabrms_calc(va,vb):
	#PCC LV side voltage - line to line	RMS
	return abs(va-vb)/math.sqrt(2)



	def update_iref_old(self,t):
		#Update reference reference current.
		try:
			#Get current controller setpoint
			
			if self.current_gradient_limiter:				
				if t > self.t_rate_limiter:
					iaR_ref_previous = self.ia_ref.real #self.ia_ref_temp.real #self.ia.real
					iaI_ref_previous = self.ia_ref.imag #self.ia_ref_temp.imag #self.ia.imag
					del_iaR_ref_command = self.ia_ref_calc().real - iaR_ref_previous
					del_iaI_ref_command = self.ia_ref_calc().imag - iaI_ref_previous					
					
					if del_iaR_ref_command > 0:
						del_iaR_ref_actual = math.copysign(min(abs(del_iaR_ref_command)/(t-self.t_rate_limiter),self.iR_ramp_up_max_gradient)*(t-self.t_rate_limiter), del_iaR_ref_command)
					else:
						del_iaR_ref_actual = math.copysign(min(abs(del_iaR_ref_command)/(t-self.t_rate_limiter),self.iR_ramp_up_max_gradient)*(t-self.t_rate_limiter), del_iaR_ref_command)#del_iaR_ref_command
					iaR_ref = iaR_ref_previous + del_iaR_ref_actual
					if abs(del_iaR_ref_actual) > 0.0001:
						print("Real current setpoint changed from {:.4f} to {:.4f} ({:.4f}) with rate:{:.4f} with dt = {:.4f} s".format(iaR_ref_previous,iaR_ref,self.ia.real,del_iaR_ref_actual/(t-self.t_rate_limiter),t -self.t_rate_limiter))
					
					if del_iaI_ref_command > 0:
						del_iaI_ref_actual = math.copysign(min(abs(del_iaI_ref_command)/(t-self.t_rate_limiter),self.iI_ramp_up_max_gradient)*(t-self.t_rate_limiter), del_iaI_ref_command)
					else:
						del_iaI_ref_actual = math.copysign(min(abs(del_iaI_ref_command)/(t-self.t_rate_limiter),self.iI_ramp_up_max_gradient)*(t-self.t_rate_limiter), del_iaI_ref_command) #del_iaI_ref_command 
					iaI_ref = iaI_ref_previous + del_iaI_ref_actual
					if abs(del_iaI_ref_actual) > 0.0001:
						print("Imag current setpoint changed from {:.4f} to {:.4f} ({:.4f}) with rate:{:.4f} with dt = {:.4f} s".format(iaI_ref_previous,iaI_ref,self.ia.real,del_iaI_ref_actual/(t-self.t_rate_limiter),t -self.t_rate_limiter))
						
					self.ia_ref = iaR_ref + 1j*iaI_ref					
					
				elif t < self.t_rate_limiter:					
					iaR_ref_previous = self.ia.real
					iaI_ref_previous = self.ia.imag
					del_iaR_ref_command = self.ia_ref_calc().real - iaR_ref_previous
					del_iaI_ref_command = self.ia_ref_calc().imag - iaI_ref_previous					
					
					if del_iaR_ref_command > 0:
						del_iaR_ref_actual = math.copysign(min(abs(del_iaR_ref_command)/(self.t_rate_limiter-t),self.iR_ramp_up_max_gradient)*(self.t_rate_limiter-t), del_iaR_ref_command)
					else:
						del_iaR_ref_actual = math.copysign(min(abs(del_iaR_ref_command)/(self.t_rate_limiter-t),self.iR_ramp_up_max_gradient)*(self.t_rate_limiter-t), del_iaR_ref_command) #del_iaR_ref_command
					iaR_ref = self.ia.real + del_iaR_ref_actual
					if abs(del_iaR_ref_actual) > 0.0001:
						print("Back in time:Real current setpoint changed from {:.4f} to {:.4f} ({:.4f}) with dt = {:.4f} s".format(iaR_ref_previous,iaR_ref,self.ia.real,t -self.t_rate_limiter))
					
					if del_iaI_ref_command > 0:
						del_iaI_ref_actual = math.copysign(min(abs(del_iaI_ref_command)/(self.t_rate_limiter-t),self.iI_ramp_up_max_gradient)*(self.t_rate_limiter-t), del_iaI_ref_command)
					else:
						del_iaI_ref_actual = math.copysign(min(abs(del_iaI_ref_command)/(self.t_rate_limiter-t),self.iI_ramp_up_max_gradient)*(self.t_rate_limiter-t), del_iaI_ref_command) #del_iaI_ref_command
					iaI_ref = self.ia.imag + del_iaI_ref_actual
					if abs(del_iaI_ref_actual) > 0.0001:
						print("Back in time:Imag current setpoint changed from {:.4f} to {:.4f} ({:.4f}) with dt = {:.4f} s".format(iaI_ref_previous,iaI_ref,self.ia.imag,t -self.t_rate_limiter))
						
					self.ia_ref = iaR_ref + 1j*iaI_ref			
					#self.ia_ref = self.ia_ref_calc()
					#print("Setpoint changed to:{} since dt = {}".format(self.ia_ref,t - self.t_rate_limiter))
				#self.t_rate_limiter = t
				#self.ia_ref_temp = self.ia_ref
			
			else:
				if t > self.t_rate_limiter:
					print("Real current setpoint changed with rate:{:.4f} at t:{:.6f}".format((self.ia_ref_calc().real - self.ia_ref.real)/(t-self.t_rate_limiter),t))
				self.ia_ref = self.ia_ref_calc()
				#print("Current setpoint changed to:{num1.real:+0.03f} {num1.imag:=+8.03f}j from {num2.real:+0.03f} {num2.imag:=+8.03f}j".format(num1=self.ia_ref,num2=self.ia_ref_temp))				
			self.t_rate_limiter = t			
			self.ib_ref = self.ib_ref_calc()
			self.ic_ref = self.ic_ref_calc()
		except:
			LogUtil.exception_handler()
"""