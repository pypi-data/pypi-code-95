import os
import logging
import re
import sys

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

def is_paxlst(data):

    # mandatory EDIFACT segments
    edifact = ["UNB", "UNH", "UNT", "UNZ"]

    # mandatory PAXLST segments
    paxlst = ["ATT", "BGM", "CNT", "DOC", "NAD", "NAT", "TDT", "UNE", "UNG"]

    # for logging purposes only
    edifact_segments_missing = []
    for x in edifact:
        if x not in data:
            edifact_segments_missing.append(x)

    paxlst_segments_missing = []
    for x in paxlst:
        if x not in data:
            paxlst_segments_missing.append(x)

    # check if all mandatory EDIFACT segments are present
    if all(x in data for x in edifact):
        # check if all mandatory PAXLST segments are present
        if all(x in data for x in paxlst):
        
            # attempt to clean PAXLST file
            return True
                    
        else:
            logging.error('Not a valid PAXLST file. PAXLST segments missing: ' + str(paxlst_segments_missing))
            return False

    else:
        logging.error('Not a valid EDIFACT file. EDIFACT segments missing: ' + str(edifact_segments_missing))
        return False


def clean(data):

    # trim new lines
    data = data.replace('\n', '').replace('\r', '')

    # trim hex characters
    data = re.sub(r'[^\x00-\x7f]', r'', data)

    if is_paxlst(data):

        # Service String Advice
        service_string_advice = "UNA"
        
        # Interchange Trailer; end of message segment
        interchange_trailer = "UNZ"
        
        # length of the SSA string according to PAXLST spec
        service_string_advice_length = 6
        
        # check if Service String Advice present
        if service_string_advice in data:
                    
            # trim Default Service Characters 
            default_service_characters = data[data.index(service_string_advice) +
                len(service_string_advice):data.index(service_string_advice) +
                len(service_string_advice) + service_string_advice_length]

            # Segment Terminator
            segment_terminator = default_service_characters[5] 
                    
            # beginning of PAXLST message
            # trim everythin before SSA string
            data = data[data.index(service_string_advice):]
            
            # end of PAXLST message
            # the PAXLST message ends after the Segment Terminator or the Interchange Trailer
            # i.e. UNZ...’ <-
            data = data[:data.index(segment_terminator,data.index(interchange_trailer)) + 1]
            
            # add newlines to increase readability
            paxlst = data.replace(segment_terminator, segment_terminator + "\n")
            
            # logging.info (paxlst)
            return (paxlst)

        # Service String Advice absent
        else:
            # assume default SSA: ":+.? '"
            segment_terminator = "'"

            # In case the Service String Advice("UNA") is missing, 
            # the message starts with the Interchange Header("UNB")
            interchange_header = "UNB"

            data = data[data.index(interchange_header):]
            
            # end of PAXLST message
            # the PAXLST message ends after the Segment Terminator or the Interchange Trailer
            # i.e. UNZ...’ <-
            data = data[:data.index(segment_terminator,data.index(interchange_trailer)) + 1]
            
            # add newlines to increase readability
            paxlst = data.replace(segment_terminator, segment_terminator + "\n")
            
            # logging.info (paxlst)
            return (paxlst)

    else:
        sys.exit()

def cleanfile(filename):

    if os.path.isfile(filename):
        with open(filename, 'r') as file:
            
            filecontent = file.read()
            return clean(filecontent)

    else:
        logging.error("File does not exist: " + filename)
        sys.exit()

