# -*- coding: utf-8 -*-

survey_att_dict = {"Project":"ISTP>International - Solar-Terrestrial Physics" ,
"Source_name":"CuPID>Cusp Plasma Imaging Detector" ,
"Discipline":"Space Physics>Magnetospheric Science" ,
"Data_type":"K0>Key Parameter" ,
"Descriptor":"CXDH>Combined Xray, Dosimetry, Housekeeping" ,
"Data_version":"1" ,
"Logical_file_id":"cupid_srvy_20210919_v01" ,
"PI_name":"B. Walsh" ,
"PI_affiliation":"BU" ,
"TEXT":"https://doi.org/10.1029/2020JA029015" ,
"Instrument_type":"Particles (space)" ,
"Mission_group":"CuPID" ,
"Logical_source":"CuPID_CXDH" ,
"Logical_source_description":"CuPID survey key parameter data"}

ephemeris_att_dict = {"Project":"ISTP>International - Solar-Terrestrial Physics" ,
"Source_name":"CuPID>Cusp Plasma Imaging Detector" ,
"Discipline":"Space Physics>Magnetospheric Science" ,
"Data_type":"K0>Key Parameter" ,
"Descriptor":"EPHM>Mission Ephemeris" ,
"Data_version":"1" ,
"Logical_file_id":"cupid_ephm_20210919_v01" ,
"PI_name":"B. Walsh" ,
"PI_affiliation":"BU" ,
"TEXT":"https://doi.org/10.1029/2020JA029015" ,
"Instrument_type":"Ephemeris" ,
"Mission_group":"CuPID" ,
"Logical_source":"CuPID_CXDH" ,
"Logical_source_description":"CuPID survey key parameter data"}

dosi_att_dict = {"Project":"ISTP>International - Solar-Terrestrial Physics" ,
"Source_name":"CuPID>Cusp Plasma Imaging Detector" ,
"Discipline":"Space Physics>Magnetospheric Science" ,
"Data_type":"K0>Key Parameter" ,
"Descriptor":"DOSI>Dosimeter" ,
"Data_version":"1" ,
"Logical_file_id":"cupid_dosi_20210919_v01" ,
"PI_name":"B. Walsh" ,
"PI_affiliation":"BU" ,
"TEXT":"https://doi.org/10.1029/2020JA029015" ,
"Instrument_type":"Particles (space)" ,
"Mission_group":"CuPID" ,
"Logical_source":"CuPID_DOSI" ,
"Logical_source_description":"CuPID dosimeter key parameter data"}

mags_att_dict = {"Project":"ISTP>International - Solar-Terrestrial Physics" ,
"Source_name":"CuPID>Cusp Plasma Imaging Detector" ,
"Discipline":"Space Physics>Magnetospheric Science" ,
"Data_type":"K0>Key Parameter" ,
"Descriptor":"MAGS>Magnetometer" ,
"Data_version":"1" ,
"Logical_file_id":"cupid_mags_20210919_v01" ,
"PI_name":"B. Walsh" ,
"PI_affiliation":"BU" ,
"TEXT":"https://doi.org/10.1029/2020JA029015" ,
"Instrument_type":"Magnetic Fields (space)" ,
"Mission_group":"CuPID" ,
"Logical_source":"CuPID_MAGS" ,
"Logical_source_description":"CuPID magnetometer key parameter data"}

xray_att_dict = {"Project":"ISTP>International - Solar-Terrestrial Physics" ,
"Source_name":"CuPID>Cusp Plasma Imaging Detector" ,
"Discipline":"Space Physics>Magnetospheric Science" ,
"Data_type":"K0>Key Parameter" ,
"Descriptor":"XRAY>X-Ray telescope" ,
"Data_version":"1" ,
"Logical_file_id":"cupid_xray_20210919_v01" ,
"PI_name":"B. Walsh" ,
"PI_affiliation":"BU" ,
"TEXT":"https://doi.org/10.1029/2020JA029015" ,
"Instrument_type":"Imagers (space)" ,
"Mission_group":"CuPID" ,
"Logical_source":"CuPID_XRAY" ,
"Logical_source_description":"CuPID X-ray telescope key parameter data"}

