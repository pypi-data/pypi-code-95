import numpy as np
from tkinter import *
from tkinter import filedialog, messagebox, ttk
import os
import shutil
import pandas as pd
import sys
import glob



def create_progress_bar():

	root_window=Tk()
	root_window.title("MIHKEL_MAGIC PROGRESS BAR")
	root_window.geometry("500x140")
	progress_bar=ttk.Progressbar(root_window, orient=HORIZONTAL, length=300, mode = 'determinate')
	progress_bar.pack(pady=15)
	progress_bar['value']=1

	textBox=Text(root_window, height=1, width=4)
	textBox.config(font=('Helvatical bold' , 20))
	textBox.tag_configure("Tag_name",justify='center')
	textBox.pack(pady=15)
	textBox.insert(END, '1%')

	root_window.update()

	return root_window, progress_bar, textBox



def update_progress_bar(current_value, total_value, progress_bar, root_window, textBox):

	progress_value=int(current_value/total_value*99)
	progress_bar['value']=progress_value
	textBox.delete('1.0',END)
	textBox.insert('1.0', str(progress_value)+'%')
	root_window.update()



def remove_subdirectories(selected_folder):

	#If excel files are stored in subdirectories, they are moved out and empty subdirectories are deleted. 

	if number_of_directories>0:

		for subfolder in os.listdir(selected_folder):
			subfolder_path=os.path.join(selected_folder,subfolder)

			for data_name in os.listdir(subfolder_path):
				old_location= os.path.join(subfolder_path, data_name)
				#Most common problem is that excel file path is too long and cannot be moved. Need to test for that. 
				#test_path_length(old_location)
				new_location= os.path.join(selected_folder, data_name)
				shutil.move(old_location,new_location)
				os.rmdir(subfolder_path)



def import_data(excel_file_path, inx): 

	column_name_list=inx.keys()
	sheet_index=1

	#[column_name_list] makes the columns be ordered according to the list.
	relevant_data = pd.read_excel(excel_file_path, sheet_name=sheet_index, usecols=column_name_list)[column_name_list].to_numpy()

	#If data contains more than 65000 datapoints, it is continued to be written on a following sheet. 
	while np.shape(relevant_data)[0] % 65000 == 0:
		sheet_index+=1
		additional_data=pd.read_excel(excel_file_path, sheet_name=sheet_index, usecols=column_name_list)[column_name_list].to_numpy()
		relevant_data = np.concatenate((relevant_data,additional_data))
	
	return relevant_data



def get_resistance_indeces(data, group_size, inx):

	#Returns incdeces for the steps where ESR measurements take place.
	#Filtering for indeces is chosen to avoid cycling through the data using for-loops.
	
	#Filter1 = Step Index needs to change. 
	filter1= data[1:,inx["Step_Index"]] != data[:-1,inx["Step_Index"]]
	#Filter2 = Cycle index should not change to avoid counting any loop steps. 
	filter2= data[1:,inx["Cycle_Index"]] == data[:-1,inx["Cycle_Index"]]
	filtered_indeces=np.where(filter1*filter2)[0]
	#Filter3 = Current becomes at least 10 times smaller. There will always be some leak current. 
	#Currents being compared are shifted by 2 since sometimes the first resistance step contains Current(A) value of the last discharge step. 
	#+1 added to reach the first resistance step index. 
	calculation_indeces=np.array([step+1 for step in filtered_indeces if ((np.abs(data[step,inx["Current(A)"]]) > 10*np.abs(data[step+2,inx["Current(A)"]])))])

	#Each measurement gives group_size suitable resistance points. If not divisible by group_size then something went wrong. 
	if len(calculation_indeces) % group_size == 0:
		return calculation_indeces
	else:
		messagebox.showerror("Error 5", "The program was stopped!\n" " \n" "There should always be a multiple of the group size of resistance steps. However, more or less were found. Check the following file: " + str(excel_file) )
		return sys.exit()





