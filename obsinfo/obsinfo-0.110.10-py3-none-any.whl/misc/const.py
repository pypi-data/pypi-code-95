"""
Exit values as constants as per UNIX BSD standard

"""

# Succesful treatment 
EXIT_SUCCESS = 0
# File could not be processed, generic reasons 
EXIT_FAILURE = 1

# Reference: https://www.freebsd.org/cgi/man.cgi?query=sysexits&manpath=FreeBSD+4.3-RELEASE

# bad CLI parameters 
EXIT_USAGE = 64
#bad file content (input file : Network metadata file) 
EXIT_DATAERR = 65
# file not found (input file : Network metadata file) 
EXIT_NOINPUT = 66 
#A service is unavailable (This can occur if a support program or file does not exist) 
EXIT_UNAVAILABLE = 69 

# (technical/internal error)
# An internal software error has been detected 
EXIT_SOFTWARE = 70

#can't create file (report file, output file)
EXIT_CANTCREAT = 73 
#An error occurred while doing I/O on some file */
EXIT_IOERR = 74 

#Something was found in an unconfigured or misconfigured state */
EXIT_CONFIG = 78 
