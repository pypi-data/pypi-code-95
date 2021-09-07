''' show_mpls_traffic_tunnel.py

IOSXE parsers for the following show commands:

    * 'show mpls traffic-eng tunnels {tunnel}'
    * 'show mpls traffic-eng tunnels'
'''

# Python
import re
import logging

# Metaparser
from genie.metaparser import MetaParser
from genie.metaparser.util.schemaengine import Any, Optional

log = logging.getLogger(__name__)


class ShowMplsTrafficEngTunnelTunnelidSchema(MetaParser):
    """Schema for show mpls traffic-eng tunnels {tunnel} """

    schema = {
        'tunnel':{
	        Any(): {
	         	'destination': str, 
	         	'status': {
	         		'admin': str, 
	         		'oper': str, 
	         		'path': str, 
	         		'signalling': str, 
                        'path_option': {
                            Optional(Any()): {
                                'type': str,
                                Optional('path_name'):str, 
                                Optional('path_weight'): int,
                                Optional('path_attribute'):str,
                                Optional('lockdown'): bool,
                                Optional('attribute'):str,
                            },
                          },
	         	}, 
	         	'config_parameters': {
	         		'bandwidth': int, 
	         		'bandwidth_unit': str, 
	         		'bandwidth_type': str, 
	         		'priority': {
	         		    'setup_priority':int,
	         		    'hold_priority':int
	         		}, 
	         		'affinity': str, 
	         		'metric_used': str, 
	         		Optional('metric_type'): str, 
	         		Optional('path_selection_tiebreaker'): {
	         			'global': str, 
	         			'tunnel_specific': str, 
	         			'effective': str,
                        'effective_type':str
	         		}, 
	         		Optional('hop_limit'): str, 
	         		Optional('cost_limit'): str, 
	         		Optional('path_invalidation_timeout'): int, 
	         		Optional('path_invalidation_timeout_unit'): str, 
	         		Optional('path_invalidation_timeout_type'): str, 
	         		Optional('action'): str, 
	         		Optional('autoroute'): str, 
	         		Optional('lockdown'): str, 
	         		Optional('loadshare'): int,
                    Optional('max_load_share'): int,
                    Optional('load_share_type'): str,
	         		Optional('auto_bw'): str, 
	         		Optional('fault_oam'): str, 
	         		Optional('wrap_protection'): str, 
	         		Optional('wrap_capable'): str,
                                Optional('autoroute_destination'): str
	         	}, 
	         	Optional('active_path_option_parameters'): {
	         		'state': {
	         			'active_path':str,
	         			'path_type':str
	         		},
	         		Optional('bandwidthoverride'): str, 
	         		Optional('lockdown'): str, 
	         		Optional('verbatim'): str, 
	         	}, 
	         	Optional('node_hop_count'): int,
	         	Optional('inlabel'): list, 
	         	Optional('outlabel'): list, 
	         	Optional('next_hop'): list, 
	         	Optional('rsvp_signalling_info'): {
	         		'src': str, 
	         		'dst': str, 
	         		'tun_id': int, 
	         		'tun_instance': int, 
	         		'rsvp_path_info': {
	         			Optional('my_address'): str, 
	         			'explicit_route': list, 
	         			Optional('record_route'): str, 
	         			Optional('tspec'): {
	         				'ave_rate': int,
                                                'ave_rate_unit':str,                            
	         				'burst': int,
                                                'burst_unit':str,                            
	         				'peak_rate': int,
                                                'peak_rate_unit':str
	         			}
	         		}, 
                                Optional('rsvp_resv_info'): {
                                    'record_route': str, 
                                    'fspec': {
                                        'ave_rate': int, 
                                        'ave_rate_unit':str,                            
                                        'burst': int, 
                                        'burst_unit':str,
                                        'peak_rate': int,
                                        'peak_rate_unit':str
	         		    },
                               },
                },
                Optional('shortest_unconstrained_path_info'): {
                    'path_weight': Any(),
                    Optional('path_weight_type'): str,
                    'explicit_route': list
                },
                Optional('history'): {
                    'tunnel': {
                            Any(): str,
                            'number_of_lsp_ids_used':int                            
                     }, 
                     Optional("current_lsp_id"): {
                            Any():{
                                Any():str
                            }
                     },
                     Optional('prior_lsp_id'): {
                            Any():{
                                Optional('id'): str, 
                                Optional('removal_trigger'): str,
                                Optional('last_error'):str
                          }
                     },
                 },
             },
       	},
     }