def calculate_ESR_10ms(data, step, internal_resistance_inx):

	"""
	Function accounts for the various forms ESR10ms might appear in the data file. The abnormalities that are overcome are:
	1) Value can be found in a range from step+2 to step+7.
	2) If a tested value is 0 or NaN, another value is tested. 
	3) Often, the first ESR values found at step are either 0 or wrong. That is why values are checked in reverse order. 
	4) Average of all values is not taken deliberately as the range can contain inaccurate values. Average is not substantially different from just taking one value. 

	"""
	increased_step_size=step+7
	ESR_10ms_value=float("NaN")
	
	while np.isnan(ESR_10ms_value) or ESR_10ms_value==0:
		ESR_10ms_value=data[increased_step_size,internal_resistance_inx]*1000
		increased_step_size-=1
		if increased_step_size<(step+2):
			messagebox.showerror("Error 3", "The program was stopped!\n" " \n" "Could not find a suitable ESR_10ms value. The search range did not contain any resistance values or they were all 0. Check the following file: " + str(excel_file) )
			return sys.exit()

	return ESR_10ms_value


def average_current(data, step, current_inx):

	#Required to check if there are 4 discharge steps available and takes their average. Available when current is negative. 
	#If less than 4 steps, takes the last value.

	if (data[step-1:step-5:-1,current_inx] < 0).all():
		return np.mean(data[step-1:step-5:-1,current_inx])

	elif (data[step-1,current_inx] < 0).all():
		return data[step-1,current_inx]

	else:
		messagebox.showerror("Error 4", "The program was stopped!\n" " \n" "Could not find a suitable value for current while calculating ESR. Check the following file: " + str(excel_file) )
		return sys.exit()


def voltage_difference(data,starting_step, inx):
	#Finds the index for the last charging step where step index changes and current becomes positive.

	step=starting_step 
	while data[step,inx["Step_Index"]]==data[starting_step,inx["Step_Index"]] or data[step,inx["Current(A)"]] < 0:
		step-=1

	return data[step,inx["Voltage(V)"]]-data[starting_step,inx["Voltage(V)"]]

def last_step(data,starting_step, inx):
	#Finds the index for the last resistance step.

	step=starting_step 
	while data[step,inx["Step_Index"]]==data[starting_step,inx["Step_Index"]]:
		step+=1
	return step-1

def X_seconds_resistance_step(data,starting_step, seconds, inx):

	step=starting_step 
	while data[step,inx["Step_Time(s)"]] < seconds and data[step,inx["Step_Index"]]==data[starting_step,inx["Step_Index"]] and data[step,inx["Cycle_Index"]]==data[starting_step,inx["Cycle_Index"]]:
		step+=1

	return step









def test_path_length(selected_path):
	
	#If path is over 259 character then returns an error as such files cannot be modified (for some reason).

	max_characters=259
	if len(selected_path)>max_characters:
		messagebox.showerror("Error 37", "The program was stopped!\n" " \n" "The selected folder results in file paths that exeeds 259 characters. Move the folder to shorten its path and try again.\n")
		sys.exit()


def test_folder_contents(selected_folder):
	
	#This script only works on a folder filled with xlsx files OR subfolders that each contains an xlsx file. Mixing files and directories is not allowed. 

	folder_contents=glob.glob(str(selected_folder)+"/*")
	global number_of_directories
	global number_of_xlsx_files
	number_of_directories=number_of_xlsx_files=0

	for contents in folder_contents:
		if os.path.isdir(contents):
			number_of_directories+=1
		elif contents.endswith(".xlsx"):
			number_of_xlsx_files+=1
		elif contents.endswith(".xls"):
			number_of_xlsx_files+=1

	if len(folder_contents)==number_of_xlsx_files:
		return
	elif len(folder_contents)==number_of_directories:
		return
	else:
		messagebox.showerror("Error 2", "The program was stopped!\n" " \n" "The selected folder contains a mixture of files and directories which is not the correct format (.xlsx). \n")
		return sys.exit()