var_att_template = {"CATDESC":"80 character-ish description of variable and dependencies - time? energy channels? this should be enough to tell users whether or not they're interested in this variable." ,
"DEPEND_0":"Epoch" ,
"FIELDNAM":"Character string describing variables, e.g. labeling a plot" ,
"FILLVAL":"number inserted to denote missing/bad data, determined by data type" ,
"FORMAT":"output_format_string" ,
"UNITS":"units, yup" ,
"VALIDMIN":"least valid value" ,
"VALIDMAX":"greatest valid value" ,
"VAR_TYPE":"data,support_data,metadata,ignore_data"}

#These are *required*.  There are also optional ones.  We'll deal with that later.
 
#Fill values are as follows
#REAL*4 ---- -1.0E31
#REAL*8 ---- -1.0E31
#BYTE ---- -128
#INTEGER*2 ---- -32768
#INTEGER*4 ---- -2147483648
#Unsigned INTEGER*1 ---- 255
#Unsigned INTEGER*2 ---- 65535
#Unsigned INTEGER*4 ---- 4294967295
#Signed INTEGER*8 ---- -9223372036854775808LL


# #Survey Data Variable Attributes
#######################################################

epoch_srvy_att = {"CATDESC":"Survey data UTC epoch in UNIX timestamp." ,
"FIELDNAM":"UTC Time" ,
"FILLVAL":-1.0E31 ,
"UNITS":"ms" ,
"VALIDMIN":"least valid value" ,
"VALIDMAX":"greatest valid value" ,
"VAR_TYPE":"support_data"}

xray_srvy_att = {"CATDESC":"X-Ray countrate in counts/second with background subtracted." ,
"DEPEND_0":"Epoch" ,
"DISPLAY_TYPE":"time_series",
"FIELDNAM":"X-Ray Countrate" ,
"FILLVAL":-1.0E31 ,
"FORMAT":"%lf.2" ,
"LABLAXIS":"XRAY CR",
"UNITS":"cts/s" ,
"VALIDMIN":"least valid value" ,
"VALIDMAX":"greatest valid value" ,
"VAR_TYPE":"data"}

xray_raw_srvy_att = {"CATDESC":"Raw X-Ray countrate in counts/second." ,
"DEPEND_0":"Epoch" ,
"DISPLAY_TYPE":"time_series",
"FIELDNAM":"Raw X-Ray Countrate" ,
"FILLVAL":-1.0E31 ,
"FORMAT":"%lf.2" ,
"LABLAXIS":"XRAY CR RAW",
"UNITS":"cts/s" ,
"VALIDMIN":"least valid value" ,
"VALIDMAX":"greatest valid value" ,
"VAR_TYPE":"data"}

xray_bg_srvy_att = {"CATDESC":"Cosmic background X-Ray countrate in counts/second." ,
"DEPEND_0":"Epoch" ,
"DISPLAY_TYPE":"time_series",
"FIELDNAM":"BG X-Ray Countrate" ,
"FILLVAL":-1.0E31 ,
"FORMAT":"%lf.2" ,
"LABLAXIS":"XRAY CR BG",
"UNITS":"cts/s" ,
"VALIDMIN":"least valid value" ,
"VALIDMAX":"greatest valid value" ,
"VAR_TYPE":"data"}

dosa_srvy_att = {"CATDESC":"Survey-Grade Dosimeter A countrate in counts/second." ,
"DEPEND_0":"Epoch" ,
"DISPLAY_TYPE":"time_series",
"FIELDNAM":"Dosi A Countrate" ,
"FILLVAL":-1.0E31 ,
"FORMAT":"%lf.1" ,
"LABLAXIS":"DOS A CR",
"UNITS":"cts/s" ,
"VALIDMIN":"least valid value" ,
"VALIDMAX":"greatest valid value" ,
"VAR_TYPE":"data"}

dosb_srvy_att = {"CATDESC":"Survey-Grade Dosimeter B countrate in counts/second." ,
"DEPEND_0":"Epoch" ,
"DISPLAY_TYPE":"time_series",
"FIELDNAM":"Dosi B Countrate" ,
"FILLVAL":-1.0E31 ,
"FORMAT":"%lf.1" ,
"LABLAXIS":"DOS B CR",
"UNITS":"cts/s" ,
"VALIDMIN":"least valid value" ,
"VALIDMAX":"greatest valid value" ,
"VAR_TYPE":"data"}

flag_srvy_att = {"CATDESC":"Survey data quality flags. 0: good, 1: soft warning, 2: hard warning" ,
"DEPEND_0":"Epoch" ,
"DISPLAY_TYPE":"no_plot",
"FIELDNAM":"Flag" ,
"FILLVAL":-32768 ,
"FORMAT":"%i" ,
"UNITS":" " ,
"VALIDMIN":"least valid value" ,
"VALIDMAX":"greatest valid value" ,
"VAR_TYPE":"support_data"}