class ShowMplsTrafficEngTunnelTunnelid(ShowMplsTrafficEngTunnelTunnelidSchema):
    """Parser show mpls traffic-eng tunnels {tunnel}"""

    cli_command = ['show mpls traffic-eng tunnels {tunnel}']

    def cli(self, tunnel='', output=None):
        if not output:
            cmd = self.cli_command[0].format(tunnel=tunnel)            
            output = self.device.execute(cmd)
    
        res={}
        result=1

        if not output.strip():
            return res

        ##Regex
        ###Name: R3_t100                             (Tunnel100) Destination: 2.2.2.2
        p1=re.compile(r'^\S+:\s+\S+\s+\((?P<Tunnel>\S+)\)\s+\S+\s+(?P<destination>\S+)')
        
        ###Eg:Status:,Config Parameters:,Active Path Option Parameters:		
        p2=re.compile(r'^(?P<key>[a-zA-Z\- ]+)\:$')
        ###Mentions the keys to be considered
        p2_1=re.compile(r'Status:|Config Parameters:|Active Path Option Parameters:|RSVP Signalling Info:|History:|Shortest Unconstrained Path Info:')
        
        
        ###path option 1, type explicit R3_R4_R5_R2 (Basis for Setup, path weight 3)
        p3=re.compile(r"^[a-zA-Z ]+(?P<path_option>[0-9 ]+)\,\s+(?P<lockdown>\([A-Z]+\))?"
                "\s*\S+\s(?P<type>[a-zA-Z_0-9 ]+)\s*(?:\(.*\,[a-z ]+(?P<path_weight>\S+)\))?$")
        p3_1=re.compile(r"^Path-option attribute:\s(?P<path_attribute>\S+)$")
                
        ###Src 3.3.3.3, Dst 2.2.2.2, Tun_Id 100, Tun_Instance 28
        p4=re.compile(r"^Src\s+([0-9\. ]+)\,")

        ###State:
        p5=re.compile(r"^State:")
        
        ###Time since created: 14 minutes, 44 seconds
        p6=re.compile(r"^Time\s+")
        
        ###Bandwidth: 500      kbps (Global)  Priority: 7  7   Affinity: 0x0/0xFFFF
        p7=re.compile(r'^Bandwidth:\s+(?P<bandwidth>.*)\s+[a-zA-Z ]+\:\s+(?P<priority>[0-9 ]+)'
                       '\s+[a-zA-Z ]+\:\s+(?P<affinity>\S+)$')
        
        ### InLabel  :  -
        ###OutLabel : Port-channel30, 63
        ###Next Hop : 193.1.1.2
        p8=re.compile(r"^([a-zA-Z ]+)\s+\:\s+([a-zA-Z\-0-9\.\, ]+)$")
        
        ###AutoRoute: enabled  LockDown: disabled Loadshare: 500 [4000000] bw-based
        p9=re.compile(r"^AutoRoute\:\s+(?P<autoroute>\S+)\s+\S+\:\s+(?P<lockdown>\S+)"
        "\s+\S+\:\s+(?P<loadshare>\d+)\s+\[(?P<max_load_share>\d+)\]\s+(?P<load_share_type>\S+)$")
        
        ###Record   Route:
        ###Tspec:,Fspec:
        p10=re.compile(r"Record   Route:|[A-Za-z ]+spec\:\s+.*")

        ###Fault-OAM: disabled, Wrap-Protection: disabled, Wrap-Capable: No
        ###Hop Limit: disabled
        ###Cost Limit: disabled
        ###BandwidthOverride: disabled  LockDown: enabled   Verbatim: disabled
        ###auto-bw: disabled
        p11=re.compile(r'Hop|Cost|auto-bw:'
                        '|State:|Path Weight:|BandwidthOverride:|Fault-OAM:|AutoRoute destination:')
        
        ###Explicit Route: 193.1.1.2 196.1.1.2 196.1.1.1 198.1.1.1
        #              198.1.1.2 2.2.2.2 
        p12=re.compile(r"^\d+\.\d+\.\d+\.\d+")

        ###Admin: up         Oper: up     Path: valid       Signalling: connected
        p13=re.compile(r"(Admin|Oper|Path|Signalling):([a-zA-Z\- ]+\s|[a-zA-Z\- ]+)")
        
        ##Path-invalidation timeout: 10000 msec (default), Action: Tear
        p14=re.compile(r"^Path-invalidation.+\:\s+(?P<path_invalidation_timeout>\d+)\s+"
                "(?P<path_invalidation_timeout_unit>\w+)\s+\((?P<path_invalidation_timeout_type>\S+)\)\,"
                "\s+\S+\s+(?P<action>\w+)$")
                
        ###Number of LSP IDs (Tun_Instances) used:
        p15=re.compile(r"Number of LSP IDs \(Tun_Instances\) used:\s+\d+")
                
        ###Current LSP: [ID: 19]
        p16=re.compile(r"^Current LSP:\s+\[ID:\s+(?P<id>\d+)\]$")

        ###Uptime: 9 hours, 52 minutes
        ###Selection: reoptimization
        p17=re.compile(r"(Uptime|Selection):\s+([0-9a-zA-Z, ]+)")
        
        ##Metric Type: TE (default)
        p18=re.compile(r"^Metric Type:\s+(?P<metric_used>\S+)(?:\s+\((?P<metric_type>\S+)\))*")
        
        ###Prior LSP: [ID: 19]
        p19=re.compile(r"^Prior LSP:\s+\[ID:\s+(?P<id>\d+)\]$")

        ##ID: path option 3 [35]
        ##Removal Trigger: tunnel shutdown
        ##Last Error: CTRL:: Explicit path has unknown address, 194.1.1.1
        p20=re.compile(r"(ID|Removal Trigger|Last Error):\s+([0-9a-zA-Z,.: ]+)")
        
        ###Global: not set   Tunnel Specific: not set   Effective: min-fill (default)
        p21=re.compile(r"^Global:\s+(?P<global>[a-zA-Z ]+)\s+Tunnel Specific:\s+(?P<tunnel_specific>[a-zA-Z ]+)\s+Effective:\s+(?P<effective>\S+)\s*\(?(?P<effective_type>[a-zA-Z ]+)?\)?$")
        
        ###Path Weight: 1 (TE)
        p22=re.compile(r"^Path Weight:\s+(?P<path_weight>(\d+))\s+\(?(?P<path_weight_type>[A-Za-z]+)?\)?$")
        
        path_option=""
        id=''
        res['tunnel']={}
        for line in output.splitlines():
            line = line.strip()
			
            ###Name: R3_t100 (Tunnel100) Destination: 2.2.2.2
            ##Eg:{tunnel100:{destiantion:2.2.2.2}}
            m1=p1.match(line)
            if m1:
                r=m1.groupdict()
                key=r['Tunnel']
                res['tunnel'][key]={}
                res['tunnel'][key]['destination']=r['destination']
                continue
            
            ###Create key,subkeys
            ###Matched line for key 
            ###Eg:Status:,Config Parameters:,Active Path Option Parameters:
            ###Then subkeys, Eg:{config_parameters:{path_selection_tiebreaker:{}},...}
            m2=p2.match(line)
            if m2:
                r1=m2.groupdict()
                if r1['key']=="Path-selection Tiebreaker":
                    ##{config_parameters:path_selection_tiebreaker}
                    res['tunnel'][key]["config_parameters"][r1['key'].lower()\
                        .replace(" ","_").replace("-","_").strip()]={}
                elif r1['key'] == "RSVP Path Info":
                    ##{rsvp_signalling_info:{rsvp_path_info:{}}
                    key3=r1['key'].lower().replace(" ","_").replace("-","_").strip()
                    res['tunnel'][key]["rsvp_signalling_info"][key3]={}
                elif r1['key'] == "RSVP Resv Info":
                    ##{rsvp_signalling_info:{rsvp_resv_info:{}}
                    key3=r1['key'].lower().replace(" ","_").replace("-","_").strip()
                    res['tunnel'][key]["rsvp_signalling_info"][key3]={}
                elif r1['key'] == "Tunnel":
                    ##tunnel:
                    res['tunnel'][key]["history"]['tunnel']={}
                else:
                    if p2_1.match(line):
                        key1=r1['key'].lower().replace(" ","_").strip()
                        res['tunnel'][key][key1]={}
                continue
				
            ####path option 1, type explicit R3_R4_R5_R2 (Basis for Setup, path weight 3)
            m3=p3.match(line)
            if m3:
                fin=m3.groupdict()
                path_option="path_option"
                if result==1:
                    res['tunnel'][key][key1][path_option]={}
                    result=0
                for item,value in fin.items():
                    if item=="path_option":
                        path=value
                        res['tunnel'][key][key1][path_option][path]={}
                    else:
                        if item=="type":
                            s=value.split()
                            res['tunnel'][key][key1][path_option][path]['type']=s[0].strip()
                            if s[0]!="dynamic":
                                res['tunnel'][key][key1][path_option][path]['path_name']=s[1].strip()
                        elif item == "lockdown":
                            if fin["lockdown"]:
                                res['tunnel'][key][key1][path_option][path]['lockdown']=True
                        else:
                            if value:
                                res['tunnel'][key][key1][path_option][path][item]=int(value)
                continue
                
            ###Path-option attribute: TU1_attrib
            m3_1=p3_1.match(line)
            if m3_1:
                grp=m3_1.groupdict()
                for item,value in grp.items():
                    res['tunnel'][key][key1][path_option][path][item]=value
				
            ###Src 3.3.3.3, Dst 2.2.2.2, Tun_Id 100, Tun_Instance 28
            m4=p4.match(line)
            if m4:
                a=line.split(",")
                for i in a:
                    i=i.strip()
                    j=i.split(" ")[1]
                    res['tunnel'][key][key1][i.split(" ")[0].lower().strip()]=\
                            int(j) if j.isdigit() else j
                continue

            ###State: explicit path option 1 is active
            m5=p5.match(line)
            if m5:
                res['tunnel'][key][key1]['state']={}
                res['tunnel'][key][key1]['state']['active_path']=\
                                re.findall(r"(\d+)",line.split(":")[1].strip())[0]
                res['tunnel'][key][key1]['state']['path_type']=\
                                line.split(":")[1].split()[0]  
                continue
                
            ###Time since created: 14 minutes, 44 seconds
            m6=p6.match(line)
            if m6:
                time=line.split(":")[0].lower().strip().replace(" ","_")
                res['tunnel'][key][key1]['tunnel'][time]=line.split(":")[1].strip()
                continue	
  
            ###Bandwidth: 500      kbps (Global)  Priority: 7  7   Affinity: 0x0/0xFFFF
            m7= p7.match(line)
            if m7:
                r4=m7.groupdict()
                for item,value in r4.items():
                    if item == "priority":
                        res['tunnel'][key][key1]['priority']={}
                        tg=value.split()
                        res['tunnel'][key][key1]['priority']['setup_priority']=int(tg[0])
                        res['tunnel'][key][key1]['priority']['hold_priority']=int(tg[1])
                    elif item == "bandwidth":
                        bandwidth_detail=value.split()
                        res['tunnel'][key][key1][item]=int(bandwidth_detail[0])
                        res['tunnel'][key][key1]["bandwidth_unit"]=bandwidth_detail[1]
                        res['tunnel'][key][key1]["bandwidth_type"]=\
                                        re.sub(r"[()]","",bandwidth_detail[2])
                    else:
                        res['tunnel'][key][key1][item]=value.strip()
                continue

            ###Match InLabel : -
            m8 = p8.match(line)
            if m8:
                r8=m8.group()
                res['tunnel'][key][r8.split(":")[0].strip().lower().replace(" ","_")]=\
                                    r8.split(":")[1].strip().split(",")
                continue

            ###AutoRoute: enabled  LockDown: disabled Loadshare: 500 [4000000] bw-based
            m9=p9.match(line)
            if m9:
                r9=m9.groupdict()
                for item,value in r9.items():
                    res['tunnel'][key][key1][item.strip()]=\
                    int(value) if value.strip().isdecimal() else value
                continue
                
            ###Record   Route:   NONE
            ###Tspec: ave rate=500 kbits, burst=1000 bytes, peak rate=500 kbits
            m10=p10.match(line)
            if m10:
                if "=" not in line:
                    res['tunnel'][key][key1][key3]["record_route"]=line.split(":")[1].strip()
                else:
                    r7=m10.group()
                    key5=r7.split(":")[0].strip().lower()
                    res['tunnel'][key][key1][key3][key5]={}
                    r8=r7.split(":")[1].split(",")
                    for i in r8:
                        res10=i.split("=")[1].split()
                        item=i.split("=")[0].lower().strip().replace(" ","_")
                        res['tunnel'][key][key1][key3][key5][item]=int(res10[0])
                        res['tunnel'][key][key1][key3][key5][item+"_unit"]=res10[1]
                continue           

            ###Global: not set   Tunnel Specific: not set   Effective: min-fill (default) 
            ###Make global part of path_selection_tiebreaker
            m21=p21.match(line)
            if m21:
                re21=m21.groupdict()        
                for item,value in re21.items():
                    res['tunnel'][key]['config_parameters']["path_selection_tiebreaker"][item.split(":")[0].strip().replace(" ","_").lower()]=\
                    value.strip()
                continue
                
            ##Path Weight: 1 (TE)
            m22=p22.match(line)
            if m22:
                re22=m22.groupdict()        
                for item,value in re22.items():
                    res['tunnel'][key][key1][item]=value.strip()
                continue
                
            ###Make explicit route as part of rsvp_path_info or shortest_unconstrained_path_info respectively
            ###Make my address as part of rsvp_path_info
            ###My Address: 192.1.1.1
            ###Explicit Route: 192.1.1.2 2.2.2.2
            if re.match("^Explicit Route:|My",line):
                if "Explicit Route:" in line:
                    explicit_route=[]
                    explicit_route.extend(line.split(":")[1].split())
                        
                    if key1=="rsvp_signalling_info": 
                       res['tunnel'][key][key1]['rsvp_path_info']['explicit_route']=explicit_route
                    elif key1=="shortest_unconstrained_path_info":
                        res['tunnel'][key][key1]['explicit_route']=explicit_route
                else:
                    res['tunnel'][key][key1]['rsvp_path_info'][line.split(":")[0]\
                    .strip().lower().replace(" ","_")]=line.split(":")[1].lower().strip()
                continue      

            ##  Node Hop Count: 1
            if "Node Hop Count:" in line:
                ib=int(line.split(":")[1].lower().strip())
                res['tunnel'][key][line.split(":")[0].strip().lower().replace(" ","_")]=ib
                continue    

            ###Fault-OAM: disabled, Wrap-Protection: disabled, Wrap-Capable: No
            ###Hop Limit: disabled
            ###Cost Limit: disabled
            ###BandwidthOverride: disabled  LockDown: enabled   Verbatim: disabled
            ###auto-bw: disabled
            m11=p11.match(line)
            if m11:
                 line=re.sub(r'\:\s{2,}',": ",line.strip())
                 re9 = re.split("\s{2,}|,",line.strip())
                 for i in re9:
                        ib=i.split(":")[1].strip().replace("[ignore","" ).replace("(te)","").strip()
                        res['tunnel'][key][key1][i.split(":")[0].strip().lower()\
                        .replace(" ","_").replace("-","_").strip()]=int(ib) if ib.isdecimal() else ib
                 continue                

            #Explicit Route: 193.1.1.2 196.1.1.2 196.1.1.1 198.1.1.1
            #                198.1.1.2 2.2.2.2
            if p12.match(line):
                explicit_route.extend(line.split())                               
				
            ###Admin: up         Oper: up     Path: valid       Signalling: connected
            if "Admin:" in line:
                m13 = p13.findall(line)
                if m13:
                    line=re.sub(r'\:\s{1,}',":",line.strip())
                    for match in m13:
                        res['tunnel'][key][key1][match[0].strip().lower()]=match[1].strip().lower()
                continue 

            ##Path-invalidation timeout: 10000 msec (default), Action: Tear
            m14=p14.match(line)
            if m14:
                re14=m14.groupdict()        
                for item,value in re14.items():
                    res['tunnel'][key][key1][item]=int(value) if value.isdecimal() else value
                continue
                
            ###Number of LSP IDs (Tun_Instances) used: 19
            m15=p15.match(line)
            if m15:
                res['tunnel'][key][key1]['tunnel']["number_of_lsp_ids_used"]=int(line.split(":")[1])
                continue

            ###Current LSP: [ID: 19]
            m16=p16.match(line)
            if m16:  
                id=m16.groupdict()             
                res['tunnel'][key][key1]['current_lsp_id']={}
                res['tunnel'][key][key1]['current_lsp_id'][id['id']]={}
                continue
                
            ###Uptime: 9 hours, 52 minutes
            ###Selection: reoptimization
            m17=p17.match(line)
            if m17:  
                res17 = p17.findall(line)
                res['tunnel'][key][key1]['current_lsp_id'][id['id']][res17[0][0].lower()]=res17[0][1]
                continue     
                
            #Metric Type: TE (default)
            m18=p18.match(line)
            if m18:
                res18=m18.groupdict()    
                res['tunnel'][key]["config_parameters"]['metric_used']=res18['metric_used']
                if res18.get("metric_type",None):
                    res['tunnel'][key]['config_parameters']['metric_type']=res18['metric_type']
                continue
                
            ###Prior LSP: [ID: 19]
            m19=p19.match(line)
            if m19:  
                id=m19.groupdict()             
                res['tunnel'][key][key1]['prior_lsp_id']={}
                res['tunnel'][key][key1]['prior_lsp_id'][id['id']]={}
                continue

            ###ID: path option 3 [35]
            ###Removal Trigger: tunnel shutdown
            ###Last Error: CTRL:: Explicit path has unknown address, 194.1.1.1
            m20=p20.match(line)
            if m20:  
                res20 = p20.findall(line)
                for prior_key,prior_value in res20:
                    res['tunnel'][key][key1]['prior_lsp_id'][id['id']][prior_key.lower().replace(" ","_")]=prior_value
                continue                   
            
        return res
        
