from bokeh.models.sources import ColumnDataSource, ColumnarDataSource
from bokeh.plotting import figure, show
from bokeh.io import output_file, save
from bokeh.palettes import Spectral4
import openpyxl
from openpyxl import load_workbook
import pandas as pd

##========= Import the data from Data_summary ============## 
def import_data_summary():
    data_summary = pd.read_csv('Data_summary.csv', index_col=0, skiprows=range(6,16), usecols=range(0,6))
    return data_summary

def plot_carbon_limit_data(data_summary):
    plot = figure(title="With Carbon Limit", x_axis_label='Year', y_axis_label='Emission (Mt CO2)')
    source = ColumnDataSource(data_summary)

    for row, name, color in zip(range(0,4),["$0/tonne", "$100/tonne", "$150/tonne", "$200/tonne"], Spectral4):
        plot.line(x=data_summary.columns, y=data_summary.iloc[row], line_width=3, legend_label=name, color=color)
        plot.circle(x=data_summary.columns, y=data_summary.iloc[row], size=10, color=color, legend_label=name)
    
    plot.legend.location = "top_left"
    plot.legend.click_policy="hide"
    output_file("plots/copper_data_summary.html")
    save(plot)
    return
    


def main():
    data_summary = import_data_summary()
    
    plot_carbon_limit_data(data_summary)

if __name__ == "__main__":
    main()