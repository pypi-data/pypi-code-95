
################## constants
P3D_FALSE=-1 
P3D_TRUE=1 

P3D_ERROR=0
P3D_MEM_ERROR=None
P3D_SUCCESS=2

BACKGROUND=0
#OBJECT=UCHAR_MAX

CONN4=611
CONN8=612

CONN6=711
CONN18=712
CONN26=713

################## error messages

def py_printErrorMessage(err_code):
  
    string = "Success. \n"
  
    if err_code == 1 or err_code == 0:
        string = "**ERROR** Error on code execution. \n"
        
  	
    if err_code == -2:
        string = "**ERROR**  Input argument IMAGE must be of type BYTE or UINT. \n"
        
  	
    if err_code == -3:
        string = "**ERROR** Input argument IMAGE must be a 2D or 3D matrix. \n"
    
    if err_code == -4:
        string = "**ERROR** Wrong argument values. Please call the help function for more information. \n"
        
   	
    print (string)

#################
  

