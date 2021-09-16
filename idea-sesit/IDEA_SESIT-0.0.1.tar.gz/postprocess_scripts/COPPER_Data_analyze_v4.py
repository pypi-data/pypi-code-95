######## Crest Results analayze ########
import pandas as pd
import numpy as np
import os
import csv
import gc

#Initializing all sets

##we can skip runnig some days using smaple_rat, for example if sample_rate=3 it will run days 1,4,7,10,... 
sample_rate=5
# number of days that we want run
rundaynum=365
cap_cost_alter=(365/rundaynum)*sample_rate
runhours=rundaynum*24
foryear=2050
refyear=2018
#carbon tax in dollars per tonne co2
ctax=0
recon=True

yearhours=pd.read_csv(r'hours.csv',header=None)
h=list(yearhours.iloc[:,0])
del h[runhours:]
hours=len(h)


max_cap_fact={'gas':0.8, 'peaker': .3, 'nuclear': 0.95, 'coal': 0.9, 'diesel': 0.95, 'waste': 0.9} #annual maximum capacity factor
min_cap_fact={'gas': 0.2, 'peaker': .02, 'nuclear': 0.75,  'coal': 0.5, 'diesel': 0.05, 'waste': 0.2} #annual minimum capacity factor
ap=["British Columbia", "Alberta",  "Saskatchewan", "Manitoba", "Ontario","Quebec", "New Brunswick", "Newfoundland and Labrador",  "Nova Scotia","Prince Edward Island"] #all provinces
ramp_rate_percent={'gas': 0.1, 'peaker':0.1 , 'nuclear': 0.05,  'coal': 0.05, 'diesel': 0.1, 'waste': 0.05} #ramp rate in percent of capacity per hour

aba=["British Columbia.a", "Alberta.a",  "Saskatchewan.a", "Manitoba.a", "Ontario.a","Ontario.b","Quebec.a","Quebec.b", "New Brunswick.a", "Newfoundland and Labrador.a","Newfoundland and Labrador.b",  "Nova Scotia.a","Prince Edward Island.a"] #all possible balancing areas

###Just for creatin input files####
aba1=['a','b']

#storecost=287165/cap_cost_alter
trans_o_m=10860/cap_cost_alter
transcost=184/cap_cost_alter
GJtoMWh=3.6
#fixed_o_m={'gas': 7480, 'peaker': 19181, 'coal': 76723, 'nuclear': 172626, 'hydro': 18797, 'wind': 47952, 'solar': 14705, 'diesel': 19181, 'waste': 100000}
fixedom=pd.read_csv(r'fixed_o_m.csv',header=None)
fixed_o_m=dict(fixedom.values) 
for k in fixed_o_m:
    fixed_o_m[k]=fixed_o_m[k]/cap_cost_alter
    
#variable_o_m={'gas': 3.52, 'peaker': 7.8, 'coal': 4.48, 'nuclear': .8, 'hydro': 3.35, 'wind': 0, 'solar': 0, 'diesel': 19.181, 'waste': 100}
variableom=pd.read_csv(r'variables_o_m.csv',header=None)
variable_o_m=dict(variableom.values)


#store_fix_o_m=18000/cap_cost_alter
pump_hydro_efficiency=0.75
#hl=[1] #hydro generation locations

merrawindsetall=pd.read_csv(r'merra_wind_set_all.csv',header=None)
wl=list(merrawindsetall.iloc[:,0])

allsolarlocations=pd.read_csv(r'all_solar_locations.csv',header=None)
sl=list(allsolarlocations.iloc[:,0])

gridlocations=pd.read_csv(r'grid_locations.csv',header=None)
gl=list(gridlocations.iloc[:,0])


allplants=[ 'gas', 'peaker', 'coal', 'nuclear', 'hydro', 'wind', 'solar', 'waste', 'diesel'] #all types of generator
tplants=['gas', 'peaker', 'coal', 'nuclear', 'waste', 'diesel'] #thermal plants

#fuelprice={'gas':4.91,'nuclear':1,'peaker': 4.91, 'coal': 1.8, 'diesel': 25.8, 'waste': 0}
fuel_price=pd.read_csv(r'fuelprice.csv',header=None)
fuelprice=dict(fuel_price.values) 


capital_cost=pd.read_csv(r'capitalcost.csv',header=None)
capitalcost=dict(capital_cost.values) 
#capitalcost={'gas': 178355, 'nuclear':998801, 'peaker': 139582, 'coal': 440647, 'diesel': 95474, 'waste': 1000000}

for k in capitalcost:
    capitalcost[k]=capitalcost[k]/cap_cost_alter

windcapcost=capitalcost['wind']      #193864/cap_cost_alter
solarcapitalcost=capitalcost['solar']   #205635/cap_cost_alter

distancetogrid=pd.read_csv(r'distance_to_grid.csv',header=None)
distance_to_grid=dict(distancetogrid.values)
intra_ba_transcost=557/cap_cost_alter
windtransmission=dict()
windcost=dict()
solarcost=dict()
for GL in gl:
    windtransmission[GL]=distance_to_grid[GL]*intra_ba_transcost
    windcost[GL]=windcapcost+windtransmission[GL]
    solarcost[GL] = solarcapitalcost + distance_to_grid[GL]*intra_ba_transcost
    
    
efficiency={'gas': 0.509, 'peaker': 0.28, 'nuclear': 0.327, 'coal': 0.39, 'diesel': 0.39, 'waste': 0.39}
fuel_co2={'gas': .051, 'peaker': .051, 'nuclear': 0, 'coal': .090, 'diesel': .072, 'waste': 0}
#reference case carbon emissions in electricity sector in 2025 in Mt by province
carbon_2025_ref={"British Columbia" :4.01, "Alberta" :60.9,  "Saskatchewan" :11.27, "Manitoba" :.28, "Ontario" :14.10, "Quebec" :2.28, "New Brunswick" :4, "Newfoundland and Labrador" :0,  "Nova Scotia" :5,"Prince Edward Island" :0}
#share carbon reduced
carbon_reduction=0

