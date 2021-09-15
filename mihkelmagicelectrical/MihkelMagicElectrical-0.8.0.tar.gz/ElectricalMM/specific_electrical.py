import numpy as np
import pandas as pd
import xlwt
from xlwt import Workbook, easyxf
from general_functions import *

def calculate_values(data, calculation_indeces, inx):

	ESR_10ms=np.array([])
	ESR_1s=np.array([])
	ESR_5s=np.array([])
	capacitance=np.array([])
	RTE=np.array([])

	for step in calculation_indeces:
		
		last_resistance_step=last_step(data, step, inx)
		last_discharge_step=step-1
		resistance_step_1s=X_seconds_resistance_step(data,step, 1.0, inx)
		resistance_step_5s=X_seconds_resistance_step(data,step, 5.0, inx)

		#Calculation explained in the standard work instruction. 

		ESR_10ms=np.append(ESR_10ms,calculate_ESR_10ms(data, step, inx["Internal_Resistance(Ohm)"]))
		
		ESR_1s=np.append(ESR_1s, (data[last_discharge_step,inx["Voltage(V)"]]-data[resistance_step_1s,inx["Voltage(V)"]])/average_current(data,step,inx["Current(A)"])*1000) 
		
		ESR_5s=np.append(ESR_5s, (data[last_discharge_step,inx["Voltage(V)"]]-data[resistance_step_5s,inx["Voltage(V)"]])/average_current(data,step,inx["Current(A)"])*1000) 
		
		capacitance=np.append(capacitance, data[last_resistance_step,inx["Discharge_Capacity(Ah)"]]*3600/1.425) #voltage_difference(data,step-1))
		
		RTE=np.append(RTE, data[last_resistance_step,inx["Discharge_Energy(Wh)"]]/data[last_resistance_step,inx["Charge_Energy(Wh)"]]) 
				
	return np.array([ESR_10ms, ESR_1s, ESR_5s, capacitance, RTE])


def create_results_worksheet():

	wb = Workbook()
	sheet = wb.add_sheet('Results')
	[sheet.col(i).width==int(16*260) for i in range(10)]

	sheet.write(0, 3, '10ms ESR ', style=easyxf('font: bold True;'))
	sheet.write(0, 4, '1s ESR ', style=easyxf('font: bold True;'))
	sheet.write(0, 5, '5s ESR ', style=easyxf('font: bold True;'))
	sheet.write(0, 6, 'Capacitance', style=easyxf('font: bold True;'))
	sheet.write(0, 7, 'RTE', style=easyxf('font: bold True;'))

	return wb, sheet

def write_results(sheet, results, groups, group_size, data, calculation_indeces, excel_file, excel_file_path, inx):

	#Data is divided into groups of size group_size corresponding to different measurement currents. 
	new_groups=groups+int(np.shape(results)[1]/group_size)
	local_group_inx=0
	gap=group_size+4

	for g in range(groups,new_groups):

		sheet.write((0 + gap*g), 0, 'File Name', style=easyxf('font: bold True;')) 
		sheet.write((1 + gap*g), 0, excel_file)

		sheet.write((2 + gap*g), 0, 'Current(A)', style=easyxf('font: bold True;')) 
		#Take the value of the current 2 seconds before the first resistance step in the group. Round down and take absolute value of the value.
		group_current=data[(calculation_indeces[local_group_inx*group_size]-2),inx["Current(A)"]]
		sheet.write((3 + gap*g), 0, np.abs(np.round(group_current, 3)))

		sheet.write((4 + gap*g), 0, 'Date_Time', style=easyxf('font: bold True;')) 
		date_time_value=str((pd.read_excel(excel_file_path, sheet_name=0)).iloc[3,1])
		sheet.write((5 + gap*g), 0, date_time_value)

		sheet.write((7 + gap*g), 0, 'Average:', style=easyxf('font: bold True;'))
		
		for row in range(np.shape(results)[0]):

			row_values=results[row][local_group_inx*group_size:(local_group_inx+1)*group_size]

			for i, val in enumerate(row_values):
				sheet.write((i+1+gap*g), (row+3), val)
		
			sheet.write((i+3+gap*g), (row+3), np.mean(row_values[-3:]), style=easyxf('font: bold True;'))
		
		local_group_inx+=1


	return new_groups