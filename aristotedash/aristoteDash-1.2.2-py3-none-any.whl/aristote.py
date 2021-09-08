'''Le logiciel principal de calcul de la prévision de production PV'''
import numpy as np,datetime as dt,pytz,pandas as pd,os
from geopy.geocoders import Nominatim
from tzwhere import tzwhere
from dorianUtils.utilsD import Utils
class ConfigAristote():
    def __init__(self):
        self.name='configAristote'
        self.geolocator = Nominatim(user_agent="Dorian",timeout=4)
        self.tz = tzwhere.tzwhere()
        self.utils=Utils()
        self.appDir  = os.path.dirname(os.path.realpath(__file__))
        self.confFolder = self.appDir +'/confFiles/'

# ==============================================================================
#                               FORMULAS
# ==============================================================================
    def nombreJoursAnnee(self,myYear):
            return (dt.datetime(myYear,1,1)-dt.datetime(myYear-1,1,1)).days

    def indiceJourJ(self,myDate):
            firstDay=pd.Timestamp(str(myDate.year)+'-1-1',tz=myDate.tz)
            return (myDate-firstDay).days

    def irradiance(self,jourJ, nbj):
            return 1367 * (1 - 0.034 * np.sin((2 * np.pi * (jourJ - 94) / nbj)))

    def timeEquation(self,jourJ, nbj):
            Temp = 2 * np.pi * (jourJ - 81) / nbj
            return -9.87 * np.sin(2 * Temp) + 7.53 * np.cos(Temp) + 1.5 * np.sin(Temp)

    def heureVraie(self,heureUTC, longituderad, equationTemps):
            hv = heureUTC.hour - longituderad * 24 / (2 * np.pi) - equationTemps / 60
            if hv < 0 : hv = hv + 24
            return hv

    def angleHoraire(self,heureVraie):
            return 0.2618 * (heureVraie - 12)

    def declinaison(self,jourJ, nbj):
            return 0.4093 * np.sin(2 * np.pi * (jourJ + 284) / nbj)

    def hauteurAngulaire(self,declinaison, latituderad, angleHoraire):
        return np.max([np.arcsin(np.sin(declinaison) * np.sin(latituderad) + np.cos(declinaison) * np.cos(latituderad) * np.cos(angleHoraire)), 0])

    def azimut(self,dec, h, latituderad, Ah):
        return np.arcsin(np.cos(dec)*np.sin(Ah)/np.cos(h))

    def azimut_v1_wrong(self,declinaison, hauteurAngulaire, latituderad, angleHoraire):
        Temp = np.arccos((-np.sin(declinaison) * np.cos(latituderad) + np.sin(latituderad) * np.cos(angleHoraire) * np.cos(declinaison)) / np.cos(hauteurAngulaire))
        if angleHoraire < 0 : Temp = -Temp
        return -Temp

    def coeffIncidence_v2(self,inclinaison, orientation, azimut, hauteurAng):
            temp = -np.sin(inclinaison) * np.sin(orientation) * np.sin(azimut)
            temp = temp + np.cos(orientation) * np.sin(inclinaison) * np.cos(azimut)
            temp = temp + np.cos(inclinaison) * np.sin(hauteurAng)
            return np.max([temp, 0])

    def coeffIncidence(self,i,o,a,Ah):
            self.utils.printListArgs(i,o,a,Ah)
            return np.sin(Ah)*np.cos(i) + np.sin(a)*np.sin(i)*np.sin(o)*np.cos(Ah) + np.sin(i)*np.cos(Ah)*np.cos(a)*np.cos(o)

    def findFormulaIncidence(self):
        import sympy as sy
        o,a,i,Ah=sy.symbols('o a i Ah')
        M1=sy.Matrix([[sy.cos(o),-sy.sin(o),0],[sy.sin(o),sy.cos(o),0],[0,0,1]])
        Z=sy.Matrix([sy.cos(Ah)*sy.sin(a),sy.cos(Ah)*sy.cos(a),sy.sin(Ah)])
        M2 = sy.Matrix([[1,0,0],[0,sy.cos(i),-sy.sin(i)],[0,sy.sin(i),sy.cos(i)]])
        Zseconde = M2*M1*Z