#maximum carbon emissions in forecast year in Mt
carbon_limit=dict()
for AP in ap:
    carbon_limit[AP]=carbon_2025_ref[AP]*(1-carbon_reduction)

fuelcost=dict()
#thermal plant co2 emissions in kg per MWh of electricity generated
carbondioxide=dict()
for TP in tplants:
    fuelcost[TP] = (fuelprice[TP] + ctax*fuel_co2[TP])/ efficiency[TP]
    carbondioxide[TP]=fuel_co2[TP]*GJtoMWh/efficiency[TP]

demandnodes=pd.read_csv(r'population_locations.csv',header=None) #import demand nodes file
n=list(demandnodes.iloc[:,0]) #demand nodes

allnodes=['all'] #dummy for all nodes

demeqsup=pd.read_csv(r'ba_set.csv',header=None)
ba=list(demeqsup.iloc[:,0])        #balancing areas where supply equals demand
del demeqsup

gltoba=pd.read_csv(r'map_gl_to_ba.csv',header=None)
map_gl_to_ba=dict(gltoba.values)        #map grid locations to balancing areas
del gltoba

gltopr=pd.read_csv(r'map_gl_to_pr.csv',header=None)
map_gl_to_pr=dict(gltopr.values)        #map grid locations to provinces
del gltopr

transmapba=pd.read_csv(r'transmission_map_ba.csv',header=None)
transmap=list(transmapba.iloc[:,0])        #map grid locations to provinces
del transmapba

transmapdis = pd.read_csv(r'transmission_map_distance.csv',header=None)
distance=dict(transmapdis.values)
del transmapdis

#extantgen = pd.read_csv(r'extant_generation_noSiteC.csv',header=None)
#extant_generation=dict(extantgen.values)
#del extantgen

extantwindsolar = pd.read_csv(r'wind_solar_extant2030.csv',header=None)
extant_wind_solar=dict(extantwindsolar.values)
del extantwindsolar

extantcapacity = pd.read_csv(r'extant_capacity.csv',header=0)
extant_capacity=dict(zip(list(extantcapacity.iloc[:]['ABA']),list(extantcapacity.iloc[:][str(foryear)])))
del extantcapacity

extanttrans = pd.read_csv(r'extant_transmission.csv',header=0)
extant_transmission=dict(zip(list(extanttrans.iloc[:]['ABA']),list(extanttrans.iloc[:][str(foryear)])))
del extanttrans

hydrocf = pd.read_csv(r'hydro_cf.csv',header=None)
hydro_cf=dict(hydrocf.values)
del hydrocf

demandgrowth = pd.read_csv(r'annual_growth.csv',header=0)
demand_growth=dict(zip(list(demandgrowth.iloc[:]['AP']),list(demandgrowth.iloc[:][str(foryear)])))
del demandgrowth

demandall = pd.read_csv(r'demand.csv',header=None)
demand_all=dict(demandall.values)
del demandall

population1 = pd.read_csv(r'population.csv',header=None)
population=dict(population1.values)
del population1

demandus = pd.read_csv(r'us_demand.csv',header=None)
demand_us=dict(demandus.values)
del demandus

maphd = pd.read_csv(r'set_map_days_to_hours.csv',header=None)
map_hd=dict(maphd.values)
del maphd

maphm = pd.read_csv(r'set_map_months_to_hours.csv',header=None)
map_hm=dict(maphm.values)
del maphm

nummonths=map_hm[runhours]
m=list(range(1,nummonths+1))

surfacearea = pd.read_csv(r'surface_area.csv',header=None)
surface_area=dict(surfacearea.values)
del surfacearea

demand13to18 = pd.read_csv(r'growth_2013_2018.csv',header=None)
demand_13_to_18=dict(demand13to18.values)
del demand13to18
#wind_cf = pd.read_csv(r'windcf.csv',header=None)
#windcf=dict(wind_cf.values)

#solar_cf = pd.read_csv(r'solarcf.csv',header=None)
#solarcf=dict(solar_cf.values)

#with open('windcf.csv') as csv_file:
#    reader = csv.reader(csv_file)
#    windcf = dict(reader)
#
#for k in windcf:
#    windcf[k]=float(windcf[k])
#
#with open('solarcf.csv') as csv_file:
#    reader = csv.reader(csv_file)
#    solarcf = dict(reader)
#
#for k in solarcf:
#    solarcf[k]=float(solarcf[k])
#windspeed = pd.read_csv(r'merra_wind_all.csv',header=0)
#
#solarcddata = pd.read_csv(r'solar_all.csv',header=0)

## according to the sample_rate these lines remove the days that we don't want to run
rundays=list(range(1,rundaynum+1,sample_rate))
d=list(rundays)
h3=list(h)
for H in h3:
    if map_hd[H] not in rundays:
        h.remove(H)
#        if H in h2:
#            h2.remove(H)
del h3
hours=len(h)
h2=list(h)
del h2[hours-1]


##calculte the diffrence between to hours in a row
time_diff=dict()
for I in list(range(len(h)-1)):
    time_diff[h[I]]=h[I+1]-h[I]



gl2=list(gl)
for GL in gl2:
    if map_gl_to_pr[GL] not in ap:
        gl.remove(GL)
