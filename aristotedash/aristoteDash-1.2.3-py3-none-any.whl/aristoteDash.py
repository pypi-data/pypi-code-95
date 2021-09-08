from dorianUtils.dashTabsD import TabMaster
import dash_html_components as html
import dash_core_components as dcc
from . import aristote
import dash
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go


class AristoteMaster(TabMaster):
    def __init__(self,app,baseId='ad0_'):
        TabMaster.__init__(self,app,baseId)
        self.lieux = ['le cheylas','saint-joachim','saint-geoire en valdaine','paris']
    def addWidgets(self,dicWidgets):
        widgetLayout,dicLayouts = [],{}
        for wid_key,wid_val in dicWidgets.items():
            if 'dd_lieu' in wid_key:
                widgetObj = self.dccE.dropDownFromList(self.baseId+wid_key,self.lieux,'lieu : ',value = wid_val)

            elif 'in_lieu' in wid_key:
                widgetLong = [html.P('longitude :'),dcc.Input(self.baseId+'in_long',type='number',step=0.0001,min=-180,max=180)]
                widgetLat = [html.P('latitude :'),dcc.Input(self.baseId+'in_lat',type='number',step=0.0001,min=-90,max=90)]
                # widgetAlt = [html.P('altitude:'),dcc.Input(self.baseId+'in_alt',type='number',step=0.0001,min=0,max=8000)]
                widgetObj = [self.dccE.build_dbcBasicBlock(w,2,1) for w in [widgetLong,widgetLat]]

            elif 'in_surface' in wid_key:
                widgetObj = [self.dccE.build_dbcBasicBlock(
                        [html.P('surface en m2:'),
                        dcc.Input(self.baseId+wid_key,type='number',step=0.01,min=0,max=100000,value=wid_val)],2,1)]

            elif 'in_rendement' in wid_key:
                widgetObj = [self.dccE.build_dbcBasicBlock([
                        html.P('rendement en %:'),
                        dcc.Input(self.baseId+wid_key,type='number',step=0.01,min=0,max=20,value=wid_val)],2,1)]

            elif 'in_inclinaison' in wid_key:
                widgetObj = [self.dccE.build_dbcBasicBlock([
                        html.P('inclinaison en °:'),
                        dcc.Input(self.baseId+wid_key,type='number',step=0.01,min=0,max=90,value=wid_val)],2,1)]

            elif 'in_orientation' in wid_key:
                widgetObj = [self.dccE.build_dbcBasicBlock([
                        html.P('orientation en °:'),
                        dcc.Input(self.baseId+wid_key,type='number',step=0.01,min=-90,max=90,value=wid_val)],2,1)]

            elif 'in_freq' in wid_key:
                widgetObj = [self.dccE.build_dbcBasicBlock([
                        html.P('frequence :'),
                        dcc.Input(self.baseId+wid_key,type='text',value=wid_val)],2,1)]

            elif 'in_period' in wid_key:
                widgetObj = [self.dccE.build_dbcBasicBlock([
                        html.P('periode :'),
                        dcc.Input(self.baseId+wid_key,type='text',value=wid_val)],2,1)]

            elif 'dd_plot' in wid_key:
                widgetObj = self.dccE.dropDownFromList(self.baseId+wid_key,['puissance','check'],'graph : ',value = wid_val)

            else :
                print('component ',wid_key,' is not available')
                return

            for widObj in widgetObj:widgetLayout.append(widObj)
        return widgetLayout