# #Ephemeris Variable Attributes
#######################################################
epoch_ephm_att = {"CATDESC":"Mission Ephemeris UTC epoch in UNIX timestamp." ,
"FIELDNAM":"UTC Time" ,
"FILLVAL":-1.0E31 ,
"UNITS":"ms" ,
"VALIDMIN":"least valid value" ,
"VALIDMAX":"greatest valid value" ,
"VAR_TYPE":"support_data"}

posgsm_ephm_att = {"CATDESC":"Spacecraft position in GSM coordinates (X/Y/Z)." ,
"DEPEND_0":"Epoch" ,
"DISPLAY_TYPE":"time_series",
"FIELDNAM":"Position GSM" ,
"FILLVAL":-1.0E31 ,
"FORMAT":"%lf.2" ,
"LABL_PTR_1":"posgsm_label",
"UNITS_PTR":"posgsm_units" ,
"VALIDMIN":"least valid value" ,
"VALIDMAX":"greatest valid value" ,
"VAR_TYPE":"data"}

posgse_ephm_att = {"CATDESC":"Spacecraft position in GSE coordinates (X/Y/Z)." ,
"DEPEND_0":"Epoch" ,
"DISPLAY_TYPE":"time_series",
"FIELDNAM":"Position GSE" ,
"FILLVAL":-1.0E31 ,
"FORMAT":"%lf.2" ,
"LABL_PTR_1":"posgse_label",
"UNITS_PTR":"posgse_units" ,
"VALIDMIN":"least valid value" ,
"VALIDMAX":"greatest valid value" ,
"VAR_TYPE":"data"}

posmag_ephm_att = {"CATDESC":"Spacecraft position in magnetic coordinates (R/MLat/MLon)." ,
"DEPEND_0":"Epoch" ,
"DISPLAY_TYPE":"time_series",
"FIELDNAM":"Position GSE" ,
"FILLVAL":-1.0E31 ,
"FORMAT":"%lf.2" ,
"LABL_PTR_1":"posmag_label",
"UNITS_PTR":"posmag_units" ,
"VALIDMIN":"least valid value" ,
"VALIDMAX":"greatest valid value" ,
"VAR_TYPE":"data"}

celest_ephm_att = {"CATDESC":"Spacecraft boresight pointing in RA and Dec." ,
"DEPEND_0":"Epoch" ,
"DISPLAY_TYPE":"time_series",
"FIELDNAM":"Celestial Pointing" ,
"FILLVAL":-1.0E31 ,
"FORMAT":"%lf.2" ,
"LABL_PTR_1":"celest_label",
"UNITS_PTR":"celest_units" ,
"VALIDMIN":"least valid value" ,
"VALIDMAX":"greatest valid value" ,
"VAR_TYPE":"data"}

pointing_ephm_att = {"CATDESC":"Spacecraft boresight pointing in GSM Vector." ,
"DEPEND_0":"Epoch" ,
"DISPLAY_TYPE":"time_series",
"FIELDNAM":"GSM Pointing" ,
"FILLVAL":-1.0E31 ,
"FORMAT":"%lf.2" ,
"LABL_PTR_1":"point_label",
"UNITS_PTR":"point_units",
"VALIDMIN":"least valid value" ,
"VALIDMAX":"greatest valid value" ,
"VAR_TYPE":"data"}

flag_ephm_att = {"CATDESC":"Ephemeris quality flags. 0 = good, 1 = soft warning, 2 = hard warning" ,
"DEPEND_0":"Epoch" ,
"DISPLAY_TYPE":"no_plot",
"FIELDNAM":"Flag" ,
"FILLVAL":-32768 ,
"FORMAT":"%i" ,
"UNITS":" " ,
"VALIDMIN":"least valid value" ,
"VALIDMAX":"greatest valid value" ,
"VAR_TYPE":"support_data"}

posgsm_ephm_label = {
"CATDESC":"GSM position label.",
"FIELDNAM":"GSM position label.",
"VAR_TYPE":"metadata"
}

posgse_ephm_label = {
"CATDESC":"GSE position label.",
"FIELDNAM":"GSE position label.",
"VAR_TYPE":"metadata"
}