#windcf=dict()
#solarcf=dict()
#for H in h:
#    for GL in gl:
#        windcf[str(H)+'.'+str(GL)]=0.7
#        solarcf[str(H)+'.'+str(GL)]=solarcddata.iloc[int(H)-1][int(GL)-1]
        
        
maxwindperkmsq=2
maxsolarperkmsq=31.28
maxwind=dict()
maxsolar=dict()
for GL in gl:
    maxwind[GL]=surface_area[GL]*maxwindperkmsq
    maxsolar[GL]=surface_area[GL]*maxsolarperkmsq

pump_hours=8;
#pump_hydro_capacity={'1508':174}
ba_pump_hydro_capacity=dict()
for ABA in aba:
    ba_pump_hydro_capacity[ABA]=0
ba_pump_hydro_capacity['Ontario.a']=174

translossfixed=0.02
translossperkm=0.00003
transloss=dict()
for ABA in aba:
    for ABBA in aba:
        if ABA+'.'+ABBA in distance:
            transloss[ABA+'.'+ABBA]=distance[ABA+'.'+ABBA]*translossperkm+translossfixed



for AP in ap:
    for H in h:
        demand_all[AP+'.'+str(H)]=demand_all[AP+'.'+str(H)]*(1+demand_13_to_18[AP])
        demand_all[AP+'.'+str(H)]=demand_all[AP+'.'+str(H)]*(1+demand_growth[AP])**(foryear-refyear)

populationaba=dict()
for ABA in aba:
    populationaba[ABA]=0
for ABA in aba:
    for GL in population:
        if map_gl_to_ba[GL]==ABA:
                populationaba[ABA]=populationaba[ABA]+population[GL]
populationap=dict()
demand=dict()


for AP in ap:
    populationap[AP]=sum(populationaba[ABA] for ABA in aba if AP in ABA)
for ABA in aba:
    pvba=ABA.replace('.a','')
    pvba=pvba.replace('.b','')
    for H in h:
        demand[ABA+'.'+str(H)]=demand_all[pvba+'.'+str(H)]*(populationaba[ABA]/populationap[pvba])

    

extant_thermal=dict()
for AP in ap:
    for ABA in aba1:
        for TP in tplants:
            extant_thermal[AP+'.'+ABA+'.'+TP]=0
            if AP+'.'+ABA+'.'+TP in extant_capacity:
                extant_thermal[AP+'.'+ABA+'.'+TP]=extant_capacity[AP+'.'+ABA+'.'+TP]
#for GL in gl:
#    for TP in tplants:
#        for EXG in extant_generation:
#            if EXG==str(GL)+'.'+TP:
#                if map_gl_to_ba[GL]+'.'+TP in extant_thermal:
#                    extant_thermal[map_gl_to_ba[GL]+'.'+TP]+=extant_generation[EXG]


hydro_capacity=dict()
extant_wind_gen=dict()
extant_solar_gen=dict()
for AP in ap:
    for ABA in aba1:
#        hydro_capacity[AP+'.'+ABA+'.'+'hydro']=0
        for H in h:
            extant_wind_gen[AP+'.'+ABA+'.'+str(H)]=0
            extant_solar_gen[AP+'.'+ABA+'.'+str(H)]=0

#CALCULATE OUTPUT POWER FOR EXTANT WIND FARM AND SOLAR POWER PLANTS            
#for GL in gl:
#    for EXG in extant_wind_solar:
#        if foryear!=2050:
##            if EXG==str(GL)+'.'+'hydro':
##                hydro_capacity[map_gl_to_ba[GL]+'.'+'hydro']+=extant_generation[EXG]
#            if EXG==str(GL)+'.'+'wind':
#                for H in h:
#                    extant_wind_gen[map_gl_to_ba[GL]+'.'+str(H)]+=(extant_wind_solar[EXG]*windcf[str(H)+'.'+str(GL)])
#            if EXG==str(GL)+'.'+'solar':
#                for H in h:
#                    extant_solar_gen[map_gl_to_ba[GL]+'.'+str(H)]+=(extant_wind_solar[EXG]*solarcf[str(H)+'.'+str(GL)])


## calculate hydro historic for different type of hydro power plant
#ror_share=0.3
#intraday_share=0.5
hydro_minflow=0.1
#;hydro=dict()
ror_hydroout=dict()
day_hydroout=dict()
month_hydroout=dict()
day_hydro_historic=dict()
month_hydro_historic=dict()
ror_hydro_capacity=dict()
day_hydro_capacity=dict()
month_hydro_capacity=dict()
day_minflow=dict()
month_minflow=dict()
for AP in ap:
   for ABA in aba1:
       ror_hydro_capacity[AP+'.'+ABA] = 0
       day_hydro_capacity[AP+'.'+ABA] = 0
       month_hydro_capacity[AP+'.'+ABA] = 0
       if AP+'.'+ABA+'.'+'hydro_run' in extant_capacity:
           ror_hydro_capacity[AP+'.'+ABA] = extant_capacity[AP+'.'+ABA+'.'+'hydro_run']
           day_hydro_capacity[AP+'.'+ABA] = extant_capacity[AP+'.'+ABA+'.'+'hydro_daily']
           month_hydro_capacity[AP+'.'+ABA] = extant_capacity[AP+'.'+ABA+'.'+'hydro_monthly']
       day_minflow[AP+'.'+ABA]=day_hydro_capacity[AP+'.'+ABA]*hydro_minflow
       month_minflow[AP+'.'+ABA]=month_hydro_capacity[AP+'.'+ABA]*hydro_minflow
       for D in d:
           day_hydro_historic[str(D)+'.'+AP+'.'+ABA]=0
           
       for M in m:
           month_hydro_historic[str(M)+'.'+AP+'.'+ABA]=0
       for H in h:
           
