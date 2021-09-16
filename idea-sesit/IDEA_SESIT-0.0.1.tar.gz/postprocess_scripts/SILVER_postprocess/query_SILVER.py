import pandas as pd
import itertools
import glob
import os
import bokeh.plotting as bp
import networkx as nx
from bokeh.plotting import figure, from_networkx
from bokeh.palettes import Spectral, Spectral11, Spectral4
from bokeh.models import ColumnDataSource, NumeralTickFormatter,ColorBar,WheelZoomTool,LabelSet
from bokeh.tile_providers import CARTODBPOSITRON, get_provider, ESRI_IMAGERY
from bokeh.transform import factor_cmap, linear_cmap
from pyproj import Proj, transform
from bokeh.models import (BoxSelectTool, BoxZoomTool, ResetTool, Circle, EdgesAndLinkedNodes, HoverTool,
                          MultiLine, NodesAndLinkedEdges, Plot, Range1d, TapTool, )

def import_UC_results(province):
    '''This function takes a two letter province code as an import variable and imports all the .csv files containing unit
    commitment results from a SILVER model run. It is built in a way where it will take the province code, change
    directories to a file of the same code, and parse through the file containing any csv files prefixed with
     “UC_Results”. It returns a dataframe with the combiend timeseries, and a datafrme of generator metadata'''
    # import all csv files from silver results folder
    owd = os.getcwd()
    os.chdir(province)
    all_filenames = [i for i in glob.glob('UC_Results_*.csv')]
    combined_csv = pd.concat([pd.read_csv(f,skiprows=[i for i in range(1,30)],index_col=0,skipfooter=749) for f in all_filenames])
    combined_csv.index = pd.to_datetime(combined_csv.index)
    combined_csv = combined_csv.drop(columns=['Total','dr'])
    os.chdir(owd)
    combined_csv.to_csv("combined_csv.csv", index=False, encoding='utf-8-sig')

    #get data about each generator from the first UC_Results CSV file
    os.chdir(province)
    map_filename = all_filenames[1]
    UC_Map = pd.read_csv(map_filename, index_col=0, skipfooter=1469)
    UC_Map = UC_Map.drop(columns=['Total', 'dr'])
    UC_Map_Transpose = UC_Map.transpose()

    os.chdir(owd)
    return combined_csv, UC_Map_Transpose

def import_line_flow(province):
    '''This function takes a two letter province code as an import variable and imports all the .csv files containing
     line flow results from a SILVER model run. It is built in a way where it will take the province code, change
       directories to a file of the same code, and parse through the file containing any csv files prefixed with
        “UC_Results”. It returns a dataframe with the combiend timeseries'''
    #todo: rename columns titles with correct time index
    owd = os.getcwd()
    os.chdir(province)

    all_filenames = [i for i in glob.glob('Line_Flow_*.csv')]
    combined = pd.concat([(pd.read_csv(f)) for f in all_filenames], axis=1)
    os.chdir(owd)
    combined.to_csv("combined_csv_lineflow.csv", index=False, encoding='utf-8-sig')
    os.chdir(owd)
    return combined

def total_generation(UC_Results,UC_Map):
    '''This function takes the data frame of UC results and the Map data frame and returns a data frame of
    aggregated energy results for the entire year summed by generator type'''

    # make a dictonary with generator type and rename the columns
    dict_UC_Map = UC_Map['kind'].to_dict()
    UC_Results = UC_Results.rename(columns=dict_UC_Map)

    # add up generation by generator kind
    total_gen = UC_Results.sum(axis=0, skipna=True)
    total_gen_1 = total_gen.groupby(level=0).sum().to_frame()
    return total_gen_1

def total_generation_plot(gen):
    '''This function takes an hourly data frame of unot commitment results aggregated for the entire year by
    generation type and plots a bar graph. the data is transposed to work with bokeh Column data source'''

    #transpose the dataframe and create stacked bar chart
    p = figure(plot_width=700, plot_height=500, y_axis_label='MWH', title='Annual Generation',
               tools="pan, reset",toolbar_location="left", active_drag=None)
    p.grid.minor_grid_line_color = '#eeeeee'
    source = bp.ColumnDataSource(gen.T)
    names = list(gen.T.columns.values)
    p.vbar_stack(x=None,source=source,width=0.7, color=Spectral[len(names)],stackers=names, legend_label=names)

    p.legend.location = 'top_left'
    p.legend.items.reverse()
    p.legend.click_policy = 'mute'
    p.yaxis.formatter = NumeralTickFormatter(format="00")

    return(p)

