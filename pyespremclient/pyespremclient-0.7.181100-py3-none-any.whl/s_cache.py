
#####################################################################
#
# ESPREM Client Cache
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
import json
import hashlib
import time

from . import s_log , s_config , s_misc

cache_dirpath = "/tmp/pyespremclient_cache2/"

#####################################################################


def is_enabled( ) :

    if( s_config.get_key( "pyespremclient_cache" ) == "on" ) :
        return True

    return False


def hashtopath( ha ) :
    subdirs=ha[0:4]+"/"+ha[4:8]+"/"
    p = cache_dirpath + subdirs + ha + ".json"
    #s_log.write_msg( p )
    return p


def get( request_inputs ) :

    if( not is_enabled( ) ) : return None

    if( request_inputs == None ) : return { }

    inputs_str = json.dumps( request_inputs )
    cache_hash = hashlib.sha256( inputs_str.encode( "utf-8" ) ).hexdigest( )

    cache_filepath = hashtopath( cache_hash ) 
    #s_log.write_msg( "cache_filepath=" + cache_filepath )
    if( not os.path.isfile( cache_filepath ) ) : return None
    with open( cache_filepath , "r" ) as f :
        return( json.load( f ) )


def available( request_inputs ) :

    if( not is_enabled( ) ) : return False

    inputs_str = json.dumps( request_inputs )
    cache_hash = hashlib.sha256( inputs_str.encode( "utf-8" ) ).hexdigest( )
    cache_filepath = cache_dirpath + cache_hash + ".json"
    s_log.write_msg( "cache_filepath=" + cache_filepath )

    return os.path.isfile( cache_filepath ) 


    #return False

    #request_str = request_list[ 0 ] + json.dumps( request_list[ 1 ] )
    #cache_hash = hashlib.sha256( request_str.encode('utf-8') ).hexdigest( )
    #cache_filepath = cache_dirpath + cache_hash + ".json"
    #s_log.write_msg("cache_filepath="+cache_filepath)

    #return os.path.isfile( cache_filepath ) 

# The response
def set( request_inputs , request_response ) :
    if( not is_enabled( ) ) : return False
    # Create/Recreate cache directory
    inputs_str = json.dumps( request_inputs )
    cache_hash = hashlib.sha256( inputs_str.encode( "utf-8" ) ).hexdigest( )
    cache_filepath = hashtopath( cache_hash ) 
    if( os.path.isfile( cache_filepath ) ) : return None
    init_path( cache_filepath )
    response = request_response.copy( )
    #response[ "_pyesprem_cache_time_" ] = int(time.time())
    with open( cache_filepath , "w" ) as f :
        #f.write( json.dumps( response ) )
        f.write( s_misc.json_encode(response) )
    s_log.write_msg( "cache updated" )

def get_data( request_list ) :
    if( not is_enabled( ) ) : return False
    request_str = request_list[ 0 ] + json.dumps( request_list[ 1 ] )
    cache_hash = hashlib.sha256( request_str.encode('utf-8') ).hexdigest( )
    cache_filepath = cache_dirpath + cache_hash + ".json"
    with open( cache_filepath , "r" ) as f :
        return( json.load( f ) )


def init_path( fp ) :
    #s_log.write_msg(fp)
    #s_log.write_msg(os.path.dirname(fp))

    fpdirname=os.path.dirname(fp)

    if( not os.path.isdir( fpdirname ) ) :
        os.makedirs( fpdirname , exist_ok = True )

#####################################################################

#init_directory( )
    