#            hydro[str(H)+'.'+AP+'.'+ABA]=0
#            if AP+'.'+str(H) in hydro_cf:
#                hydro[str(H)+'.'+AP+'.'+ABA]=hydro_cf[AP+'.'+str(H)]*hydro_capacity[AP+'.'+ABA+'.'+'hydro']
         if AP+'.'+str(H) in hydro_cf:
              ror_hydroout[str(H)+'.'+AP+'.'+ABA]=ror_hydro_capacity[AP+'.'+ABA]*hydro_cf[AP+'.'+str(H)]
              day_hydroout[str(H)+'.'+AP+'.'+ABA] = day_hydro_capacity[AP+'.'+ABA]*hydro_cf[AP+'.'+str(H)]
              month_hydroout[str(H)+'.'+AP+'.'+ABA] = month_hydro_capacity[AP+'.'+ABA]*hydro_cf[AP+'.'+str(H)]
         else:
              ror_hydroout[str(H)+'.'+AP+'.'+ABA]=0
              day_hydroout[str(H)+'.'+AP+'.'+ABA] =0
              month_hydroout[str(H)+'.'+AP+'.'+ABA] =0
            
       
         day_hydro_historic[str(map_hd[H])+'.'+AP+'.'+ABA]=day_hydro_historic[str(map_hd[H])+'.'+AP+'.'+ABA]+day_hydroout[str(H)+'.'+AP+'.'+ABA]
         month_hydro_historic[str(map_hm[H])+'.'+AP+'.'+ABA]=month_hydro_historic[str(map_hm[H])+'.'+AP+'.'+ABA]+month_hydroout[str(H)+'.'+AP+'.'+ABA]
            


## hydro renewal and greenfield necessary inputs
if recon:
    hydro_new = pd.read_excel (r'hydro_new_recon.xlsx',header=0 ,error_bad_lines=False)
else:
    hydro_new = pd.read_excel (r'hydro_new.xlsx',header=0 ,error_bad_lines=False)      

hydro_renewal=list(hydro_new.iloc[:]['Short Name'])
cost_renewal=dict(zip(hydro_renewal,list(hydro_new.iloc[:]['Annualized Capital Cost ($M/year)'])))
capacity_renewal=dict(zip(hydro_renewal,list(hydro_new.iloc[:]['Additional Capacity (MW)'])))
devperiod_renewal=dict(zip(hydro_renewal,list(hydro_new.iloc[:]['Development Time (years)'])))
location_renewal=dict(zip(hydro_renewal,list(hydro_new.iloc[:]['Balancing Area'])))
distance_renewal=dict(zip(hydro_renewal,list(hydro_new.iloc[:]['Distance to Grid (km)'])))
type_renewal=dict(zip(hydro_renewal,list(hydro_new.iloc[:]['Type'])))
fixed_o_m_renewal=dict(zip(hydro_renewal,list(hydro_new.iloc[:]['Fixed O&M ($/MW-year)'])))
variable_o_m_renewal=dict(zip(hydro_renewal,list(hydro_new.iloc[:]['Variable O&M ($/MWh)'])))

hr_ror=list()
cost_ror_renewal=dict()
capacity_ror_renewal=dict()
hr_ror_location=dict()

hr_day=list()
cost_day_renewal=dict()
capacity_day_renewal=dict()
hr_day_location=dict()

hr_mo=list()
cost_month_renewal=dict()
capacity_month_renewal=dict()
hr_month_location=dict()

hr_pump=list()
cost_pump_renewal=dict()
capacity_pump_renewal=dict()
hr_pump_location=dict()
for k in hydro_renewal:
    if foryear-2020>=devperiod_renewal[k]:
        if type_renewal[k]=='hydro_run':
            hr_ror.append(k)
            cost_ror_renewal[k]=cost_renewal[k]*1000000+distance_renewal[k]*intra_ba_transcost*capacity_renewal[k]
            capacity_ror_renewal[k]=capacity_renewal[k]
            hr_ror_location[k]=location_renewal[k]

        if type_renewal[k]=='hydro_daily':
            hr_day.append(k)
            cost_day_renewal[k]=cost_renewal[k]*1000000+distance_renewal[k]*intra_ba_transcost*capacity_renewal[k]
            capacity_day_renewal[k]=capacity_renewal[k]
            hr_day_location[k]=location_renewal[k]

        if type_renewal[k]=='hydro_monthly':
            hr_mo.append(k)
            cost_month_renewal[k]=cost_renewal[k]*1000000+distance_renewal[k]*intra_ba_transcost*capacity_renewal[k]
            capacity_month_renewal[k]=capacity_renewal[k]
            hr_month_location[k]=location_renewal[k]
        if type_renewal[k]=='hydro_pump':
            hr_pump.append(k)
            cost_pump_renewal[k]=cost_renewal[k]*1000000+distance_renewal[k]*intra_ba_transcost*capacity_renewal[k]
            capacity_pump_renewal[k]=capacity_renewal[k]
            hr_pump_location[k]=location_renewal[k]


              
           
ror_renewalout=dict()
for HR_ROR in hr_ror:
    for H in h:
        province_loc=hr_ror_location[HR_ROR].replace('.a','')
        province_loc=province_loc.replace('.b','')
        ror_renewalout[str(H)+'.'+HR_ROR]=capacity_ror_renewal[HR_ROR]*hydro_cf[province_loc+'.'+str(H)]

for k in cost_ror_renewal:
    cost_ror_renewal[k]=cost_ror_renewal[k]/cap_cost_alter        
        