def dispatch_stack(UC_Results,UC_Map):
    '''This function takes the data frame of UC results and the Map data frame and returns a data frame of
    hourly energy results grouped by generator type. '''

    # make a dictonary with generator type and rename the columns
    dict_UC_Map = UC_Map['kind'].to_dict()
    UC_Results = UC_Results.rename(columns=dict_UC_Map)

    # group generation by generator kind
    gen_type = UC_Results.groupby(level=0,axis=1).sum()

    return gen_type

def dispatch_stack_plot(gen):
    '''This function takes the dataframe from the dispatch_stack function and plots as an area plot for each
    generations type. The plotting is facilitated with the Bokeh Varea Stack function.'''
    # tool setup
    TOOLTIPS = [("hour", "@{Time}"),
                ("Energy generated ", "$sy MWH"), ]

    width = 1500
    height = 500
    title = 'Dispatch by Generator Type'
    p = figure(plot_width=width, plot_height=height, x_axis_type='datetime', x_axis_label='Time', y_axis_label='MWH',
               title=title,tools="box_zoom, pan, hover, crosshair, reset", tooltips=TOOLTIPS, toolbar_location="left",active_drag="box_zoom")
    p.grid.minor_grid_line_color = '#eeeeee'

    # data source
    gen = gen.rename_axis('Time')
    mySource = bp.ColumnDataSource(gen)

    # the order of the names list changes the order of the stack
    names = list(gen.columns.values)

    # create plots
    p.varea_stack(stackers=names, x='Time', color=Spectral[len(names)], legend_label=names, source=mySource)

    # reverse and move the legend entries to match the stacked order
    p.legend.items.reverse()
    p.legend.location = 'top_left'
    p.legend.click_policy = 'hide'
    p.yaxis.formatter = NumeralTickFormatter(format="00")
    return(p)

def GHG_factors(map, UC_Results):
    '''This function takes a csv file containing the site independent data which contains a GHG emission factor for
    each generation type. It takes the UC results and Map dataframes, re-titles each column by generator type and the
    and multiples the GHG factors to each respective column. The data is then grouped by generation type and summed
    for a total system emissions.'''

    owd = os.getcwd()
    kind_data = pd.read_csv(owd + '\site_independent.csv')
    combined = pd.merge(left=map, right=kind_data, left_on="kind", right_on="kind", how="left")
    combined = combined.set_index(map.index)
    # make a dictonary with generator type and rename the columns
    dict_UC_Map = combined['GHG emissions'].to_dict()
    GHG_emissions = UC_Results.mul(pd.Series(dict_UC_Map), axis=1)

    dict_UC_Map = map['kind'].to_dict()
    GHG_emissions_type= GHG_emissions.rename(columns=dict_UC_Map)
    GHG_by_type = GHG_emissions_type.groupby(level=0, axis=1).sum()
    total_GHG = GHG_emissions.sum(axis=1)

    return GHG_emissions, GHG_by_type, total_GHG

def GHG_plot(GHG_emissions):
    '''This function takes the transformed data for GHG emissions by generation type from the GHG factors function
    and plots a ling graph to display the emissions over time. '''

    #tool setup
    TOOLTIPS = [("hour", "$index"),
                ("C02 Emissions", "$y kg C02e"), ]
    width = 1500
    height = 500
    title = 'GHG Emissions by Generation type'
    p = figure(plot_width=width, plot_height=height, x_axis_type='datetime', x_axis_label='Time', y_axis_label='kg C02e',
               title=title, tooltips=TOOLTIPS,tools="box_zoom, pan, hover, crosshair, reset", toolbar_location="left", active_drag="box_zoom")
    p.grid.minor_grid_line_color = '#eeeeee'

    numlines = len(GHG_emissions.columns.tolist())
    print(GHG_emissions.columns.tolist())
    mypalette = Spectral[numlines]
    names = list(GHG_emissions.columns.values)

    colors = itertools.cycle(Spectral11)
    for i in GHG_emissions.columns:
        p.line(x=GHG_emissions.index, y=GHG_emissions[i], line_color=next(colors), line_width=2,legend_label = i)


    # move the legend entries to match the stacked order
    p.legend.location = 'top_left'
    p.legend.click_policy = 'hide'
    p.yaxis.formatter = NumeralTickFormatter(format="00")
    return(p)