# ==============================================================================
#                     COMPUTE FROM CONFIGURATION
# ==============================================================================
    def getLongLat(self,address):
        location = self.geolocator.geocode(address)
        return location.latitude,location.longitude

    def declinaison_fromConf(self,myDate):
        jourJ  = self.indiceJourJ(myDate)
        nbj    = self.nombreJoursAnnee(myDate.year)
        return self.declinaison(jourJ, nbj)

    def heureVrai_fromConf(self,myDate,longitude,latitude):
        jourJ = self.indiceJourJ(myDate)
        nbj = self.nombreJoursAnnee(myDate.year)
        equationTemps = self.timeEquation(jourJ, nbj)
        heureUTC     = myDate.tz_convert('UTC')
        longituderad,latituderad = longitude*np.pi/180,latitude*np.pi/180
        return self.heureVraie(heureUTC, longituderad, equationTemps)

    def angleHoraire_fromConf(self,myDate,longitude,latitude):
        heureVraie   = self.heureVrai_fromConf(myDate,longitude,latitude)
        return self.angleHoraire(heureVraie)

    def getHauteurAngulaIre_fromConf(self,myDate,longitude,latitude):
        latituderad = latitude*np.pi/180
        declinaison  = self.declinaison_fromConf(myDate)
        angleHoraire = self.angleHoraire_fromConf(myDate,longitude,latitude)
        return self.hauteurAngulaire(declinaison, latituderad, angleHoraire)

    def getAzimut_fromConf(self,myDate,longitude,latitude):
        declinaison  = self.declinaison_fromConf(myDate)
        hauteurAng = self.getHauteurAngulaIre_fromConf(myDate,longitude,latitude)
        latituderad = latitude*np.pi/180
        angleHoraire = self.angleHoraire_fromConf(myDate,longitude,latitude)
        return self.azimut(declinaison, hauteurAng, latituderad, angleHoraire)

    def coefIncidence_fromConf(self,myDate,longitude,latitude,inclinaison,orientation):
        azimut=self.getAzimut_fromConf(myDate,longitude,latitude)
        hauteurAng = self.getHauteurAngulaIre_fromConf(myDate,longitude,latitude)
        return self.coeffIncidence_v2(inclinaison*np.pi/180, orientation*np.pi/180, azimut, hauteurAng)

    def irradiance_fromConf(self,myDate):
        jourJ = self.indiceJourJ(myDate)
        nbj = self.nombreJoursAnnee(myDate.year)
        return self.irradiance(jourJ, nbj)

    def calculPmaxTheorique(self,surface,myDate,longitude,latitude,inclinaison,orientation):
        E = self.irradiance_fromConf(myDate)
        coeffIncidence_v2 = self.coefIncidence_fromConf(myDate,longitude,latitude,inclinaison,orientation)
        return surface * E * coeffIncidence_v2

    def puissance_PV(self,surface,myDate,longitude,latitude,inclinaison,orientation,rendement):
        return rendement*self.calculPmaxTheorique(surface,myDate,longitude,latitude,inclinaison,orientation)