day_renewal_historic=dict()
day_renewalout=dict()
for HR_DAY in hr_day:
    for D in d:
        day_renewal_historic[str(D)+'.'+HR_DAY]=0 
    for H in h:
        province_loc=hr_day_location[HR_DAY].replace('.a','')
        province_loc=province_loc.replace('.b','')
        day_renewalout[str(H)+'.'+HR_DAY]=capacity_day_renewal[HR_DAY]*hydro_cf[province_loc+'.'+str(H)]
        day_renewal_historic[str(map_hd[H])+'.'+HR_DAY]=day_renewal_historic[str(map_hd[H])+'.'+HR_DAY]+day_renewalout[str(H)+'.'+HR_DAY]

for k in cost_day_renewal:
    cost_day_renewal[k]=cost_day_renewal[k]/cap_cost_alter


month_renewal_historic=dict()
month_renewalout=dict()
for HR_MO in hr_mo:
    for M in m:
        month_renewal_historic[str(M)+'.'+HR_MO]=0
    for H in h:
        province_loc=hr_month_location[HR_MO].replace('.a','')
        province_loc=province_loc.replace('.b','')
        month_renewalout[str(H)+'.'+HR_MO]=capacity_month_renewal[HR_MO]*hydro_cf[province_loc+'.'+str(H)]
        month_renewal_historic[str(map_hm[H])+'.'+HR_MO]=month_renewal_historic[str(map_hm[H])+'.'+HR_MO]+month_renewalout[str(H)+'.'+HR_MO]

for k in cost_month_renewal:
    cost_month_renewal[k]=cost_month_renewal[k]/cap_cost_alter


for k in cost_pump_renewal:
    cost_pump_renewal[k]=cost_pump_renewal[k]/cap_cost_alter
    
#####recontract input data ###########33

windcost_recon=118662.7485/cap_cost_alter
solarcost_recon=94204.76075/cap_cost_alter
#column_name_loc=str(foryear)+'_ended'
#column_name_cap=str(foryear)+'_ended_cap'
windsolarrecon = pd.read_csv(r'wind_solar_location_recon.csv',header=0)
wind_solar_recon_2030=dict(zip(list(windsolarrecon.iloc[:]['2030_ended']),list(windsolarrecon.iloc[:]['2030_ended_cap'])))
wind_solar_recon_2050=dict(zip(list(windsolarrecon.iloc[:]['2050_ended']),list(windsolarrecon.iloc[:]['2050_ended_cap'])))

wind_recon_capacity=dict()
solar_recon_capacity=dict()
for GL in gl:
    wind_recon_capacity[GL]=0
    solar_recon_capacity[GL]=0
    if foryear==2030:
        if str(GL)+'.'+'wind' in wind_solar_recon_2030:
            wind_recon_capacity[GL]=wind_solar_recon_2030[str(GL)+'.'+'wind']
        if str(GL)+'.'+'solar' in wind_solar_recon_2030:
            solar_recon_capacity[GL]=wind_solar_recon_2030[str(GL)+'.'+'solar']
    
    if foryear==2050:
        if str(GL)+'.'+'wind' in wind_solar_recon_2030:
            wind_recon_capacity[GL]=wind_solar_recon_2030[str(GL)+'.'+'wind']
            if str(GL)+'.'+'wind' in wind_solar_recon_2050:
                wind_recon_capacity[GL]=wind_recon_capacity[GL]+wind_solar_recon_2050[str(GL)+'.'+'wind']
        elif str(GL)+'.'+'wind' in wind_solar_recon_2050:
            wind_recon_capacity[GL]=wind_solar_recon_2050[str(GL)+'.'+'wind']
        
        if str(GL)+'.'+'solar' in wind_solar_recon_2030:
            solar_recon_capacity[GL]=wind_solar_recon_2030[str(GL)+'.'+'solar']
            if str(GL)+'.'+'solar' in wind_solar_recon_2050:
                solar_recon_capacity[GL]=solar_recon_capacity[GL]+wind_solar_recon_2050[str(GL)+'.'+'solar']
        elif str(GL)+'.'+'solar' in wind_solar_recon_2050:
            solar_recon_capacity[GL]=wind_solar_recon_2050[str(GL)+'.'+'solar']


cleared_data=gc.collect()
######### Doublicate some sets ###############
ttplants=tplants
nn=n
ggl=gl
hh=h
app=ap
abba=aba


############# Analyze the results ##################
coordinate = pd.read_excel (r'coordinate.xlsx')

cwd=os.getcwd()
if recon:
    folder_name='outputs'+'_fy'+str(foryear)+'_ct'+str(ctax)+'_rd'+str(rundaynum)+'_sr'+str(sample_rate)+'_recon'
else:
    folder_name='outputs'+'_fy'+str(foryear)+'_ct'+str(ctax)+'_rd'+str(rundaynum)+'_sr'+str(sample_rate)

os.chdir(folder_name)


capacity_thermal=pd.read_csv(r'capacity_thermal.csv', header=None)

retire_thermal =pd.read_csv(r'retire_thermal.csv', header=None)

capacity_wind =pd.read_csv(r'capacity_wind.csv', header=None)

capacity_solar = pd.read_csv(r'capacity_solar.csv', header=None)

supply =pd.read_csv(r'supply.csv', header=None)

windout =pd.read_csv(r'windout.csv', header=None)

solarout =pd.read_csv(r'solarout.csv', header=None)

pumpout =pd.read_csv(r'pumpout.csv', header=None)


pumpin =pd.read_csv(r'pumpin.csv', header=None)

pumpenergy =pd.read_csv(r'pumpenergy.csv', header=None)

daystoragehydroout =pd.read_csv(r'daystoragehydroout.csv', header=None)

monthstoragehydroout =pd.read_csv(r'monthstoragehydroout.csv', header=None)

transmission = pd.read_csv(r'transmission.csv', header=None)

