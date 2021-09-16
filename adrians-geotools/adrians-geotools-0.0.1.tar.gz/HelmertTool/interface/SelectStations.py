import tkinter as tk 
import pandas as pd 
import tkinter.ttk as ttk 
from HelmertTool.io import get_path
class SelectStationsWindow(tk.Tk):
    
    def __init__(self, master, *args, **kwargs):
        super().__init__()
        self.master = master
        self.stations = master.stations
        self.resizable(height=False, width=False)
        self.title("Select stations")
        
        self.init_rows_and_header_frame()
        self.rows = {}
        self.use_default_stations = True
        self.default_stations = self.load_default_stations()

        for station in self.stations.itertuples():
            row = SelectStationsRow(self.rows_frame, station, self.set_selection)            
            self.rows[station.Index] = row
        
        self.header_frame.columnconfigure(0, minsize=70)
        self.header_frame.columnconfigure(1, minsize=100)
        self.header_frame.columnconfigure(2, minsize=30)

        self.rows_frame.columnconfigure(0, minsize=70)
        self.rows_frame.columnconfigure(1, minsize=100)
        self.rows_frame.columnconfigure(2, minsize=30)


        tk.Label(self.header_frame, text = "Select stations",font=("helvetica", 12)).grid(row=0, column=0, columnspan=2, pady=5, padx=5)
        ttk.Button(self.header_frame, text = "Default", command = self.toggle_default_stations).grid(row=0, column=2)
        ttk.Label(self.header_frame, text = "Select").grid(row=1, column=0, pady=5)
        ttk.Button(self.header_frame, text = "Station name", command = self.sort_by_name).grid(row=1, column=1)
        ttk.Button(self.header_frame, text = "Sigma", command = self.sort_by_sigma).grid(row=1, column=2)
        self.grid()

        self.bind_all("<Up>", self.scroll_up)
        self.bind_all("<Down>", self.scroll_down)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.grab_set()

    def scroll_up(self, *args):
        self.canvas.yview_scroll(-5, "units")

    def scroll_down(self, *args):
        self.canvas.yview_scroll(5, "units")
    
    def on_close(self):
        #self.master.new_helmert_transform()
        self.destroy()

    def grid(self):
        for row_index, station_index in enumerate(self.stations.index):  
            self.rows[station_index].grid(row_index)

    def set_selection(self, index, value):
        self.stations.at[index, "Selected"] = value

    def sort_by_name(self):
        self.stations = self.stations.sort_values(by="Station_Name")
        #self.master.stations = self.stations
        self.grid()

    def sort_by_sigma(self):
        self.stations = self.stations.sort_values(by="Sigma")
        #self.master.stations = self.stations
        self.grid()

    def init_rows_and_header_frame(self):
        header_canvas = tk.Canvas(self, highlightthickness=0, height=65, width=250) #!Hardcoded height
        header_canvas.grid(row=0, column=0, sticky="news")
        self.canvas = tk.Canvas(self, highlightthickness=0, height=700, width=250)
        self.canvas.grid(row=1, column=0, sticky="news")

        def xview(*args):
            self.canvas.xview(*args)
            header_canvas.xview(*args)

        self.yscrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.yscrollbar.grid(row=1, column=1, sticky = "ns")
        self.xscrollbar = tk.Scrollbar(self, orient="horizontal", command=xview)
        self.xscrollbar.grid(row=2, column=0, sticky = "we")

        self.canvas.configure(yscrollcommand=self.yscrollbar.set, xscrollcommand=self.xscrollbar.set)
        header_canvas.configure(xscrollcommand=self.xscrollbar.set)

        self.rows_frame = tk.Frame(self.canvas)
        self.header_frame = tk.Frame(header_canvas)
        self.canvas.create_window((0, 0), window=self.rows_frame, anchor="nw")   
        header_canvas.create_window((0, 0), window=self.header_frame, anchor="nw")
        
        def scroll_config(*args):
            """Sets scroll region for table and header"""
            region = (0,0, header_canvas.bbox("all")[2], self.canvas.bbox("all")[3])
            self.canvas.configure(scrollregion=region)
            header_canvas.configure(scrollregion=header_canvas.bbox("all"))

        self.rows_frame.bind("<Configure>", scroll_config)
        self.header_frame.bind("<Configure>", scroll_config)

    def toggle_default_stations(self, *args):
        
        if self.use_default_stations:
            for row in self.rows.values():
                row.var.set(row.station.Station_Name in self.default_stations.values)
            self.use_default_stations = False
        else:
            for row in self.rows.values():
                row.var.set(True)
            self.use_default_stations = True

    def load_default_stations(self):
        return pd.read_fwf(get_path("transform_sites.txt"), header = None)

class SelectStationsRow():

    def __init__(self, master, station, set_selection, *args, **kwargs):

        self.master = master 
        self.set_selection = set_selection
        self.station = station

        self.var = tk.BooleanVar(self.master, value = station.Selected)
        self.var.trace("w", lambda *args: self.set_selection(station.Index, self.var.get()))

        self.check = ttk.Checkbutton(self.master, variable=self.var, onvalue=True, offvalue=False)
        self.station_name_label = tk.Label(self.master, text = station.Station_Name)
        self.sigma_label = tk.Label(self.master, text = round(station.Sigma,3))
   
    def grid(self, row):
        self.check.grid_forget()
        self.check.grid(row=row, column=0, sticky="ew", padx=23)
        self.station_name_label.grid_forget()
        self.station_name_label.grid(row=row, column=1, sticky="w", padx=10)
        self.sigma_label.grid_forget()
        self.sigma_label.grid(row=row, column=2, sticky="w", padx=10)