def total_GHG_plot(GHG_total):
    '''This function takes an hourly dataframe of unit commitment results aggregated for the entire year by
    generation type and plots a bar graph. '''

    #tool setup
    TOOLTIPS = [("hour", "$index"),
                ("GHG Emissions", "$y kg C02e"), ]
    width = 1500
    height = 500
    title = 'Total GHG Emissions'
    p = figure(plot_width=width, plot_height=height, x_axis_type='datetime', x_axis_label='Time', y_axis_label='kg C02e',
               title=title, tooltips=TOOLTIPS, tools="box_zoom, pan, hover, crosshair, reset", toolbar_location="left", active_drag="box_zoom")
    p.grid.minor_grid_line_color = '#eeeeee'

    p.line(GHG_total.index, GHG_total, color='black', line_width=2)
    p.yaxis.formatter = NumeralTickFormatter(format="00")

    return(p)

def map_generators(Province,Viz_Colour,Tile,size_input):
    '''This function imports a csv file of generator data and locates it on a map with options for multiple
    visualizations. The latitude and longitude data is transformed to mercator using the pyproj library. The points
    are then plotted over a bokeh figure with a basemap tile. input to this function configure the visualization option
    including choosing the tile, changing the color to present generation type or capacity, or resizing the points
    by nameplate capacity.'''


    title = 'Generator Assets in '+ Province
    TOOLTIPS = [("Asset ID", "@{Asset ID}"),("Project Name", "@{Project Name}"),("Location", "@Location"),
                ("Owner", "@Owner"),("Type","@{Generator Type}"), ("Installed Capacity","@{Installed Capacity}"+" MWH")]

    inProj = Proj(init='epsg:3857')
    outProj = Proj(init='epsg:4326')

    #set start postion of map on north america
    world_lon1, world_lat1 = transform(outProj, inProj, -150, 30)
    world_lon2, world_lat2 = transform(outProj, inProj, -50, 80)

    tile_provider = get_provider(Tile)
    p = figure(x_range=(world_lon1, world_lon2), y_range=(world_lat1, world_lat2),
               x_axis_type="mercator", y_axis_type="mercator",
               x_axis_label='Longitude', y_axis_label='Latitude',
               title=title, toolbar_location="left", tooltips=TOOLTIPS,
               tools="pan, lasso_select, hover, crosshair, reset",
               plot_width=700, plot_height=700,)
    p.add_tile(tile_provider)

    owd = os.getcwd()
    os.chdir("chargedup")
    data = pd.read_csv(Province + ".csv")
    os.chdir(owd)

    point_data = pd.DataFrame(data, columns=["Asset ID","Location","Generator Type",
                                             "Project Name","Installed Capacity", "Owner", "Longitude", "Latitude",])

    lons, lats = [], []

    for lon, lat in list(zip(point_data["Longitude"], point_data["Latitude"])):
        x, y = transform(outProj, inProj, lon, lat)
        lons.append(x)
        lats.append(y)

    point_data["MercatorX"] = lons
    point_data["MercatorY"] = lats

    colour1 = factor_cmap('Generator Type', palette=Spectral11, factors=sorted(point_data['Generator Type'].unique()))

    colour2 = linear_cmap(field_name='Installed Capacity', palette=Spectral11, low=min(point_data['Installed Capacity']),
                         high=max(point_data['Installed Capacity']))


    if size_input == "Capacity":
        # changing size... kinda works
        #need a log algorithum for size to fix the disparity between small and large generators
        point_data['size'] = pow(point_data['Installed Capacity'],0.5)
        Size = 'size'
    else:
        Size=15

    if Viz_Colour == "Capacity":
        colour = colour2
        color_bar = ColorBar(color_mapper=colour2['transform'], label_standoff=12, title='Capacity')
        Legend_Visibility = False
        p.add_layout(color_bar, 'right')

    else:
        colour=colour1
        Legend_Visibility = True

    source = ColumnDataSource(point_data)
    p.circle(x="MercatorX", y="MercatorY", size=Size, line_color='black', fill_color=colour,
             fill_alpha=0.8, source=source, legend_group='Generator Type')

    p.legend.location = 'top_left'
    p.legend.click_policy = 'mute'
    p.legend.visible = Legend_Visibility
    p.yaxis.formatter = NumeralTickFormatter(format="00")

    #have to add the wheel zoom tool spprately to trun off the zoom on axis feature
    p.add_tools(WheelZoomTool(zoom_on_axis=False))
    p.toolbar.active_scroll = p.select_one(WheelZoomTool)
    return(p)

