# Copyright 2021 Akita Software, Inc.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#    http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.conf import settings
from django.utils import timezone
import threading
import platform
import queue
import pydantic
import requests
import json
import time
import logging
from typing import List, Optional

from . import har
import akita_har.models as har_models

#
# API for communicating with Daemon
#
class LoggingOptions(pydantic.BaseModel):
    trace_name: str
    trace_id: str   # NB: no public package defines our Python akid types
    service_id: str
    sample_rate: Optional[float]
    filter_third_party_trackers: bool

class ActiveTraceDiff(pydantic.BaseModel):
    activated_traces: List[LoggingOptions]
    deactivated_traces: List[str]

class MiddlewareRegistration(pydantic.BaseModel):
    client_name: str
    active_trace_ids: List[str]

class Traces(pydantic.BaseModel):
    client_name: str
    trace_events: List[har_models.Entry]
    no_more_events: bool
    
#
# Middleware class
#

class AkitaMiddleware(object):
    """Sends requests and responses to an Akita CLI running in daemon mode.
    The config file entries used by this middleware are:

    AKITA_SERVICE_NAME: identifies the Akita service corresponding to this application
    AKITA_MIDDLEWARE_NAME (default is hostname): identifies the middleware in the Akita web console 
    AKITA_DAEMON_HOST (default "localhost:50080"): network address of the Akita daemon
    AKITA_MAX_QUEUE_LEN (default 200): maximum number of events to buffer
    """
    
    def __init__( self, get_response ):
        # Next handler on the stack
        self.get_response = get_response

        self.logger = logging.getLogger( __name__ )

        # This configurationn is mandatory
        self.service_name = settings.AKITA_SERVICE_NAME

        # These configurations have defaults
        self.middleware_name = getattr( settings, "AKITA_MIDDLEWARE_NAME", platform.node() )
        self.daemon_host = getattr( settings, "AKITA_DAEMON_HOST", "localhost:50080" )
        max_queue_len = getattr( settings, "AKITA_MAX_QUEUE_LEN", 200 )
        
        # Only report request/response pairs when the daemon indicates that
        # collection has been enabled.  We have one thread long-polling the daemon
        # and another delivering trace events from a queue.        
        self.trace_enabled = False
        self.trace_lock = threading.Lock()
        self.trace_active = []
        self.trace_queue = queue.Queue(maxsize=max_queue_len)
        
        self.long_poll_thread = threading.Thread( target=self.long_poll, daemon=True )
        self.upload_thread = threading.Thread( target=self.upload, daemon=True )
        self.long_poll_thread.start()
        self.upload_thread.start()
        

    def capture_request( self ):
        with self.trace_lock:
            return self.trace_enabled
        
    def __call__(self, request):
        processing_start = timezone.now()

        response = self.get_response(request)

        if self.capture_request():
            entry = har.django_to_har_entry(processing_start, request, response)
            # If queue is full, just drop the trace event
            self.trace_queue.put( entry, block=False )
            
        return response

    def long_poll( self ):
        url = f"http://{self.daemon_host}/v1/services/{self.service_name}/middleware"
        headers = { "content-type" : "application/json" }
        
        while True:
            with self.trace_lock:
                active_trace_ids = [ l.trace_id for l in self.trace_active ]
                
            payload = MiddlewareRegistration(
                client_name = self.middleware_name,
                active_trace_ids = active_trace_ids
            )

            try:
                resp = requests.post( url, data=payload.json(), headers=headers )
                if resp.status_code != requests.codes.ok and resp.status_code != requests.codes.accepted:
                    self.logger.warning( f"Error response {resp.status_code} from daemon: {resp.text}" )
                    time.sleep(60)
                    continue
                
                diff = ActiveTraceDiff( **resp.json() ) 
            except requests.exceptions.RequestException as e:
                self.logger.warning( f"HTTP request error communicating with daemon: {e}" )
                time.sleep( 60 )
                continue
            except pydantic.ValidationError as e:
                self.logger.warning( f"Can't parse response from daemon: {e}" )
                time.sleep( 60 )
                continue

            for a in diff.deactivated_traces:
                self.logger.info( f"Deactivating trace ID {a}" )
            for a in diff.activated_traces:
                self.logger.info( f"Activating trace ID {a.trace_id} name {a.trace_name}" )
                
            with self.trace_lock:
                self.trace_active = [ a for a in self.trace_active if a.trace_id not in diff.deactivated_traces ]
                already_active = set( a.trace_id for a in self.trace_active )
                self.trace_active.extend( t for t in diff.activated_traces if t not in already_active )
                self.trace_enabled = len( self.trace_active ) > 0

    def upload( self ):
        while True:
            e = self.trace_queue.get()

            # Somebody may have asked for the events to go to more than
            # one trace. I think sample_rate is the daemon's responsibility, though.
            to_traces = []            
            with self.trace_lock:
                to_traces = [ a.trace_name for a in self.trace_active ]

            for trace_name in to_traces:
                url = f"http://{self.daemon_host}/v1/services/{self.service_name}/traces/{trace_name}/events"
                headers = { "content-type" : "application/json" }
                payload = Traces(
                    client_name = self.middleware_name,
                    trace_events = [e],
                    no_more_events = False
                )
                try:
                    resp = requests.post( url, data=payload.json(), headers=headers )
                    if resp.status_code != requests.codes.ok and resp.status_code != requests.codes.accepted:
                        self.logger.warning( f"Error response {resp.status_code} from daemon: {resp.text}" )                       
                except requests.exceptions.RequestException as e:
                    self.logger.warning( f"HTTP request error communicating with daemon: {e}" )
                    continue

            
    