class PowerTab(AristoteMaster):
    def __init__(self,app,baseId='apd0_'):
        AristoteMaster.__init__(self,app,baseId)
        self.tabname = 'power'
        self.tabLayout = self._buildLayout()
        self.cfg = aristote.ConfigAristote()
        self._define_callbacks()

    def _buildLayout(self,widthG=88,tagCatDefault=None):
        dicBasicWidgets = {
                    'pdr_time' : {'tmin':'2010-01-01','tmax':'2022-12-31'},
                    'dd_style':'lines+markers','dd_typeGraph':'scatter',
                    'dd_cmap':'jet'
                    }
        dicSpecialWidgets = {
                    'dd_lieu':'le cheylas',
                    'in_lieu':'',
                    'in_surface':100,
                    'in_rendement':19,
                    'in_inclinaison':25,
                    'in_orientation':0,
                    'in_freq':'3600s',
                    'dd_plot':'puissance',
                    }
        basicWidgets = self.dccE.basicComponents(dicBasicWidgets,self.baseId)
        specialWidgets = self.addWidgets(dicSpecialWidgets)
        widgetLayout = specialWidgets+ basicWidgets
        return self.dccE.buildGraphLayout(widgetLayout,self.baseId,widthG=widthG)

    def _define_callbacks(self):

        @self.app.callback(
                            Output(self.baseId + 'in_lat', 'value'),
                            Output(self.baseId + 'in_long', 'value'),
                            Input(self.baseId + 'dd_lieu','value'))

        def updateLongLat(lieu):
            longlat = self.cfg.getLongLat(lieu)
            return longlat

        listInputsGraph = {
                        'pdr_timeBtn':'n_clicks',
                        'in_long':'value',
                        'in_lat':'value',
                        'in_surface':'value',
                        'in_rendement':'value',
                        'in_inclinaison':'value',
                        'in_orientation':'value',
                        'dd_typeGraph':'value',
                        'dd_cmap':'value',
                        'dd_style':'value',
                        'dd_plot':'value'
                        }
        listStatesGraph = {
                            'in_freq':'value',
                            'graph':'figure',
                            'pdr_timeStart' : 'value',
                            'pdr_timeEnd':'value',
                            'pdr_timePdr':'start_date',
                            }
        @self.app.callback(
        Output(self.baseId + 'graph', 'figure'),
        Output(self.baseId + 'pdr_timeBtn', 'n_clicks'),
        [Input(self.baseId + k,v) for k,v in listInputsGraph.items()],
        [State(self.baseId + k,v) for k,v in listStatesGraph.items()],
        State(self.baseId+'pdr_timePdr','end_date'))
        def updateGraph(timeBtn,long,lat,surface,rendement,inclinaison,orientation,
                        typeGraph,colmap,style,plot,freq,fig,date0,date1,t0,t1):
            ctx = dash.callback_context
            trigId = ctx.triggered[0]['prop_id'].split('.')[0]
            # to ensure that action on graphs only without computation do not
            # trigger computing the dataframe again
            listTriggers = ['in_long','in_lat','in_surface','in_rendement','in_inclinaison','in_orientation','pdr_timeBtn']
            if not timeBtn or trigId in [self.baseId+k for k in listTriggers] :
                timeRange   = [date0+' '+t0,date1+' '+t1]
                if plot == 'puissance':
                    df = self.cfg.PV_timeSeries(timeRange,surface,long,lat,inclinaison,orientation,rendement,freq)
                elif plot == 'check':
                    df = self.cfg.check_timeSeries(timeRange,long,lat,inclinaison,orientation,freq)
                fig = self.utils.multiUnitGraph(df)
                fig.update_yaxes(showgrid=False)
            else :fig = go.Figure(fig)
            fig = self.utils.updateStyleGraph(fig,style,colmap)
            fig.update_layout(height=1000)
            return fig,timeBtn

class EnergyTab(AristoteMaster):
    def __init__(self,app,baseId='aed0_'):
        AristoteMaster.__init__(self,app,baseId)
        self.tabname = 'energy'
        self.tabLayout = self._buildLayout()
        self.cfg = aristote.ConfigAristote()
        self._define_callbacks()

    def _buildLayout(self,widthG=88,tagCatDefault=None):
        dicBasicWidgets = {
                    'pdr_time' : {'tmin':'2010-01-01','tmax':'2022-12-31'},
                    }
        dicSpecialWidgets = {
                    'dd_lieu':'le cheylas',
                    'in_lieu':'',
                    'in_surface':100,
                    'in_rendement':19,
                    'in_inclinaison':25,
                    'in_orientation':0,
                    'in_freq':'3600s',
                    'in_period':'1d',
                    'dd_plot':'puissance',
                    }
        basicWidgets = self.dccE.basicComponents(dicBasicWidgets,self.baseId)
        specialWidgets = self.addWidgets(dicSpecialWidgets)
        widgetLayout = specialWidgets+ basicWidgets
        return self.dccE.buildGraphLayout(widgetLayout,self.baseId,widthG=widthG)

    def _define_callbacks(self):

        @self.app.callback(
                            Output(self.baseId + 'in_lat', 'value'),
                            Output(self.baseId + 'in_long', 'value'),
                            Input(self.baseId + 'dd_lieu','value'))

        def updateLongLat(lieu):
            longlat = self.cfg.getLongLat(lieu)
            return longlat

        listInputsGraph = {
                        'pdr_timeBtn':'n_clicks',
                        'in_long':'value',
                        'in_lat':'value',
                        'in_surface':'value',
                        'in_rendement':'value',
                        'in_inclinaison':'value',
                        'in_orientation':'value',
                        }
        listStatesGraph = {
                            'in_freq':'value',
                            'in_period':'value',
                            'pdr_timeStart' : 'value',
                            'pdr_timeEnd':'value',
                            'pdr_timePdr':'start_date',
                            }
        @self.app.callback(
        Output(self.baseId + 'graph', 'figure'),
        [Input(self.baseId + k,v) for k,v in listInputsGraph.items()],
        [State(self.baseId + k,v) for k,v in listStatesGraph.items()],
        State(self.baseId+'pdr_timePdr','end_date'))
        def updateGraph(timeBtn,long,lat,surface,rendement,inclinaison,orientation,
                            freqCalc,period,date0,date1,t0,t1):
            timeRange = [date0+' '+t0,date1+' '+t1]
            fig = self.cfg.plot_energy_timeSeries(timeRange,surface=surface,longitude=long,latitude=lat,
                                        inclinaison=inclinaison,orientation=orientation,rendement=rendement,
                                        period=period,freqCalc=freqCalc)
            fig.update_layout(height=1000)
            return fig