capacity_transmission =pd.read_csv(r'capacity_transmission.csv', header=None)

ror_renewal_binary =pd.read_csv(r'ror_renewal_binary.csv', header=None)

day_renewal_binary =pd.read_csv(r'day_renewal_binary.csv', header=None)

month_renewal_binary = pd.read_csv(r'month_renewal_binary.csv', header=None)

pumphydro = pd.read_csv(r'pumphydro.csv', header=None)

dayrenewalout = pd.read_csv(r'dayrenewalout.csv', header=None)

monthrenewalout = pd.read_csv(r'monthrenewalout.csv', header=None)

obj = pd.read_csv(r'obj_value.csv', header=None)

if recon:
    capacity_wind_recon = pd.read_csv(r'capacity_wind_recon.csv',header=None)
    capacity_solar_recon =pd.read_csv(r'capacity_solar_recon.csv', header=None)
    
    
######### Whole country Generation outline ##########
tp_num=len(tplants)
Canada_gen_outline=dict()
capcitytherm=list(capacity_thermal.iloc[:,2])
retiretherm=list(retire_thermal.iloc[:,2])
Total_installed=dict()
Total_retired=dict()
Total_installed_hydro_aba=dict()
Total_recon_installed=dict()
Total_generation_ABA=dict()
Total_installed_ABA=dict()
for ALP in allplants:
    Canada_gen_outline[ALP]=0
    Total_installed[ALP]=0
    if ALP !='wind' and ALP!='solar' and ALP!='hydro':
        Total_retired[ALP]=0
    else:
        Total_recon_installed[ALP]=0
    for ABA in aba:
        Total_generation_ABA[ABA+'.'+ALP]=0
        Total_installed_ABA[ABA+'.'+ALP]=0

        if ALP !='wind' and ALP!='solar' and ALP!='hydro':
            index_aba=aba.index(ABA)
            index_tp=tplants.index(ALP)
            Canada_gen_outline[ALP]=Canada_gen_outline[ALP]+extant_thermal[ABA+'.'+ALP]+capcitytherm[index_aba*tp_num+index_tp]-retiretherm[index_aba*tp_num+index_tp]
            Total_installed[ALP]+=capcitytherm[index_aba*tp_num+index_tp]
            Total_retired[ALP]+=retiretherm[index_aba*tp_num+index_tp]
            Total_generation_ABA[ABA+'.'+ALP]+=extant_thermal[ABA+'.'+ALP]+capcitytherm[index_aba*tp_num+index_tp]-retiretherm[index_aba*tp_num+index_tp]
            Total_installed_ABA[ABA+'.'+ALP]+=capcitytherm[index_aba*tp_num+index_tp]
        elif ALP =='hydro':
            Total_generation_ABA[ABA+'.'+ALP+'.ror']=0
            Total_generation_ABA[ABA+'.'+ALP+'.day']=0
            Total_generation_ABA[ABA+'.'+ALP+'.month']=0
            Total_installed_hydro_aba[ABA+'.ror']=0
            Total_installed_hydro_aba[ABA+'.day']=0
            Total_installed_hydro_aba[ABA+'.month']=0
            Canada_gen_outline[ALP]=Canada_gen_outline[ALP]+ror_hydro_capacity[ABA]+day_hydro_capacity[ABA]+month_hydro_capacity[ABA]
            Total_generation_ABA[ABA+'.'+ALP+'.ror']+=ror_hydro_capacity[ABA]
            Total_generation_ABA[ABA+'.'+ALP+'.day']+=day_hydro_capacity[ABA]
            Total_generation_ABA[ABA+'.'+ALP+'.month']+=month_hydro_capacity[ABA]
            
            for HR_ROR in hr_ror:
                if ABA==location_renewal[HR_ROR]:
                    index_rn=hr_ror.index(HR_ROR)
                    Canada_gen_outline[ALP]=Canada_gen_outline[ALP]+ror_renewal_binary.iloc[index_rn][1]*capacity_renewal[HR_ROR]
                    Total_installed[ALP]+=ror_renewal_binary.iloc[index_rn][1]*capacity_renewal[HR_ROR]
                    Total_installed_hydro_aba[ABA+'.ror']+=ror_renewal_binary.iloc[index_rn][1]*capacity_renewal[HR_ROR]
                    Total_generation_ABA[ABA+'.'+ALP+'.ror']+=ror_renewal_binary.iloc[index_rn][1]*capacity_renewal[HR_ROR]

                    if 'RC_' in HR_ROR:
                        Total_recon_installed[ALP]+=ror_renewal_binary.iloc[index_rn][1]*capacity_renewal[HR_ROR]
                        
                    
            for HR_DAY in hr_day:        
                if ABA==location_renewal[HR_DAY]:
                    index_rn=hr_day.index(HR_DAY)
                    Canada_gen_outline[ALP]=Canada_gen_outline[ALP]+day_renewal_binary.iloc[index_rn][1]*capacity_renewal[HR_DAY]
                    Total_installed[ALP]+=day_renewal_binary.iloc[index_rn][1]*capacity_renewal[HR_DAY]
                    Total_installed_hydro_aba[ABA+'.day']+=day_renewal_binary.iloc[index_rn][1]*capacity_renewal[HR_DAY]
                    Total_generation_ABA[ABA+'.'+ALP+'.day']+=day_renewal_binary.iloc[index_rn][1]*capacity_renewal[HR_DAY]
                    if 'RC_' in HR_DAY:
                        Total_recon_installed[ALP]+=day_renewal_binary.iloc[index_rn][1]*capacity_renewal[HR_DAY]

                    
            for HR_MO in hr_mo:
                if ABA==location_renewal[HR_MO]:
                    index_rn=hr_mo.index(HR_MO)
                    Canada_gen_outline[ALP]=Canada_gen_outline[ALP]+month_renewal_binary.iloc[index_rn][1]*capacity_renewal[HR_MO]
                    Total_installed[ALP]+=month_renewal_binary.iloc[index_rn][1]*capacity_renewal[HR_MO]
                    Total_installed_hydro_aba[ABA+'.month']+=month_renewal_binary.iloc[index_rn][1]*capacity_renewal[HR_MO]
                    Total_generation_ABA[ABA+'.'+ALP+'.month']+=month_renewal_binary.iloc[index_rn][1]*capacity_renewal[HR_MO]
                    if 'RC_' in HR_MO:
                        Total_recon_installed[ALP]+=month_renewal_binary.iloc[index_rn][1]*capacity_renewal[HR_MO]

                    
        elif ALP=='wind' or ALP=='solar':
