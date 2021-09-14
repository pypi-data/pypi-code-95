import pandas as pd, numpy as np
from dorianUtils.configFilesD import ConfigDashTagUnitTimestamp
import subprocess as sp, os,re,glob, datetime as dt
from dateutil import parser
pd.options.mode.chained_assignment = None  # default='warn'

class ConfigFilesSmarthyes(ConfigDashTagUnitTimestamp):
    # ==========================================================================
    #                       INIT FUNCTIONS
    # ==========================================================================

    def __init__(self,folderPkl,folderFig=None,folderExport=None,encode='utf-8'):
        confFolder = os.path.dirname(os.path.realpath(__file__))+'/confFiles/'
        super().__init__(folderPkl,confFolder,folderFig=folderFig,folderExport=folderExport)
        self._buildDfPLC()
        self.unitCol,self.descriptCol,self.tagCol = self._getPLC_ColName()
        self.usefulTags=self.usefulTags.fillna('')
        self.usefulTags = self._buildAutoGroups()

    def _buildAutoGroups(self):
        autoGroups = np.unique([k[:-3] for k in self.dfPLC.TAG])
        groups,units,predefCat=[],[],[]
        for k in autoGroups:
            tagsInGroup= self.getTagsTU(k,'')
            if len(tagsInGroup)>0:
                allUnits,idxs = np.unique([self.getUnitofTag(k) for k in tagsInGroup],return_index=True)
                for u,i in zip(allUnits,idxs):
                    units.append(u)
                    groups.append(k)
                    predefCat.append(k+'_'+u)
        autoGroups = pd.DataFrame([predefCat,groups,units]).transpose()
        autoGroups.columns = ['predefinedCategories','Pattern','Unit']
        return autoGroups.set_index('predefinedCategories')

    def _buildDfPLC(self):
        self.dfPLC.columns = [k.upper() for k in self.dfPLC.columns]

    # def _loadDFTagsDay(self,datum,listTags,parked,pool,raw=False):
    #     ConfigDashTagUnitTimestamp._loadDFTagsDay()
