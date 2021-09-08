
#####################################################################
#
# ESPREM Client 
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

import os
import re
import io
import json
import atexit
#from pathlib import Path

#####################################################################

from . import s_log , s_config , s_net , s_cache , s_misc 

####################################################################

s_log.write_msg( "    ####    ####    ####    ####" )

####################################################################

if( "NOM_SERVER_CONFIGURATION" in os.environ ) :
    s_log.write_msg( "Found NOM_SERVER_CONFIGURATION" )
    s_config.init_fromfile( os.environ[ "NOM_SERVER_CONFIGURATION" ] , "sparc_esprem" )
    
####################################################################

def log_msg( msg ) :
    s_log.write_msg( msg )

def version( ) :
    return( config_get_key( "_version_" ) )

def config_get( ) :
    return( s_config.get_config( ) )

def config_get_key( config_key ) :
    return( s_config.get_key( config_key ) )

def config_set_key( config_key , config_val ) :
    s_config.set_key( config_key , config_val )

def config_init_fromfile( config_path , config_key ) :
    return s_config.init_fromfile( config_path , config_key )

def json_encode( data ) :
    return s_misc.json_encode( data )

def pickle_load( fn ) :
    return s_misc.pickle_load( fn )

def cache_available( request_inputs ) :
    return s_cache.available( request_inputs )

def cache_set( request_inputs , request_response ) :
    s_cache.set( request_inputs , request_response )

def cache_get( request_inputs ) :
    return s_cache.get( request_inputs )

####################################################################

def do_request( request_endpoint , request_params , request_id = 0 , request_timeout_in = 60 ) :

    #if( s_cache.available( [ request_endpoint , request_params ] ) ) :
    #    s_log.write_msg( "CACHE HIT" )
    #    return s_cache.get_data( [ request_endpoint , request_params ] )
    #s_log.write_msg( "CACHE MISS" )
    
    ####################################################################

    #if( s_cache.available( request_params) ) :
    #    log_msg( "CACHE AVAILABLE" )

    request_timeout = int( s_config.get_key( "pyespremclient_timeout" , 600 ) )
    log_msg( "request_timeout=" + str( request_timeout )  )

    ####################################################################

    response = s_net.get_response( request_endpoint , request_params , request_id , request_timeout ) 

    if( "code" in response ) :
        res_str = json.dumps( response , indent = 4 )
        s_log.write_msg( res_str )
        return( response )
        #assert False , "code"

    if( "_error" in response ) :
        res_str = json.dumps( response , indent = 4 )
        s_log.write_msg( res_str )
        return( response )
        #assert False , "_error"

    ####################################################################

    #s_cache.update( request_params , response )

    ####################################################################

    return( response )