posmag_ephm_label = {
"CATDESC":"MAG position label.",
"FIELDNAM":"MAG position label.",
"VAR_TYPE":"metadata"
}

celest_ephm_label = {
"CATDESC":"Celestial pointing label.",
"FIELDNAM":"Celestial pointing label.",
"VAR_TYPE":"metadata"
}

point_ephm_label = {
"CATDESC":"GSM vector pointing label.",
"FIELDNAM":"GSM vector pointing label.",
"VAR_TYPE":"metadata"
}

posgsm_ephm_units = {
"CATDESC":"GSM position unit.",
"FIELDNAM":"GSM position unit.",
"VAR_TYPE":"metadata"
}

posgse_ephm_units = {
"CATDESC":"GSE position unit.",
"FIELDNAM":"GSE position unit.",
"VAR_TYPE":"metadata"
}

posmag_ephm_units = {
"CATDESC":"MAG position unit.",
"FIELDNAM":"MAG position unit.",
"VAR_TYPE":"metadata"
}

celest_ephm_units = {
"CATDESC":"Celestial pointing unit.",
"FIELDNAM":"Celestial pointing unit.",
"VAR_TYPE":"metadata"
}

point_ephm_units = {
"CATDESC":"GSM vector pointing unit.",
"FIELDNAM":"GSM vector pointing unit.",
"VAR_TYPE":"metadata"
}

# #Dosimeter Variable Attributes
#######################################################

epoch_dosi_att = {"CATDESC":"Dosimeter UTC epoch in UNIX timestamp." ,
"FIELDNAM":"UTC Time" ,
"FILLVAL":-1.0E31 ,
"UNITS":"ms" ,
"VALIDMIN":"least valid value" ,
"VALIDMAX":"greatest valid value" ,
"VAR_TYPE":"support_data"}

dosa_dosi_att = {"CATDESC":"Dosimeter A countrate in counts/second." ,
"DEPEND_0":"Epoch" ,
"DISPLAY_TYPE":"time_series",
"FIELDNAM":"Dosi A Countrate" ,
"FILLVAL":-1.0E31 ,
"FORMAT":"%lf" ,
"LABLAXIS":"DOS A CR",
"UNITS":"Counts/Second" ,
"VALIDMIN":"least valid value" ,
"VALIDMAX":"greatest valid value" ,
"VAR_TYPE":"data"}

dosb_dosi_att = {"CATDESC":"Dosimeter B countrate in counts/second." ,
"DEPEND_0":"Epoch" ,
"DISPLAY_TYPE":"time_series",
"FIELDNAM":"Dosi B Countrate" ,
"FILLVAL":-1.0E31 ,
"FORMAT":"%lf" ,
"LABLAXIS":"DOS B CR",
"UNITS":"Counts/Second" ,
"VALIDMIN":"least valid value" ,
"VALIDMAX":"greatest valid value" ,
"VAR_TYPE":"data"}

flag_dosi_att = {"CATDESC":"Dosimeter quality flags. 0 = good, 1 = soft warning, 2 = hard warning" ,
"DEPEND_0":"Epoch" ,
"DISPLAY_TYPE":"no_plot",
"FIELDNAM":"Flag" ,
"FILLVAL":-32768 ,
"FORMAT":"%i" ,
"UNITS":" " ,
"VALIDMIN":"least valid value" ,
"VALIDMAX":"greatest valid value" ,
"VAR_TYPE":"support_data"}

# #Magnetometer Variable Attributes
#######################################################

epoch_mags_att = {"CATDESC":"Magnetometer UTC epoch in UNIX timestamp." ,
"FIELDNAM":"UTC Time" ,
"FILLVAL":-1.0E31 ,
"UNITS":"ms" ,
"VALIDMIN":"least valid value" ,
"VALIDMAX":"greatest valid value" ,
"VAR_TYPE":"support_data"}

bgsm_mags_att = {"CATDESC":"DC magnetic field measurements in GSM coordinates (X/Y/Z)." ,
"DEPEND_0":"Epoch" ,
"DISPLAY_TYPE":"time_series",
"FIELDNAM":"BGSM" ,
"FILLVAL":-1.0E31 ,
"FORMAT":"%lf" ,
"LABL_PTR_1":"bgsm_label",
"UNITS_PTR":"bgsm_units" ,
"VALIDMIN":"least valid value" ,
"VALIDMAX":"greatest valid value" ,
"VAR_TYPE":"data"}

