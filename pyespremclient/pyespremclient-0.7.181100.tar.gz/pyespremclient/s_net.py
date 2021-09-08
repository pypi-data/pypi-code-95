
#####################################################################
#
# ESPREM Client Net
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
import time
import requests
from requests import ReadTimeout, ConnectTimeout, HTTPError, Timeout 

from . import s_log , s_config

#####################################################################

def get_response( request_endpoint , request_params , request_id , request_timeout ) :

    s_log.write_msg( "s_net.get_response START" )

    ################################################################

    headers =   {
                    "content-type" : "application/json" 
                }
    
    payload =   {
                    "method" : request_endpoint ,
                    "params" : request_params ,
                    "jsonrpc" : "2.0" ,
                    "id" : request_id ,
                }

    ################################################################

    try :

        response = requests.post( s_config.get_key( "url_endpoint" ) , json = payload , headers = headers , timeout = request_timeout )


        #s_log.write_msg( "s_net.get_response SLEEP 5" )
        #time.sleep(5)

        s_log.write_msg( "s_net.get_response END" )

        if( response.status_code != 200 ) :

            response =  {
                            "_error" :  {
                                            "error" : True ,
                                            "error_code" : "status_code" ,
                                            "error_msg" : response.text ,
                                        }
                        }    

            return( response )    

    except requests.ConnectionError as e :

        response =  {
                        "_error" :  {
                                        "error" : True ,
                                        "error_code" : "ConnectionError" ,
                                        "error_msg" : str( e ) ,
                                    }
                    }    

        return( response )    

    except requests.HTTPError as e :

        response =  {
                        "_error" :  {
                                        "error" : True ,
                                        "error_code" : "HTTPError" ,
                                        "error_msg" : str( e ) ,
                                    }
                    }    

        return( response )    

    except requests.exceptions.InvalidSchema as e :

        response =  {
                        "_error" :  {
                                        "error" : True ,
                                        "error_code" : "InvalidSchema" ,
                                        "error_msg" : str( e ) ,
                                    }
        
                    }    

        return( response )   

    except requests.exceptions.InvalidURL as e :

        response =  {
                        "_error" :  {
                                        "error" : True ,
                                        "error_code" : "InvalidURL " ,
                                        "error_msg" : str(e) ,
                                    }
                    }    

        return( response )    

    except requests.exceptions.MissingSchema as e :

        response =  {
                        "_error" :  {
                                        "error" : True ,
                                        "error_code" : "MissingSchema " ,
                                        "error_msg" : str( e ) ,
                                    }
                    }    

        return( response )    

    except( ConnectTimeout, HTTPError, ReadTimeout, Timeout ) :
        response =  {
                        "_error" :  {
                                        "error" : True ,
                                        "error_code" : "TIMEOUT" ,
                                        "error_msg" : "TIMEOUT" ,
                                    }
                    }    

        return( response )  


    ################################################################

    response = response.json( )

    if( "result" in response ) :
        return( response[ "result" ] )
    
    ################################################################

    return( response[ "error" ] )


    

    