# ==============================================================================
#                               GRAPHICS
# ==============================================================================
    def timespace(self,timeRange,N=100):
        start,end = [pd.Timestamp(k) for k in timeRange]
        t = np.linspace(start.value, end.value, N)
        return pd.to_datetime(t)

    def PV_timeSeries(self,timeRange,surface=1.6*1.02,longitude=5.635,latitude=45.456,
                                inclinaison=45,orientation=0,rendement=19.2,freqCalc='60s'):
        try : local_tz = self.tz.tzNameAt(latitude,longitude)
        except : local_tz='Europe/Paris'
        times = pd.date_range(start=timeRange[0],end=timeRange[1], freq=freqCalc,tz=local_tz)
        irradiances = [self.irradiance_fromConf(k) for k in times]
        coeffIncidences = [self.coefIncidence_fromConf(k,longitude,latitude,inclinaison,orientation) for k in times]
        puissanceMaxTh = [self.calculPmaxTheorique(surface,k,longitude,latitude,inclinaison,orientation)/1000 for k in times]
        puissancesPV = [rendement/100*k for k in puissanceMaxTh]

        df = pd.DataFrame([times,irradiances,coeffIncidences,puissanceMaxTh,puissancesPV]).transpose()
        df.columns = ['timestamp','irradiance(W/m2)',"coefficient d'incidence",
        'puissance théorique max(kW)','puissance PV (kW)']
        df = df.set_index('timestamp')
        return df

    def check_timeSeries(self,timeRange,longitude=5.635,latitude=45.456,
                                inclinaison=45,orientation=0,freqCalc='60s'):
        try : local_tz = self.tz.tzNameAt(latitude,longitude)
        except : local_tz='Europe/Paris'
        times = pd.date_range(start=timeRange[0],end=timeRange[1], freq=freqCalc,tz=local_tz)
        declinaisons = [self.declinaison_fromConf(k)*180/np.pi for k in times]
        heures_vrais = [self.heureVrai_fromConf(k,longitude,latitude) for k in times]
        angles_horaires = [self.angleHoraire_fromConf(k,longitude,latitude)*180/np.pi for k in times]
        hauteurs_angulaires = [self.getHauteurAngulaIre_fromConf(k,longitude,latitude)*180/np.pi for k in times]
        azimuts = [self.getAzimut_fromConf(k,longitude,latitude)*180/np.pi for k in times]
        df = pd.DataFrame([times,declinaisons,heures_vrais,angles_horaires,hauteurs_angulaires,azimuts]).transpose()
        df.columns = ['timestamp','declinaison(°)','heure vraie',
                        'angle horaire(°)','hauteur angulaire(°)','azimut(°)']
        df = df.set_index('timestamp')
        return df

    def energy_PV_timeSeries(self,timeRange,surface=1.6*1.02,longitude=5.635,latitude=45.456,
                                inclinaison=45,orientation=0,rendement=19.2,period='1d',freqCalc='60s'):

        try : local_tz = self.tz.tzNameAt(latitude,longitude)
        except : local_tz='Europe/Paris'
        times = pd.date_range(start=timeRange[0],end=timeRange[1], freq=freqCalc,tz=local_tz)
        puissanceMaxTh = [self.calculPmaxTheorique(surface,k,longitude,latitude,inclinaison,orientation)/1000 for k in times]
        puissancesPV = [rendement/100*k for k in puissanceMaxTh]
        df = pd.DataFrame(puissancesPV,index=times)
        df = df.resample(period).sum()*df.index.freq.delta.total_seconds()
        df.columns=['energie produite(kWh)']
        return df

    def plot_energy_timeSeries(self,timeRange,**kwargs):
        import plotly.express as px
        df = self.energy_PV_timeSeries(timeRange,**kwargs)
        fig = px.bar(df,title='énergie produite par les PVs')
        fig.update_layout(yaxis_title='énergie en kWh')
        fig.update_layout(bargap=0.5)

        nbDays=(df.index[-1]-df.index[0]).days
        energieTotale=df.sum()[0]/1000
        txt = " Energie totale produite :  {:.2f} MWh \n Nombres de jours {:.0f}"

        fig.add_annotation(x=0.95, y=0.98,
        xref="x domain", yref="y domain",
        font=dict(
            family="Courier New, monospace",
            size=20,
            color="red"
            ),
        text=txt.format(energieTotale,nbDays),

        showarrow=False)

        return fig