bgse_mags_att = {"CATDESC":"DC magnetic field measurements in GSE coordinates (X/Y/Z)." ,
"DEPEND_0":"Epoch" ,
"DISPLAY_TYPE":"time_series",
"FIELDNAM":"BGSE" ,
"FILLVAL":-1.0E31 ,
"FORMAT":"%lf" ,
"LABL_PTR_1":"bgse_label",
"UNITS_PTR":"bgse_units" ,
"VALIDMIN":"least valid value" ,
"VALIDMAX":"greatest valid value" ,
"VAR_TYPE":"data"}

bgeo_mags_att = {"CATDESC":"DC magnetic field measurements in GEO coordinates (NS/EW/R)." ,
"DEPEND_0":"Epoch" ,
"DISPLAY_TYPE":"time_series",
"FIELDNAM":"BGEO" ,
"FILLVAL":-1.0E31 ,
"FORMAT":"%lf" ,
"LABL_PTR_1":"bgeo_label",
"UNITS_PTR":"bgeo_units" ,
"VALIDMIN":"least valid value" ,
"VALIDMAX":"greatest valid value" ,
"VAR_TYPE":"data"}

flag_mags_att = {"CATDESC":"Magnetometer quality flags. 0 = good, 1 = soft warning, 2 = hard warning" ,
"DEPEND_0":"Epoch" ,
"DISPLAY_TYPE":"no_plot",
"FIELDNAM":"Flag" ,
"FILLVAL":-32768 ,
"FORMAT":"%i" ,
"UNITS":" " ,
"VALIDMIN":"least valid value" ,
"VALIDMAX":"greatest valid value" ,
"VAR_TYPE":"support_data"}

bgsm_mags_label = {
"CATDESC":"B GSM label.",
"FIELDNAM":"B GSM label.",
"VAR_TYPE":"metadata"
}

bgse_mags_label = {
"CATDESC":"B GSE label.",
"FIELDNAM":"B GSE label.",
"VAR_TYPE":"metadata"
}

bgeo_mags_label = {
"CATDESC":"B GEO label.",
"FIELDNAM":"B GEO label.",
"VAR_TYPE":"metadata"
}

bgsm_mags_units = {
"CATDESC":"B GSM units.",
"FIELDNAM":"B GSM units.",
"VAR_TYPE":"metadata"
}

bgse_mags_units = {
"CATDESC":"B GSE units.",
"FIELDNAM":"B GSE units.",
"VAR_TYPE":"metadata"
}

bgeo_mags_units = {
"CATDESC":"B GEO units.",
"FIELDNAM":"B GEO units.",
"VAR_TYPE":"metadata"
}

# #Survey Data Variable Attributes
#######################################################

epoch_xray_template = {"CATDESC":"X-Ray Event Arrival UTC epoch in UNIX timestamp." ,
"FIELDNAM":"UTC Time" ,
"FILLVAL":-1.0E31 ,
"UNITS":"ms" ,
"VALIDMIN":"least valid value" ,
"VALIDMAX":"greatest valid value" ,
"VAR_TYPE":"support_data"}

position_xray_att = {"CATDESC":"Event Arrival Position in RA/Dec." ,
"DEPEND_0":"Epoch" ,
"FIELDNAM":"Photon Position" ,
"FILLVAL":-1.0E31 ,
"FORMAT":"CDF_DOUBLE" ,
"LABL_PTR_1":"posxray_label",
"UNITS":"Degrees" ,
"VALIDMIN":"least valid value" ,
"VALIDMAX":"greatest valid value" ,
"VAR_TYPE":"data",
"DISPLAY_TYPE":"time_series"}

flag_xray_att = {"CATDESC":"X-Ray data quality flags. 0 = good, 1 = soft warning, 2 = hard warning" ,
"DEPEND_0":"Epoch" ,
"FIELDNAM":"Flag" ,
"FILLVAL":-32768 ,
"FORMAT":"%i" ,
"UNITS":" " ,
"VALIDMIN":"least valid value" ,
"VALIDMAX":"greatest valid value" ,
"VAR_TYPE":"support_data",
"DISPLAY_TYPE":"no_plot"}

position_xray_label = {
"CATDESC":"X-Ray event position label.",
"FIELDNAM":"X-Ray event position label.",
"VAR_TYPE":"metadata"
}

position_xray_units = {
"CATDESC":"X-Ray event position units.",
"FIELDNAM":"X-Ray event position units.",
"VAR_TYPE":"metadata"
}