#            if ALP=='wind':
#                Total_generation_ABA[ABA+'.'+ALP]=0
#                
#            if ALP=='solar':
#                Total_generation_ABA[ABA+'.'+ALP]=0
                
            for GL in gl:
                if map_gl_to_ba[GL]==ABA and str(GL)+'.'+ALP in extant_wind_solar:
                    Canada_gen_outline[ALP]=Canada_gen_outline[ALP]+extant_wind_solar[str(GL)+'.'+ALP]
                    Total_generation_ABA[ABA+'.'+ALP]+=extant_wind_solar[str(GL)+'.'+ALP]               
                if map_gl_to_ba[GL]==ABA and ALP=='wind':
                    Canada_gen_outline[ALP]=Canada_gen_outline[ALP]+capacity_wind.iloc[int(GL)-1][1]
                    Total_installed[ALP]+=capacity_wind.iloc[int(GL)-1][1]
                    Total_generation_ABA[ABA+'.'+ALP]+=capacity_wind.iloc[int(GL)-1][1]
                    if recon:
                        Total_installed[ALP]+=capacity_wind_recon.iloc[int(GL)-1][1]
                        Total_generation_ABA[ABA+'.'+ALP]+=capacity_wind_recon.iloc[int(GL)-1][1]
                        Total_recon_installed[ALP]+=capacity_wind_recon.iloc[int(GL)-1][1]
                        Canada_gen_outline[ALP]+=capacity_wind_recon.iloc[int(GL)-1][1]
                        
                if map_gl_to_ba[GL]==ABA and ALP=='solar':
                    Canada_gen_outline[ALP]=Canada_gen_outline[ALP]+capacity_solar.iloc[int(GL)-1][1]  
                    Total_installed[ALP]+=capacity_solar.iloc[int(GL)-1][1]
                    Total_generation_ABA[ABA+'.'+ALP]+=capacity_solar.iloc[int(GL)-1][1]
                    if recon:
                        Total_installed[ALP]+=capacity_solar_recon.iloc[int(GL)-1][1]
                        Total_generation_ABA[ABA+'.'+ALP]+=capacity_solar_recon.iloc[int(GL)-1][1]
                        Total_recon_installed[ALP]+=capacity_solar_recon.iloc[int(GL)-1][1]
                        Canada_gen_outline[ALP]+=capacity_solar_recon.iloc[int(GL)-1][1]

Total_installed_wind=0
Total_installed_solar=0
total_wind_recon=0
total_solar_recon=0
for GL in gl:
    Total_installed_wind+=capacity_wind.iloc[int(GL)-1][1]
    Total_installed_solar+=capacity_solar.iloc[int(GL)-1][1]
    if recon:
        total_wind_recon+=capacity_wind_recon.iloc[int(GL)-1][1]
        total_solar_recon+=capacity_solar_recon.iloc[int(GL)-1][1]
        
######## sind and solar location(grid cell and coordinate) and capacity #######
wind_cap=list()
solar_cap=list()
lon=list()
lat=list()
loc_aba=list()
gl_loc=list()
for GL in gl:
    if capacity_wind.iloc[int(GL)-1][1]!=0 or capacity_solar.iloc[int(GL)-1][1]!=0:
        gl_loc.append(GL)
        wind_cap.append(capacity_wind.iloc[int(GL)-1][1])
        solar_cap.append(capacity_solar.iloc[int(GL)-1][1])
        loc_aba.append(map_gl_to_ba[GL])
        lon.append(coordinate.iloc[GL*2-1]['lon'])
        lat.append(coordinate.iloc[GL*2-1]['lat'])
        
Installed_wind_solar_data= pd.DataFrame(np.array([gl_loc, wind_cap,solar_cap,lon,lat,loc_aba]))

##### installed transmission ##########3
Installed_transmission=dict()
tr_list=list(capacity_transmission.iloc[:][0])
iter_index=-1        
for TR in tr_list:
    iter_index+=1 
    for TRM in transmap:
        if TR+'.'+capacity_transmission.iloc[iter_index][1] in TRM:
            Installed_transmission[TRM]=capacity_transmission.iloc[iter_index][2]
            
###### Carbon Emission by BA ######
#sum(model.supply[H,ABA,TP]*carbondioxide[TP]/1000000 for H in h for TP in tplants for ABA in aba if AP in ABA)<=carbon_limit[AP]            

Carbon_ABA=dict()
hours_list=list(supply.iloc[:][0])
ba_list=list(supply.iloc[:][1])
tp_type=list(supply.iloc[:][2])
prod_power=list(supply.iloc[:][3])
for ABA in aba:
    Carbon_ABA[ABA]=0            
for IND in list(range(len(hours_list))):
    Carbon_ABA[ba_list[IND]]+=prod_power[IND]*carbondioxide[tp_type[IND]]*sample_rate/1000000

