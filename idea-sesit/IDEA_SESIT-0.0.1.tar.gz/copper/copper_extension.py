from bokeh.models.annotations import ColorBar
from bokeh.models.sources import ColumnDataSource
from bokeh.plotting import figure
from bokeh.io import output, show, output_file, save
from bokeh.palettes import Bokeh5
from jinja2.nodes import Output
import pandas as pd

##========= Import the data from Data_summary ============## 
def import_data_summary():
    data_summary = pd.read_csv('Data_summary.csv', index_col=0, skiprows=range(6,16), usecols=range(0,6))
    return data_summary

def plot_carbon_limit_data(data_summary):
    plot = figure(title="With Carbon Limit", x_axis_label='Year', y_axis_label='Emission (Mt CO2)')

    for row, name, color in zip(range(0,5),["$0/tonne", "$50/tonne", "$100/tonne", "$150/tonne", "$200/tonne"], Bokeh5):
        plot.line(x=data_summary.columns, y=data_summary.iloc[row], line_width=3, legend_label=name, color=color)
        plot.circle(x=data_summary.columns, y=data_summary.iloc[row], size=10, color=color, legend_label=name)
    
    plot.legend.location = "top_left"
    plot.legend.click_policy="hide"
    return plot
    
def plot_total_o_p():
    data = pd.read_csv('Data_summary.csv', index_col=0, skiprows=range(6,16), usecols=[9,11])
    bar_plot = figure(title="Total Operation and Planning Cost", x_axis_label='Carbon Tax($/tonne)', y_axis_label='Normalized Cost')
    bar_plot.vbar(data.index, top=data['normalized'], width=10, color=Bokeh5)
    return bar_plot

    
def main():
    data_summary = import_data_summary()  
    carbon_plot = plot_carbon_limit_data(data_summary)
    cost_plot = plot_total_o_p()

    output_file('plots/carbon_plot.html')
    save(carbon_plot)
    output_file('plots/cost_plot.html')
    save(cost_plot)
    
if __name__ == "__main__":
    main()