def transmission_network(line_data,shape):
    '''this function creates a network graph based on transmission line information. The networkx library is used to
    create a graph that is then plotted with Bokeh functions. Bokeh interactions are used for highlighting connections.
    the layout is selected as an input to the function, and networkx built in layouts can be selected to
    locate the nodes in the figure '''

    df1 = line_data.iloc[:, 0:2]
    df1['node_atribute'] = df1['from']

    G = nx.from_pandas_edgelist(df1, source='from', target='to')

    p = Plot(plot_width=700, plot_height=700,
                x_range=Range1d(-1.1, 1.1), y_range=Range1d(-1.1, 1.1))
    p.title.text = "Transmission Network Graph"

    p.add_tools(HoverTool(tooltips=None), TapTool(), BoxSelectTool())

    #using nx spring layout. but the goal woluld be to use bokeh StaticLayoutProvider with x and y mercator coordinates

    if shape == 1:
        layout = nx.spring_layout
    else:
        layout = nx.circular_layout


    graph_renderer = from_networkx(G, layout_function=layout, scale=1, center=(0, 0))

    graph_renderer.node_renderer.glyph = Circle(size=15, fill_color=Spectral4[0])
    graph_renderer.node_renderer.selection_glyph = Circle(size=15, fill_color=Spectral4[2])
    graph_renderer.node_renderer.hover_glyph = Circle(size=15, fill_color=Spectral4[1])

    graph_renderer.edge_renderer.glyph = MultiLine(line_color="#CCCCCC", line_alpha=0.8, line_width=2)
    graph_renderer.edge_renderer.selection_glyph = MultiLine(line_color=Spectral4[2], line_width=2)
    graph_renderer.edge_renderer.hover_glyph = MultiLine(line_color=Spectral4[1], line_width=2)


    graph_renderer.selection_policy = NodesAndLinkedEdges()
    graph_renderer.inspection_policy = EdgesAndLinkedNodes()

    p.renderers.append(graph_renderer)

    pos = graph_renderer.layout_provider.graph_layout
    x, y = zip(*pos.values())

    node_labels = list(G.node)

    source = ColumnDataSource({'x': x, 'y': y, 'label': [node_labels[i] for i in range(len(x))]})
    labels = LabelSet(x='x', y='y',x_offset=5,y_offset=5, text='label',text_font_size="8pt", angle=0, source=source)

    p.renderers.append(labels)

    return(p)

def Gen_inspector(UC_Results, UC_Map):

    '''This function takes the UC resutls data and the map dataframes and returns the columns of the data with
    the names of each generator so that it each generator can be plotted individually. The function also returns
    a list of generator bus names so that the streamlit app can provide a data selector to sub select generators
    from the list'''

    # make a dictonary with generator type and rename the columns
    dict_UC_Map = UC_Map['bus'].to_dict()
    UC_Results_gens = UC_Results.rename(columns=dict_UC_Map)

    UC_Results_gens = UC_Results_gens.groupby(level=0,axis=1).sum()

    bus_names = list(UC_Results_gens.columns.values)
    print(bus_names)
    return(UC_Results_gens,bus_names)

def plot_Gens(Gen_data,bus_names):
    '''This function takes the UC_results data and a string with the generator names that will be plot as
    multiple lines on a single bokeh figure. '''

    #trim Gen_data columns to bus_names
    cols = bus_names
    Gen_data_trimmed = Gen_data.loc[:,cols]

    TOOLTIPS = [("hour", "$index"),
                ("Energy generated ", "$y MWH"), ]
    width = 1500
    height = 500
    title = 'Generator Inspector'
    p = figure(plot_width=width, plot_height=height, x_axis_type='datetime', x_axis_label='Time', y_axis_label='MWH',
               title=title, tooltips=TOOLTIPS, tools="box_zoom, pan, hover, crosshair, reset", toolbar_location="left", active_drag="box_zoom")
    p.grid.minor_grid_line_color = '#eeeeee'

    colors = itertools.cycle(Spectral11)
    for i in Gen_data_trimmed.columns:
        p.line(x=Gen_data_trimmed.index, y=Gen_data_trimmed[i], line_color=next(colors), line_width=2,legend_label = i)

    # move the legend entries to match the stacked order
    p.legend.location = 'top_left'
    p.legend.click_policy = 'mute'
    p.yaxis.formatter = NumeralTickFormatter(format="00")
    return (p)

# ----------------------------------------------------------------------------------------------------------------------
def main():
    #test individual functions here when running this script in an IDE
    x=1
if __name__ == "__main__":
    main()