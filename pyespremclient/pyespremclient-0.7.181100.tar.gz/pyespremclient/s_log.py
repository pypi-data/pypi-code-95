
#####################################################################
#
# ESPREM Client Log
#
# Project   : PYESPREMCLIENT
# Author(s) : Zafar Iqbal < zaf@sparc.gr >
# Copyright : (C) 2021 SPARC PC < https://sparc.space/ >
#
# All rights reserved. No warranty, explicit or implicit, provided.
# SPARC PC is and remains the owner of all titles, rights
# and interests in the Software.
#
#####################################################################

import json

from datetime import datetime

datetime.now( ).strftime("%Y_%m_%d-%I_%M_%S_%p")

#####################################################################

def default_json( t ) :
    return f'{t}'

def write_msg( msg_raw ) :

    msg = msg_raw

    if(msg==None): msg="!NONE!"
    
    if( isinstance( msg , list ) ) :
        msg = ",".join( map( str , msg ) )
    
    if( isinstance( msg , dict ) ) :
        msg = json.dumps( msg , default = default_json )


    if( isinstance( msg , ( int , float , bool ) ) ) :
        msg = str( msg )

    msg = datetime.now( ).strftime( "%Y_%m_%d-%I_%M_%S_%p" ) + " " + msg
    with open( "/tmp/pyespremclient.log" , "a+" , 1 ) as log_file :
        log_file.write( msg + "\n" )


    