import numpy as np
from tkinter import *
from tkinter import filedialog, messagebox, ttk
import os
import shutil
import pandas as pd
from general_functions import *
from specific_electrical import *



#Dictionary with relevant column names and assigned indeces.
inx={"Step_Index" : 0,
 "Cycle_Index" : 1,
 "Current(A)" : 2,
 "Voltage(V)" : 3,
 "Discharge_Capacity(Ah)" : 4,
 "Internal_Resistance(Ohm)" : 5,
 "Charge_Energy(Wh)" : 6,
 "Discharge_Energy(Wh)" : 7,
 "Step_Time(s)" : 8,
}

#Select folder to analyse
root1 = Tk()
root1.withdraw()
selected_folder=filedialog.askdirectory()

root2,progress_bar, textBox=create_progress_bar()

test_folder_contents(selected_folder)
remove_subdirectories(selected_folder)

excel_file_list=os.listdir(selected_folder)
results_workbook, results_sheet = create_results_worksheet()

#Create global variables needed for saving data for multiple excel files. 
groups=0
group_size=5
global files_processed
files_processed=0

for excel_file in excel_file_list:

	print(excel_file)
	excel_file_path=os.path.join(selected_folder, excel_file)	
	data=import_data(excel_file_path, inx)

	files_processed+=1
	update_progress_bar(files_processed, len(excel_file_list), progress_bar, root2, textBox)

	calculation_indeces = get_resistance_indeces(data, group_size, inx)
	results=calculate_values(data,calculation_indeces, inx)

	groups=write_results(results_sheet, results, groups, group_size, data, calculation_indeces, excel_file, excel_file_path, inx)

#Create excel file, open it and close the interface. 
results_name=(os.path.basename(selected_folder) + '_Results.xls')
results_path=os.path.join(selected_folder, results_name)
results_workbook.save(results_path)
root2.destroy()
os.startfile(results_path)



