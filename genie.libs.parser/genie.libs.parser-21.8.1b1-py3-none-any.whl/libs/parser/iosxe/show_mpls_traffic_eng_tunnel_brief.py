''' show_mpls_traffic_eng_tunnel_brief.py

IOSXE parsers for the following show commands:
    * show mpls traffic-eng tunnels brief
	
'''

# Python
import re

# Metaparser
from genie.metaparser import MetaParser
from genie.metaparser.util.schemaengine import Schema, Any, Optional

# parser utils
from genie.libs.parser.utils.common import Common


# =============================================
# Parser for 'show mpls traffic-eng tunnels brief'
# =============================================

class ShowMplsTrafficEngTunnelBriefSchema(MetaParser):
    """Schema for show mpls traffic-eng tunnels brief
    """

    schema = {
            Optional('signalling_summary'): {
	                Optional('lsp_tunnels_process'): str,
	            	Optional('passive_lsp_listener'): str,
	            	Optional('rsvp_process'): str,
	            	Optional('forwarding'): str,
	            	Optional('auto_tunnel'): {
	            		Optional('p2p_state'): str,
	            		Optional('min_range'): str,
	            		Optional('max_range'): str
	            	},
	            	Optional('periodic_reoptimization'): str,
	            	Optional('periodic_frr_promotion'): str,
	            	Optional('periodic_auto_bw_collection'): str,
	            	Optional('sr_tunnel_max_label_push'): str

	        },
	        'p2p_tunnels': {
	        	 Optional('tunnel_id'): {
                    Optional(Any()):{
	        	        Optional('destination_ip'): str,
	        	        Optional('up_intf'): str,
	        	        Optional('down_intf'): str,
	        	        Optional('state'): str,
	        	        Optional('prot'): str
                    },
                 },
	        },
            'p2mp_tunnels': {
                      Optional('tunnel_id'):str
            }

	}

class ShowMplsTrafficEngTunnelBrief(ShowMplsTrafficEngTunnelBriefSchema):
    """ Parser for show mpls traffic-eng tunnels brief"""

    cli_command = 'show mpls traffic-eng tunnels brief'
	
    def cli(self, output=None):
        if output is None:
            out = self.device.execute(self.cli_command)
        else:
            out = output

        result_dict = {}
        res=1
        
        #Matches pattern with key:
        #Eg:
        #Signalling Summary:
        #P2P TUNNELS/LSPs:
        #P2MP TUNNELS:        
        p1=re.compile(r"^(?P<key>[a-zA-Z\/\d ]+)\:$")

        #Matched lines for p2 regex, all the string with the format, key: value
        # Eg: LSP Tunnels Process:            running        
        p2=re.compile(r'^(?P<key1>[\S ]+)\:\s+(?P<value1>[\S ]+)$')
        
        #Macallan-SVL_t100                2.2.2.2          -         Gi1/1/0/2 up/up        
        p3=re.compile(r'\S+\_(?P<tunnel_id>\S+)\s+(?P<destination_ip>\S+)\s+(?P<up_intf>\S+)\s+(?P<down_intf>\S+)\s+(?P<state>\S+)\/(?P<prot>\S+)')

        #p2p    Disabled (0), id-range:62336-64335
        p4=re.compile(r'\S+\s+(?P<p2p_state>\S+)\s+\S+\,\s+[a-z\- ]+\:(?P<min_range>\d+)\-(?P<max_range>\d+)')

        for line in out.splitlines():
            line=line.strip()

            #P2P TUNNELS/LSPs:
            #line that contains <key>:
            m1=p1.match(line)
            if m1:
               r=m1.groupdict()
               key=r['key'].lower().replace(" ","_").replace("/lsps","")##replace space and /lsps
               result_dict[key]={}

            #    Periodic reoptimization:        every 180 seconds, next in 127 seconds
            m2=p2.match(line)
            if m2:
                r1=m2.groupdict()
                #Value that have , or ( fetch the first digit from that line else consider the value as it is.
                #Eg:Periodic reoptimization: every 180 seconds, next in 127 seconds
                if ("," in r1['value1']) or ("(" in r1['value1']) :
                    res2=re.findall('(\d+)',r1['value1'])[0]
                else:
                    #LSP Tunnels Process:            running
                    res2=r1['value1']
                result_dict[key][r1['key1'].lower().replace(" ","_").replace("-","_")]=res2
                
            #Macallan-SVL_t100                          2.2.2.2          -         Po60      up/up
            m3=p3.match(line)
            if m3:
                if res==1:
                    result_dict[key]['tunnel_id']={}
                    res=0
                r3=m3.groupdict()
                key1=r3['tunnel_id']
                del r3['tunnel_id']                
                result_dict[key]['tunnel_id'][key1]={}
                for item,value in r3.items():
                    result_dict[key]['tunnel_id'][key1][item]=value
                    
            #Add 'auto-tunnel' as key
            if "auto-tunnel" in line:
                result_dict[key]['auto_tunnel']={}

            #	p2p    Disabled (0), id-range:62336-64335
            m4=p4.match(line)
            if m4:
                r4=m4.groupdict()
                for item,value in r4.items():
                    result_dict[key]['auto_tunnel'][item]=value
        return result_dict



