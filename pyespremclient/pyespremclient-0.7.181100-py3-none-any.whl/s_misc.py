
#####################################################################
#
# ESPREM Client Misc
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
import atexit
import json
import pickle
import numpy

from . import s_log  

#####################################################################

def cleanup( ) :
    s_log.write_msg( "CLEANUP" )

atexit.register( cleanup )
s_log.write_msg( "Registered cleanup" )

#####################################################################

class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """
    def default(self, obj):
        if isinstance(obj, numpy.integer):
            return int(obj)
        elif isinstance(obj, numpy.floating):
            return float(obj)
        elif isinstance(obj, numpy.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

def json_encode( data ) :
    return json.dumps(data, cls=NumpyEncoder)

#####################################################################

def pickle_load( fn ) :
    if( os.path.isfile( fn ) ) :
        s_log.write_msg( "FOUND " + fn )
        with open( fn , "rb" ) as f :
            return( pickle.load( f ) )
    else:
        return None
        
def pickle_save( data ) :
    #f = open("local_espremrunresponse.pkl","wb")
    #pickle.dump(run_response,f)
    #f.close()
    pass


    