class ShowMplsTrafficEngTunnelSchema(MetaParser):
    """Schema for show mpls traffic-eng tunnels"""

    schema = {
        'tunnel_type':{
            Any():{
                'tunnel_name':{
	                Any(): {
	                 	Optional('destination'): str, 
                                Optional('signalled_state'): bool,
                                Optional('tunnel_state'): str,
	                 	Optional('status'): {
	                 		'admin': str, 
	                 		'oper': str, 
	                 		'path': str, 
	                 		'signalling': str, 
                                        'path_option': {
                                             Optional(Any()): {
                                                'type': str,
                                                Optional('path_name'):str, 
                                                Optional('path_weight'): int,
                                                Optional('path_attribute'): str,
                                                Optional('lockdown'): bool,
                                                Optional('attribute'):str,
                             	            },
                                       },
	                 	}, 
	                 	Optional('config_parameters'): {
	                 	    'bandwidth': int, 
	         	    	    'bandwidth_unit': str, 
	         	    	    'bandwidth_type': str, 
	                 	    'priority': {
	                 		    'setup_priority':int,
	                 		    'hold_priority':int
	                 	     }, 
	                 	    'affinity': str, 
	         	    	    'metric_used': str, 
	         	    	    Optional('metric_type'): str, 
	                 	    Optional('path_selection_tiebreaker'): {
	                 		    'global': str, 
	                 		    'tunnel_specific': str, 
	                 		    'effective': str,
	                 		    'effective_type': str
	                 	    }, 
	                 	    Optional('hop_limit'): str, 
	                 	    Optional('cost_limit'): str, 
	         	    	    Optional('path_invalidation_timeout'): int, 
	         	    	    Optional('path_invalidation_timeout_unit'): str, 
	         	    	    Optional('path_invalidation_timeout_type'): str, 
                                    Optional('action'): str, 
	                 	    Optional('autoroute'): str, 
	                 	    Optional('lockdown'): str, 
                            Optional('max_load_share'): int,
                            Optional('load_share_type'): str,
	                 	    Optional('loadshare'): int, 
	                 	    Optional('auto_bw'): str, 
	                 	    Optional('fault_oam'): str, 
	                 	    Optional('wrap_protection'): str, 
	                 	    Optional('wrap_capable'): str,
                                    Optional('autoroute_destination'): str
	                 	}, 
	                 	Optional('active_path_option_parameters'): {
	                 		'state': {
	                 			'active_path':str,
	                 			'path_type':str
	                 		},
	                 		Optional('bandwidthoverride'): str, 
	                 		Optional('lockdown'): str, 
	                 		Optional('verbatim'): str, 
	                 	}, 
	                 	Optional('node_hop_count'): int,
	                 	Optional('inlabel'): list, 
	                 	Optional('outlabel'): list, 
	                 	Optional('next_hop'): list, 
                                Optional('prev_hop'): list,
	                 	Optional('rsvp_signalling_info'): {
	                 		'src': str, 
	                 		'dst': str, 
	                 		'tun_id': int, 
	                 		'tun_instance': int, 
	                 		'rsvp_path_info': {
	                 			Optional('my_address'): str, 
	                 			'explicit_route': list, 
	                 			Optional('record_route'): str, 
	                 			Optional('tspec'): {
	         	    			    'ave_rate': int,
                                                    'ave_rate_unit':str,                            
	         	    			    'burst': int,
                                                    'burst_unit':str,                            
	         	    			    'peak_rate': int,
                                                    'peak_rate_unit':str
	                 			}
	                 		}, 
                                        Optional('rsvp_resv_info'): {
                                              'record_route': str, 
                                              'fspec': {
                                                   'ave_rate': int, 
                                                   'ave_rate_unit':str,                            
                                                   'burst': int, 
                                                   'burst_unit':str,
                                                   'peak_rate': int,
                                                   'peak_rate_unit':str
	                 		    },
                                        },
                                 },
                                 Optional('shortest_unconstrained_path_info'): {
                                          'path_weight': Any(),
                                          Optional('path_weight_type'): str,
                                          'explicit_route': list
                                 },
                                 Optional('history'): {
                                        'tunnel': {
                                              Any(): str,
                                             'number_of_lsp_ids_used':int                            
                                         }, 
                                         Optional("current_lsp_id"): {
                                              Any():{
                                                 Any(): str
                                              }
                                         },
                                         Optional('prior_lsp_id'): {
                                              Any():{
                                                 Optional('id'): str, 
                                                 Optional('removal_trigger'): str,
                                                 Optional('last_error'):str
                                              }
                                        }
                                },
                          },
                     },
                },
	    },
        }
