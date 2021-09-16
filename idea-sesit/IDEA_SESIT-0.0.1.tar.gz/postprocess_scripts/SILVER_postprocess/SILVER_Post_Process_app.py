import streamlit as st
import pandas as pd
import numpy as np
import urllib
from query_SILVER import import_UC_results,import_line_flow, total_generation,\
    dispatch_stack, dispatch_stack_plot,total_generation_plot, plot_Gens,\
    GHG_factors, GHG_plot, total_GHG_plot, map_generators, transmission_network, Gen_inspector

st.header("SILVER RESULTS")
expander = st.beta_expander("FAQ")
expander.write("This tool takes output data from the SILVER electricity system model and visualizes the data in an "
               "interactive way on a locally hosted webapp. The webapp platform is based on Streamlit, and the plotting "
               "functions are based on Pandas and Bokeh. Data is provided from SILVER model outputs and spatial data "
               "collected externally.")

options = ['AB','BC','MN','NB','NL','NS','ON','PE','QB','SK']

@st.cache
def get_data(scenario):
    Generators, Map = import_UC_results(scenario)
    Lines = import_line_flow(scenario)
    return(Generators, Map, Lines)

#Functions for displaying data
try:
    def plot_dispatch_stack(scenario):
        Generators, Map, Lines = get_data(scenario)
        gen_type = dispatch_stack(Generators, Map)
        p = dispatch_stack_plot(gen_type)
        return(st.bokeh_chart(p, use_container_width=True))

    def plot_total_gen(scenario):
        Generators, Map, Lines = get_data(scenario)
        total_gen = total_generation(Generators, Map)
        p = total_generation_plot(total_gen)
        return (st.bokeh_chart(p, use_container_width=True))

    def total_gen_table(scenario):
        Generators, Map, Lines = get_data(scenario)
        total_gen = total_generation(Generators, Map)
        return(total_gen)

    def GHG(scenario):
        Generators, Map, Lines = get_data(scenario)
        GHG_emissions, GHG_by_type, total_GHG = GHG_factors(UC_Results=Generators,map=Map)
        p = total_GHG_plot(total_GHG)
        return (st.bokeh_chart(p, use_container_width=True))

    def GHG_by_Type(scenario):
        Generators, Map, Lines = get_data(scenario)
        GHG_emissions, GHG_by_type, total_GHG = GHG_factors(UC_Results=Generators,map=Map)
        p = GHG_plot(GHG_by_type)
        return (st.bokeh_chart(p, use_container_width=True))

    def map_data(scenario):
        if st.checkbox('Satellite Imagery'):
            Tile = 'ESRI_IMAGERY'
        else: Tile = 'CARTODBPOSITRON'

        if st.checkbox('Colour by Installed Capacity'):
            Viz_Colour = "Capacity"
        else: Viz_Colour = None

        if st.checkbox('Size by Installed Capacity'):
            size = "Capacity"
        else: size = None

        p = map_generators(Province=scenario,Tile=Tile,Viz_Colour=Viz_Colour,size_input = size)
        return(st.bokeh_chart(p, use_container_width=True))

    def transmission(scenario):
        Generators, Map, Lines = get_data(scenario)
        if st.checkbox('Layout with Fruchterman-Reingold force-directed algorithm'):
            Shape = 1
        else: Shape = 0
        p = transmission_network(Lines, Shape)
        return(st.bokeh_chart(p, use_container_width=True))

    def Gens(gen_data,bus_names):
        p = plot_Gens(gen_data,bus_names)
        return (st.bokeh_chart(p, use_container_width=True))


#write to the app and add interactions

    #Sidebar
    scenario = st.sidebar.selectbox('Province', options)

    if st.sidebar.checkbox('Dispatch Stack'):
        plot_dispatch_stack(scenario)


    if st.sidebar.checkbox('Total GHG Plot'):
        GHG(scenario)

    if st.sidebar.checkbox('GHG Plot by Generation Type'):
        GHG_by_Type(scenario)

    if st.sidebar.checkbox('Generator Map'):
        map_data(scenario)

    if st.sidebar.checkbox('Generator Inspector'):
        Generators, Map, Lines = get_data(scenario)
        gen_data, bus_names = Gen_inspector(Generators, Map)
        options = st.multiselect('Generator Buses', bus_names)
        Gens(gen_data, options)
        st.write('You selected:', options)

    if st.sidebar.checkbox('Transmission Network'):
        transmission(scenario)

    if st.sidebar.checkbox('Total Annual Generation '):
        total_gen = total_gen_table(scenario)
        col1, col2, col3 = st.beta_columns(3)
        with col1:
            plot_total_gen(scenario)
        with col2:
            st.dataframe(total_gen)

    if st.sidebar.checkbox('Raw Data'):
        Generators, Map, Lines = get_data(scenario)
        #st.dataframe(Generators)
        st.dataframe(Map)
        st.dataframe(Lines)

#Error handling: pass errors to streamlit app
except urllib.error.URLError as e:
    st.error(
        """
        **This webapp requires internet access.**

        Connection error: %s
    """
        % e.reason
    )