Obj=obj.iloc[0][1]*sample_rate        
os.chdir(cwd)        
del D
del H
del I
del M    

import matplotlib.pyplot as plt

"""
# Pie chart, where the slices will be ordered and plotted counter-clockwise:
labels =list(Canada_gen_outline.keys())
sizes = list(Canada_gen_outline.values())
explode = (0, 0, 0, 0,0,0,0,0,0)  # only "explode" the 2nd slice (i.e. 'Hogs')

fig1, ax1 = plt.subplots(dpi=800,figsize=(8,8))
wedges, texts, autotexts=ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.0f%%',
        shadow=False, startangle=90,pctdistance=0.85,labeldistance=1.07,textprops=dict(color="w"))
ax1.axis('equal')
  # Equal aspect ratio ensures that pie is drawn as a circle.
ax1.legend(wedges,labels,
    title='Generation types',
    loc='center left',
    prop={'size':10},
    bbox_to_anchor=(1,0,1,1))
plt.setp(autotexts,size=7, weight="bold")
ax1.set_title("Canada generation outline")
plt.show()   


fig, ax = plt.subplots(figsize=(12, 12), subplot_kw=dict(aspect="equal"))
wedges, texts = ax.pie(sizes, wedgeprops=dict(width=0.5), startangle=-40)

bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
kw = dict(arrowprops=dict(arrowstyle="-"),
          bbox=bbox_props, zorder=0, va="center")

for i, p in enumerate(wedges):
    ang = (p.theta2 - p.theta1)/2. + p.theta1
    y = np.sin(np.deg2rad(ang))
    x = np.cos(np.deg2rad(ang))
    horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
    connectionstyle = "angle,angleA=0,angleB={}".format(ang)
    kw["arrowprops"].update({"connectionstyle": connectionstyle})
    ax.annotate(labels[i], xy=(x, y), xytext=(1.15*np.sign(x), 1.15*y),
                horizontalalignment=horizontalalignment, **kw)

ax.set_title("Matplotlib bakery: A donut")

plt.show()
"""


#Provincial generation outline:
for AP in ap:
    if AP=="Ontario":
        with open(AP+'_fy'+str(foryear)+'_ct'+str(ctax)+'_rd'+str(rundaynum)+'_sr'+str(sample_rate)+'_recon.csv','w') as csv_writer:
            for ALP in allplants:
                csv_writer.write("%s,%s\n"%(ALP,Total_generation_ABA['Ontario.a.'+ALP]+Total_generation_ABA['Ontario.b.'+ALP]))
    elif AP=="Quebec":
        with open(AP + '_fy' + str(foryear) + '_ct' + str(ctax) + '_rd' + str(rundaynum) + '_sr' + str(sample_rate) + '_recon.csv', 'w') as csv_writer:
            for ALP in allplants:
                csv_writer.write("%s,%s\n" % (ALP, Total_generation_ABA['Quebec.a.' + ALP] + Total_generation_ABA['Quebec.b.' + ALP]))
    elif AP=="Newfoundland and Labrador":
        with open(AP + '_fy' + str(foryear) + '_ct' + str(ctax) + '_rd' + str(rundaynum) + '_sr' + str(sample_rate) + '_recon.csv', 'w') as csv_writer:
            for ALP in allplants:
                csv_writer.write("%s,%s\n" % (ALP, Total_generation_ABA['Newfoundland and Labrador.a.' + ALP] + Total_generation_ABA['Newfoundland and Labrador.b.' + ALP]))
    if not AP=="Ontario" and not AP=="Quebec" and not AP == "Newfoundland and Labrador":
        with open(AP+'_fy'+str(foryear)+'_ct'+str(ctax)+'_rd'+str(rundaynum)+'_sr'+str(sample_rate)+'_recon.csv','w') as csv_writer:
            for ALP in allplants:
                csv_writer.write("%s,%s\n"%(ALP,Total_generation_ABA[AP+'.a.'+ALP]))


#Federal generation outline
with open('Canada_outline'+'_fy'+str(foryear)+'_ct'+str(ctax)+'_rd'+str(rundaynum)+'_sr'+str(sample_rate)+'_recon.csv','w') as csv_writer:
    for key in Canada_gen_outline.keys():
        csv_writer.write("%s,%s\n"%(key,Canada_gen_outline[key]))


#Provincial and Narional carbon emission:
with open('carbon_emission'+'_fy'+str(foryear)+'_ct'+str(ctax)+'_rd'+str(rundaynum)+'_sr'+str(sample_rate)+'_recon.csv','w') as csv_writer:
    for ABA in aba:
        if ABA=='Ontario.a':
            csv_writer.write("%s,%s\n" % ('Ontario.a',Carbon_ABA['Ontario.a']+Carbon_ABA['Ontario.b']))
        elif ABA=='Quebec.a':
            csv_writer.write("%s,%s\n" % ('Quebec.a', Carbon_ABA['Quebec.a'] + Carbon_ABA['Quebec.b']))
        elif ABA=='Newfoundland and Labrador.a':
            csv_writer.write("%s,%s\n" % ('Newfoundland and Labrador.a', Carbon_ABA['Newfoundland and Labrador.a'] + Carbon_ABA['Newfoundland and Labrador.b']))
        if not ABA=='Ontario.a' and not ABA=='Ontario.b' and not ABA=='Quebec.a' and not ABA=='Quebec.b' and not ABA=='Newfoundland and Labrador.a' and not ABA=='Newfoundland and Labrador.b':
            csv_writer.write("%s,%s\n" % (ABA,Carbon_ABA[ABA]))
    csv_writer.write("%s,%s\n" % ('Canada',sum(Carbon_ABA.values())))