class ShowMplsTrafficEngTunnel(ShowMplsTrafficEngTunnelSchema):
    """Parser show mpls traffic-eng tunnels"""

    cli_command = ['show mpls traffic-eng tunnels']

    def cli(self, output=None):
        if not output:
            cmd = self.cli_command[0]
            
            output = self.device.execute(cmd)
            
        res={}
        result=1
        base_key=""
        path_opt,id="",""
        tunnel_types=["P2P TUNNELS/LSPs","P2MP TUNNELS","P2MP SUB-LSPS"]
        if not output.strip():
            return res
            
        ##Regex
        ###Name: R3_t100                             (Tunnel100) Destination: 2.2.2.2
        p1=re.compile(r'^\S+:\s+\S+\s+\((?P<Tunnel>\S+)\)\s+\S+\s+(?P<destination>\S+)')
        
        ###Eg:Status:,Config Parameters:,Active Path Option Parameters:		
        p2=re.compile(r'^(?P<key>[a-zA-Z\-0-9/LSPs ]+)\:$')
        ###Mentions the keys to be considered
        p2_1=re.compile(r'Status:|Config Parameters:|Active Path Option Parameters:'
        '|RSVP Signalling Info:|History:|Shortest Unconstrained Path Info:')
        
        ###path option 1, type explicit R3_R4_R5_R2 (Basis for Setup, path weight 3)
        p3=re.compile(r"^[a-zA-Z ]+(?P<path_option>[0-9 ]+)\,\s+(?P<lockdown>\([A-Z]+\))?"
                "\s*\S+\s(?P<type>[a-zA-Z_0-9 ]+)\s*(?:\(.*\,[a-z ]+(?P<path_weight>\S+)\))?")
        p3_1=re.compile(r"^Path-option attribute:\s(?P<path_attribute>\S+)$")
        
        ###Src 3.3.3.3, Dst 2.2.2.2, Tun_Id 100, Tun_Instance 28
        p4=re.compile(r"^Src\s+([0-9\. ]+)\,")

        ###Time since created: 14 minutes, 44 seconds
        p5=re.compile(r"^Time\s+")
        
        ###Bandwidth: 500      kbps (Global)  Priority: 7  7   Affinity: 0x0/0xFFFF
        p6=re.compile(r'^Bandwidth:\s+(?P<bandwidth>.*)\s+[a-zA-Z ]+\:\s+(?P<priority>[0-9 ]+)'
                       '\s+[a-zA-Z ]+\:\s+(?P<affinity>\S+)$')
        
        ### InLabel  :  -
        ###OutLabel : Port-channel30, 63
        ###Next Hop : 193.1.1.2
        p7=re.compile(r"^([a-zA-Z ]+)\s+\:\s+([a-zA-Z\/\-0-9\.\, ]+)$")
        
        ###AutoRoute: enabled  LockDown: disabled Loadshare: 500 [4000000] bw-based
        p8=re.compile(r"^AutoRoute\:\s+(?P<autoroute>\S+)\s+\S+\:\s+(?P<lockdown>\S+)"
        "\s+\S+\:\s+(?P<loadshare>\d+)\s+\[(?P<max_load_share>\d+)\]\s+(?P<load_share_type>\S+)$")

        ###Record   Route:
        ###Tspec:,Fspec:
        p9=re.compile(r"Record   Route:|[A-Za-z ]+spec\:\s+.*")

        ###Fault-OAM: disabled, Wrap-Protection: disabled, Wrap-Capable: No
        ###Hop Limit: disabled
        ###Cost Limit: disabled
        ###BandwidthOverride: disabled  LockDown: enabled   Verbatim: disabled
        ###auto-bw: disabled
        p10=re.compile(r'Hop|Cost|'
                    'auto-bw:|State:|Path Weight:|BandwidthOverride:|Fault-OAM:|AutoRoute destination:')
        
        ###Explicit Route: 193.1.1.2 196.1.1.2 196.1.1.1 198.1.1.1
        #              198.1.1.2 2.2.2.2 --matches line
        p11=re.compile(r"^\d+\.\d+\.\d+\.\d+")

        ###State:
        p12=re.compile(r"^State:")
        
        ###Admin: up         Oper: up     Path: valid       Signalling: connected
        p13=re.compile(r"(Admin|Oper|Path|Signalling):([a-zA-Z\- ]+\s|[a-zA-Z\- ]+)")

        ##Path-invalidation timeout: 10000 msec (default), Action: Tear
        p14=re.compile(r"^Path-invalidation.+\:\s+(?P<path_invalidation_timeout>\d+)\s+"
                "(?P<path_invalidation_timeout_unit>\w+)\s+\((?P<path_invalidation_timeout_type>\S+)\)"
                "\,\s+\S+\s+(?P<action>\w+)$")
                
        ####LSP Tunnel PE1_t100 is signalled, connection is up
        p15=re.compile(r"^LSP\sTunnel\s+[a-zA-Z0-9]+\_\w"
		              "(?P<tunnel_id>[0-9]+)\s+is\s+(?P<signalled>\S+)\,\s+connection\s+is\s+(?P<state>\S+)$")                
        
        ###Number of LSP IDs (Tun_Instances) used:
        p16=re.compile(r"Number of LSP IDs \(Tun_Instances\) used:\s+\d+")
                
        ###Current LSP: [ID: 19]
        p17=re.compile(r"^Current LSP:\s+\[ID:\s+(?P<id>\d+)\]$")

        ###Uptime: 9 hours, 52 minutes
        ###Selection: reoptimization
        p18=re.compile(r"(Uptime|Selection):\s+([0-9a-zA-Z, ]+)")
        
        ##Metric Type: TE (default)
        p19=re.compile(r"^Metric Type:\s+(?P<metric_used>\S+)(?:\s+\((?P<metric_type>\S+)\))*")
        
        ###Prior LSP: [ID: 19]
        p20=re.compile(r"^Prior LSP:\s+\[ID:\s+(?P<id>\d+)\]$")

        ##ID: path option 3 [35]
        ##Removal Trigger: tunnel shutdown
        ##Last Error: CTRL:: Explicit path has unknown address, 194.1.1.1
        p21=re.compile(r"(ID|Removal Trigger|Last Error):\s+([0-9a-zA-Z,.: ]+)")        
  
        ###Global: not set   Tunnel Specific: not set   Effective: min-fill (default)
        p22=re.compile(r"^Global:\s+(?P<global>[a-zA-Z ]+)\s+Tunnel Specific:\s+(?P<tunnel_specific>[a-zA-Z ]+)\s+Effective:\s+(?P<effective>\S+)\s*\(?(?P<effective_type>[a-zA-Z ]+)?\)?$")
        
        ###Path Weight: 1 (TE)
        p23=re.compile(r"^Path Weight:\s+(?P<path_weight>(\d+))\s+\(?(?P<path_weight_type>[A-Za-z]+)?\)?$")
  
        res['tunnel_type']={}
        for line in output.splitlines():
            line = line.strip()
                
            ###Matched line for key 
            ###Eg:Status:, Config Parameters:, Active Path Option Parameters:
            ###P2MP TUNNELS:, P2MP SUB-LSPS, P2P TUNNELS/LSPs      
            m2=p2.match(line)
            if m2:
                r1=m2.groupdict()
                if r1['key']in tunnel_types:
                    base_key=r1['key'].lower().replace(" ","_").replace(
                        "/lsps","").replace("-","_")
                    res['tunnel_type'][base_key]={}
                    res['tunnel_type'][base_key]['tunnel_name']={}
                    continue
                else:
                    if r1['key']=="Path-selection Tiebreaker":
                            res['tunnel_type'][base_key]['tunnel_name'][key]["config_parameters"][r1['key'].\
                            lower().replace(" ","_").replace("-","_").strip()]={}
                    elif r1['key'] == "RSVP Path Info":
                        key3=r1['key'].lower().replace(" ","_").replace("-","_").strip()
                    
                        res['tunnel_type'][base_key]['tunnel_name'][key]["rsvp_signalling_info"][key3]={}
                    elif r1['key'] == "RSVP Resv Info":
                        key3=r1['key'].lower().replace(" ","_").replace("-","_").strip()
                        res['tunnel_type'][base_key]['tunnel_name'][key]["rsvp_signalling_info"][key3]={}
                    elif r1['key'] == "Tunnel":
                        ##tunnel:
                        res['tunnel_type'][base_key]['tunnel_name'][key]["history"]['tunnel']={}
                    else:
                        if p2_1.match(line):
                            key1=r1['key'].lower().replace(" ","_").strip()
                            res['tunnel_type'][base_key]['tunnel_name'][key][key1]={}
                    continue
              
            ###LSP Tunnel PE1_t100 is signalled, connection is up
            m=p15.match(line)
            if m:
                m15=m.groupdict()
                key="Tunnel"+m15['tunnel_id']
                res['tunnel_type'][base_key]['tunnel_name'][key]={}
                if m15['signalled'] == "signalled":
                    res['tunnel_type'][base_key]['tunnel_name'][key]['signalled_state']=True
                else:
                    res['tunnel_type'][base_key]['tunnel_name'][key]['signalled_state']=False
                res['tunnel_type'][base_key]['tunnel_name'][key]['tunnel_state']=m15['state']
                continue
	
            ###Name: R3_t100                             (Tunnel100) Destination: 2.2.2.2
            ##Eg:{tunnel100:{destiantion:2.2.2.2}}
            m1=p1.match(line)
            if m1:
                r=m1.groupdict()
                key=r['Tunnel']
                res['tunnel_type'][base_key]['tunnel_name'][key]={}
                res['tunnel_type'][base_key]['tunnel_name'][key]['destination']=r['destination']
                continue

            ####path option 1, type explicit R3_R4_R5_R2 (Basis for Setup, path weight 3)
	        ##'path_option': {'1': {'type': 'explicit','path_name':'R3_R4_R5_R2', 'path_weight': 3}} 
            m3=p3.match(line)
            if m3:
                fin=m3.groupdict()
                path_option="path_option"
                if result==1:
                    res['tunnel_type'][base_key]['tunnel_name'][key][key1][path_option]={}
                    result=0
                for item,value in fin.items():
                    if item=="path_option":
                        path=value
                        res['tunnel_type'][base_key]['tunnel_name'][key][key1][path_option][path]={}
                    else:
                        if item=="type":
                            s=value.split()
                            res['tunnel_type'][base_key]['tunnel_name'][key][key1][path_option][path]['type']=s[0].strip()
                            if s[0]!="dynamic":
                                res['tunnel_type'][base_key]['tunnel_name'][key][key1][path_option][path]['path_name']=s[1].strip()
                        elif item == "lockdown":
                            if fin["lockdown"]:
                                res['tunnel_type'][base_key]['tunnel_name'][key][key1][path_option][path]['lockdown']=True
                        else:
                            if value:
                                res['tunnel_type'][base_key]['tunnel_name'][key][key1][path_option][path][item]=int(value)
                   
                continue
				
            ###Path-option attribute: TU1_attrib
            m3_1=p3_1.match(line)
            if m3_1:
                grp=m3_1.groupdict()
                for item,value in grp.items():
                    res['tunnel_type'][base_key]['tunnel_name'][key][key1][path_option][path][item]=value
                    
            ###Src 3.3.3.3, Dst 2.2.2.2, Tun_Id 100, Tun_Instance 28
            ##Eg:{'src': '3.3.3.3', 'dst': '2.2.2.2', 'tun_id': 100, 'tun_instance': 28}
            m4=p4.match(line)
            if m4:
                a=line.split(",")
                for i in a:
                    i=i.strip()
                    j=i.split(" ")[1]
                    res['tunnel_type'][base_key]['tunnel_name'][key][key1][i.split(" ")[0].lower().strip()]=\
                                            int(j) if j.isdigit() else j
                continue

            ###State: explicit path option 1 is active
            m12=p12.match(line)
            if m12:
                res['tunnel_type'][base_key]['tunnel_name'][key][key1]['state']={}
                res['tunnel_type'][base_key]['tunnel_name'][key][key1]['state']['active_path']=\
                            re.findall(r"(\d+)",line.split(":")[1].strip())[0]
                res['tunnel_type'][base_key]['tunnel_name'][key][key1]['state']['path_type']=\
                            line.split(":")[1].split()[0]  
                continue
				
            ###Time since created: 14 minutes, 44 seconds
            m5=p5.match(line)
            if m5:
                time=line.split(":")[0].lower().strip().replace(" ","_")
                res['tunnel_type'][base_key]['tunnel_name'][key][key1]['tunnel'][time]=line.split(":")[1].strip()
                continue	

            ###Bandwidth: 500      kbps (Global)  Priority: 7  7   Affinity: 0x0/0xFFFF
            m6= p6.match(line)
            if m6:
                result=1
                r4=m6.groupdict()
                for item,value in r4.items():
                    if item == "priority":
                        res['tunnel_type'][base_key]['tunnel_name'][key][key1]['priority']={}
                        tg=value.split()
                        res['tunnel_type'][base_key]['tunnel_name'][key][key1]['priority']['setup_priority']=int(tg[0])
                        res['tunnel_type'][base_key]['tunnel_name'][key][key1]['priority']['hold_priority']=int(tg[1])
                    elif item == "bandwidth":
                        bandwidth_detail=value.split()
                        res['tunnel_type'][base_key]['tunnel_name'][key][key1][item]=int(bandwidth_detail[0])
                        res['tunnel_type'][base_key]['tunnel_name'][key][key1]["bandwidth_unit"]=bandwidth_detail[1]
                        res['tunnel_type'][base_key]['tunnel_name'][key][key1]["bandwidth_type"]=\
                                            re.sub(r"[()]","",bandwidth_detail[2])
                    else:
                        res['tunnel_type'][base_key]['tunnel_name'][key][key1][item]=value.strip()
                continue
				
            ###Match InLabel : -
            m7 = p7.match(line)
            if m7:
                r5=m7.group()
                res['tunnel_type'][base_key]['tunnel_name'][key][r5.split(":")[0].strip().lower().\
                                    replace(" ","_")]=list(map(str.strip,r5.split(":")[1].strip().split(",")))
                continue

            ###AutoRoute: enabled  LockDown: disabled Loadshare: 500 [4000000] bw-based
            m8=p8.match(line)
            if m8:
                r6=m8.groupdict()
                for item,value in r6.items():
                    res['tunnel_type'][base_key]['tunnel_name'][key][key1][item.strip()]=\
                                    int(value) if value.strip().isdecimal() else value
                continue
                
            ###Record   Route:   NONE
            ###Tspec: ave rate=500 kbits, burst=1000 bytes, peak rate=500 kbits
            m9=p9.match(line)
            if m9:
                if "=" not in line:
                    res['tunnel_type'][base_key]['tunnel_name'][key][key1][key3]["record_route"]=\
                                    line.split(":")[1].strip()
                else:
                    r7=m9.group()
                    key4=r7.split(":")[0].strip().lower()
                    res['tunnel_type'][base_key]['tunnel_name'][key][key1][key3][key4]={}
                    r8=r7.split(":")[1].split(",")
                    for i in r8:
                        res10=i.split("=")[1].split()
                        item=i.split("=")[0].lower().strip().replace(" ","_")
                        res['tunnel_type'][base_key]['tunnel_name'][key][key1][key3][key4][item]=int(res10[0])
                        res['tunnel_type'][base_key]['tunnel_name'][key][key1][key3][key4][item+"_unit"]=res10[1]                
                        continue           

                
            ###Global: not set   Tunnel Specific: not set   Effective: min-fill (default) 
            ###Make global part of path_selection_tiebreaker
            m22=p22.match(line)
            if m22:
                re22=m22.groupdict()        
                for item,value in re22.items():
                    res['tunnel_type'][base_key]['tunnel_name'][key]['config_parameters']["path_selection_tiebreaker"][item.split(":")[0].strip().replace(" ","_").lower()]=\
                    value.strip()
                continue
                
            ##Path Weight: 1 (TE)
            m23=p23.match(line)
            if m23:
                re23=m23.groupdict()        
                for item,value in re23.items():
                    res['tunnel_type'][base_key]['tunnel_name'][key][key1][item]=value.strip()
                continue
                
            ###Make explicit route as part of rsvp_path_info or shortest_unconstrained_path_info respectively
            ###Make my address as part of rsvp_path_info
            ###My Address: 192.1.1.1
            ###Explicit Route: 192.1.1.2 2.2.2.2
            if re.match("^Explicit Route:|My",line):
                if "Explicit Route:" in line:
                    explicit_route=[]
                    explicit_route.extend(line.split(":")[1].split())
                        
                    if key1=="rsvp_signalling_info": 
                       res['tunnel_type'][base_key]['tunnel_name'][key][key1]['rsvp_path_info']\
                               ['explicit_route']=explicit_route
                    elif key1=="shortest_unconstrained_path_info":
                        res['tunnel_type'][base_key]['tunnel_name'][key][key1]['explicit_route']=explicit_route
                else:
                    res['tunnel_type'][base_key]['tunnel_name'][key][key1]['rsvp_path_info']\
                    [line.split(":")[0].strip().lower().replace(" ","_")]=line.split(":")[1].\
                                                                            lower().strip()
                continue      

            ##  Node Hop Count: 1
            if "Node Hop Count:" in line:
                ib=int(line.split(":")[1].lower().strip())
                res['tunnel_type'][base_key]['tunnel_name'][key][line.split(":")[0].strip().lower().replace(" ","_")]=ib
                continue             
                
            ###Fault-OAM: disabled, Wrap-Protection: disabled, Wrap-Capable: No
            ###Hop Limit: disabled
            ###Cost Limit: disabled
            ###BandwidthOverride: disabled  LockDown: enabled   Verbatim: disabled
            ###auto-bw: disabled
            m10=p10.match(line)
            if m10:
                 line=re.sub(r'\:\s{2,}',": ",line.strip())
                 re9 = re.split("\s{2,}|,",line.strip())
                 for i in re9:
                        ib=i.split(":")[1].strip().replace("[ignore","" ).strip()
                        res['tunnel_type'][base_key]['tunnel_name'][key][key1][i.split(":")[0].strip()\
                            .lower().replace(" ","_").replace("-","_").strip()]=\
                            int(ib) if ib.isdecimal() else ib
                 continue                

            #Explicit Route: 193.1.1.2 196.1.1.2 196.1.1.1 198.1.1.1
            #198.1.1.2 2.2.2.2
            if p11.match(line):
                explicit_route.extend(line.split())

            ###Admin: up         Oper: up     Path: valid       Signalling: connected
            if "Admin:" in line:
                m13 = p13.findall(line)
                if m13:
                    line=re.sub(r'\:\s{1,}',":",line.strip())
                    for match in m13:
                        res['tunnel_type'][base_key]['tunnel_name'][key][key1][match[0].strip().lower()]=\
                                        match[1].strip().lower()
                continue 

            ##Path-invalidation timeout: 10000 msec (default), Action: Tear
            m14=p14.match(line)
            if m14:
                re14=m14.groupdict()        
                for item,value in re14.items():
                    res['tunnel_type'][base_key]['tunnel_name'][key][key1][item]=\
                                    int(value) if value.isdecimal() else value
                continue
                
            ###Number of LSP IDs (Tun_Instances) used: 19
            m16=p16.match(line)
            if m16:
                res['tunnel_type'][base_key]['tunnel_name'][key][key1]['tunnel']["number_of_lsp_ids_used"]=int(line.split(":")[1])
                continue

            ###Current LSP: [ID: 19]
            m17=p17.match(line)
            if m17:  
                id=m17.groupdict()             
                res['tunnel_type'][base_key]['tunnel_name'][key][key1]['current_lsp_id']={}
                res['tunnel_type'][base_key]['tunnel_name'][key][key1]['current_lsp_id'][id['id']]={}
                continue
                
            ###Uptime: 9 hours, 52 minutes
            ###Selection: reoptimization
            m18=p18.match(line)
            if m18:  
                res18 = p18.findall(line)
                res['tunnel_type'][base_key]['tunnel_name'][key][key1]['current_lsp_id'][id['id']][res18[0][0].lower()]=res18[0][1]
                continue     
                
            #Metric Type: TE (default)
            m19=p19.match(line)
            if m19:
                res19=m19.groupdict()    
                res['tunnel_type'][base_key]['tunnel_name'][key]["config_parameters"]['metric_used']=res19['metric_used']
                if res19.get("metric_type",None):
                    res['tunnel_type'][base_key]['tunnel_name'][key]['config_parameters']['metric_type']=res19['metric_type']
                continue
                
            ###Prior LSP: [ID: 19]
            m20=p20.match(line)
            if m20:  
                id=m20.groupdict()             
                res['tunnel_type'][base_key]['tunnel_name'][key][key1]['prior_lsp_id']={}
                res['tunnel_type'][base_key]['tunnel_name'][key][key1]['prior_lsp_id'][id['id']]={}
                continue

            ###ID: path option 3 [35]
            ###Removal Trigger: tunnel shutdown
            ###Last Error: CTRL:: Explicit path has unknown address, 194.1.1.1
            m21=p21.match(line)
            if m21:  
                res21 = p21.findall(line)
                for prior_key,prior_value in res21:
                    res['tunnel_type'][base_key]['tunnel_name'][key][key1]['prior_lsp_id'][id['id']][prior_key.lower().replace(" ","_")]=prior_value
                continue                   

        return res
