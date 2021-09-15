###########
#TO DO ####

# mutations que sur les noeuds du modèle pour gagner du temps ?
# intégrer banque de donnée 2020+
# changer dans compare_survival pour direct utiliser final_states et pas avoir à run plot_piechart avant
# 

###########

import pandas as pd
import maboss
from sklearn import mixture
from sklearn.impute import SimpleImputer
from scipy import stats
from  scipy.stats import kurtosis, median_abs_deviation
from unidip.dip import diptst 
import scanpy as sc
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sb
#help(kurtosis)


def percent_0s(df, axis=0):
    n_0s = np.sum(df==0, axis=axis)
    return n_0s/df.shape[axis]

def discard_percent_0s(df, max_percent=0.95,axis=0):
    p_0s = percent_0s(df, axis=axis)
    if axis==0:
        df_filt = df.transpose()[p_0s<=max_percent]
        return df_filt.transpose()
    else:
        return df[p_0s<=max_percent]
    
#function combinating the three methods to define binarizable variables used in PROFILE
def binarizable(df, bi_min=None, kurtosis_max=None, diptest_max=None, return_df=False):
    df_ = df.copy()
    if (bi_min==None) & (kurtosis_max==None) & (diptest_max==None):
        print('No filter will be applied since no threshold has been precised.')
        return None
    if bi_min != None:
        df_ = df_.transpose()[df_.bimodality_index()>=bi_min].transpose()
    if kurtosis_max != None:
        df_ = df_.transpose()[kurtosis(df_)<kurtosis_max].transpose()
    if diptest_max!=None:
        df_ = df_.transpose()[diptest(df_)<diptest_max].transpose()
    if return_df==False:
        return df_.columns
    else:
        return df_

#method to calculate the bimodality index for all the variables of a dataframe
def bimodality_index(df, axis=0):
    #don't forget that mixture gives a dofferent result at each run since the process starts from a random state.
    BIs = []
    if axis==0:
        for i in range(df.shape[1]):            
            g = mixture.GaussianMixture(n_components=2)
            g.fit(np.array(df.iloc[:,i]).reshape(-1, 1))
            
            sigma = np.sqrt(np.mean(g.covariances_))
            delta = abs(g.means_[0] - g.means_[1])/sigma
            pi = g.weights_[0]
            BI = delta * np.sqrt(pi*(1-pi))
            BIs.append(BI)
    else:
        for i in range(df.shape[0]):        
            g = mixture.GaussianMixture(n_components=2)
            g.fit(np.array(df.iloc[i,:]).reshape(-1, 1))
                  
            sigma = np.sqrt(np.mean(g.covariances_))
            delta = abs(g.means_[0] - g.means_[1])/sigma
            pi = g.weights_[0]
            BI = delta * np.sqrt(pi*(1-pi))
            BIs.append(BI)
    return np.array(BIs)
#add the function modality_index as a method of pandas.DataFrame objects.
pd.DataFrame.bimodality_index = bimodality_index

def diptest(df, axis=0):
    dip_pvalue = []
    if axis==0:
        for i in range(df.shape[1]):
            gene = df.iloc[:,i]
        
            dip_pvalue.append(diptst(gene)[1])
        dip_pvalue = pd.Series(dip_pvalue, index=df.columns)
        return dip_pvalue
    else:
        raise
            

def binarize(df, axis=0):
    bin_df = df.transpose()[[False for n in range(df.shape[1])]].transpose()
    if axis==0:
        for i in range(df.shape[1]):
            gene = df.iloc[:,i]
            g = mixture.GaussianMixture(n_components=2)
            g.fit(np.array(df.iloc[:,i]).reshape(-1, 1))
            if g.means_[0]<g.means_[1]:
                #print(1)
                bin_df[df.columns[i]]=g.predict(np.array(df.iloc[:,i]).reshape(-1, 1))
            else:
                #print(2)
                bin_df[df.columns[i]] = np.abs(g.predict(np.array(df.iloc[:,i]).reshape(-1, 1))-1)

    else:
        bin_df = bin_df.transpose()
        for i in range(df.shape[0]):
            gene = df.iloc[i,:]
            
            g = mixture.GaussianMixture(n_components=2)
            g.fit(np.array(df.iloc[:,1]).reshape(-1, 1))
            g.predict(np.array(df.iloc[:,1]).reshape(-1, 1))
            bin_df[df.index[i]]=g.predict(np.array(df.iloc[:,i]).reshape(-1, 1))
    return bin_df


def uni_norm(df):
    df_ = df.copy()

    lambd = np.log(3)/median_abs_deviation(df_)
    df_norm = 1/(1+np.exp(-lambd*(df_-df_.median())))
    return df_norm
def inflated0_norm(df):
    if len(df.columns)!=0:
        percent_1 = np.percentile(df, 1)
        percent_99 = np.percentile(df, 99)
        df_norm = (df - percent_1)/(percent_99 - percent_1)
        df_norm[df_norm>1]=1
        df_norm[df_norm<0]=0
    else:
        df_norm=df
    return df_norm
def inflated0_test(df):
    amplitudes = np.max(df) - np.min(df)
    peaks=[]
    results = []    
    for i in range(df.shape[1]):
        gene = df.iloc[:,i]
        kde1 = stats.gaussian_kde(gene)
        
        x_eval = np.linspace(np.min(gene), np.max(gene), 1000)
        proba = kde1(x_eval)
        
        peaks.append(x_eval[np.where(proba==max(proba))[0]])
        if peaks[-1]<amplitudes[i]/10:
            results.append(True)
        else:
            results.append(False)
    return df.columns[results]
    

#SCRIPT


######################################################################
##                 Personnalized data calculation                   ##
######################################################################

def mutations_effects_compilation(fnames_celllines_mutations, fname_oncoKB_database, homozygous_loss_only=True):
    oncoKB = pd.read_csv(fname_oncoKB_database, sep='\t', index_col=0)
    
    
    
    cosmic_loss = ['Substitution - Nonsense', 'Deletion - Frameshift',\
                   'Insertion - Frameshift', 'Complex - frameshift']
    cosmic_unknown = ['Unknown', 'Substitution - coding silent', 'Nonstop extension', 'Deletion - In frame', 'Insertion - In frame']
    #keep In frame insertion/deletion in unknown or check somewhere? 
    oncoKB_loss = ['Likely Loss-of-function', 'Loss-of-function']
    oncoKB_gain = ['Likely Gain-of-function', 'Gain-of-function']
    oncoKB_switch = ['Switch-of-function', 'Likely Switch-of-function']
    oncoKB_neutral = ['Neutral']
    oncoKB_undefined = [oncoKB['Mutation Effect'].unique()[9],'Inconclusive']

    cellline_names = ['Car1', 'HT29', 'LS411N', 'SW1417', 'SW1463', 'SW403', 'SW480', 'SW620', 'SW837', 'HCT116']
    for cellline_name in fnames_celllines_mutations:

        mutations = pd.read_csv(fnames_celllines_mutations[cellline_name], index_col = 0)
        mutations.index = [ind.split('_')[0] for ind in mutations.index]



        functional_impact = []
        for i in range(len(mutations['AA Mutation'])):
            mutation = mutations.iloc[i,:]
            gene_name = mutation.name
            mutation_name = mutation['AA Mutation'].split('.')[1]

            if mutation['Type'] in cosmic_loss:
                predicCOSMIC = 'OFF'
                functional_impact.append(predicCOSMIC)

            elif mutation['Type']=='Substitution - Missense': 
                try:
                    oncoKB_mutation = oncoKB.loc[gene_name][oncoKB.loc[gene_name]['Alteration'] == mutation_name]
                    oncoKB_impact = oncoKB_mutation['Mutation Effect'][0]
                    if oncoKB_impact in oncoKB_gain:
                        predicKB = 'ON'
                    elif oncoKB_impact in oncoKB_loss:
                        predicKB = 'OFF'
                    elif oncoKB_impact in oncoKB_neutral:
                        predicKB = 1/2
                    elif oncoKB_impact in oncoKB_switch:
                        predicKB = 2
                    elif oncoKB_impact in oncoKB_undefined:
                        predicKB = -1
                except:
                    predicKB = -12
                functional_impact.append(predicKB)

            elif mutation['Type'] in cosmic_unknown:
                predicCOSMIC = -13
                functional_impact.append(predicCOSMIC)


        mutations['Impact'] = functional_impact
        gain = mutations[mutations['Impact']=='ON']
        loss=mutations[mutations['Impact']=='OFF']
        if homozygous_loss_only:
            loss = loss[loss['Zygosity']=='Homozygous']
        impacted = gain.append(loss)
        impacted = impacted.groupby(impacted.index).first()['Impact']
        try:    
            df
            df = pd.concat([df, pd.Series(impacted, name=cellline_name)], axis=1)
        except:
            print('done')
            df = pd.DataFrame(pd.Series(impacted, name=cellline_name))
    return df.transpose()


def transition_rates_calculation(df_rna_count_matrix, dict_nodes_genes=None,\
                                 max_percent_0 = 0.95, diptest_max=0.05, bi_min=1.5, kurtosis_max=1,\
                                 amplification_factor = 100, return_initial_states=True):
    """ This function defines personalized transition rates values for Boolean model simulations with MaBoSS according to
        the workflow proposed in the publication of J. Béal et al. (2018), 
        'Personalization of Logical Models With Multi-Omics Data Allows Clinical Stratification of Patients' 
   
   ______ 
   inputs
    - df_rna_count_matrix (DataFrame): dataframe of RNA expression, where the samples are the lines and the genes are the columns.
    - dict_nodes_genes (dict):  dictionary, where the keys are the nodes of a model and the values the gene names corresponding to this nodes
    
    _______
    outputs
    - transition_rates_up (DataFrame): the transition rates of the activation of the genes for each sample. 
    They are sufficients to personalize the model but if the  transition_rates_down are needed
    the can be obtained by 1/tranisition_rates_up
    """
    df = df_rna_count_matrix.copy()
    if type(dict_nodes_genes)==dict:
        #filter the genes that are in the model
        dict_nodes2 = {node: dict_nodes_genes[node] for node in dict_nodes_genes if dict_nodes_genes[node] in df.columns}
        df = df.loc[:,dict_nodes2.values()]
        df = df.loc[:,~df.columns.duplicated()]


        #rename df with model nodes directly ?
        #inv_map = {v: k for k, v in dict_nodes2.items()}
        #df = df.rename(columns = inv_map)
        
    else:
        print("the dictionary providing the genes corresponding to the nodes of a model has not been defined")
    
    #filter the genes on the percent of cells their values are 0.
    df_filt = discard_percent_0s(df, max_percent=0.95)
    
    #get the index of the genes that seems to be binarizable
    ind_bin = binarizable(df_filt, diptest_max=diptest_max, bi_min=bi_min, kurtosis_max=kurtosis_max)
    #normalzie these genes and store the result in bin_df
    print("binarization of {} genes started.".format(len(ind_bin)))
    bin_df = binarize(df_filt[ind_bin])
    print("binarization of {} genes done.\n".format(len(ind_bin)))

    #group all the other genes in another df
    no_bin_ind = [ind for ind in df_filt.columns if ind not in ind_bin]
    df_no_bin = df_filt[no_bin_ind]
    
    #get the index of the genes that seems to follow a 0 inflated distribution
    inflated0_ind = inflated0_test(df_no_bin)
    #normalize their values and store it in inflated0_df
    inflated0_df = inflated0_norm(df_no_bin[inflated0_ind])

    #get all the other indexes 
    univar_ind = [ind for ind in df_no_bin.columns if ind not in inflated0_ind]
    #normalize their expressions
    univar_df = uni_norm(df_no_bin[univar_ind])

    print("normalization of {} genes done.".format(len(no_bin_ind)))
    
    total_binnorm_df = pd.concat([bin_df, univar_df, inflated0_df], axis=1)
    #return the binarized/normalized values return total_binnorm_df

    transitions_up = amplification_factor**(2*(np.array(total_binnorm_df)-0.5))
    df_tr_up = pd.DataFrame(transitions_up, index=total_binnorm_df.index, columns=total_binnorm_df.columns)
    if return_initial_states == True:
        return df_tr_up, total_binnorm_df
    else:
        return df_tr_up
#__________________________________________________________________________________________________________#

######################################################################
##                    MaBoSS simulation objetcs                     ##
######################################################################

class Cellline:
    def __init__(self, name, mutations, transition_rates_up, initial_states, dict_gene_nodes, dict_strict_gene_nodes):
        self.name = name
        self.mutations = mutations
        self.transition_rates_up = transition_rates_up
        self.initial_states = initial_states
        self.dict_gene_nodes = dict_gene_nodes
        self.dict_strict_gene_nodes = dict_strict_gene_nodes
    def __repr__(self):
        try :
            self.model
            try:
                self.results
                return self.name+', simu'
            except:
                return self.name+', compu'
        except:
            return self.name 
    
    def personalize_model(self, model):
        personalized_model = model.copy()
        nodes = model.network.names
        
        for node in nodes:
            to_inverse=False
            if node in self.dict_gene_nodes:
                for gene in self.dict_gene_nodes[node]:
                    if gene[0]=='!':
                        to_inverse = True
                        gene = gene[1:]
                    if gene in self.mutations.keys():
                        val_mut = self.mutations[gene]
                        if to_inverse:
                            if val_mut=='ON':
                                val_mut ='OFF'
                            else:
                                val_mut = 'ON'
                        personalized_model.mutate(node, val_mut)
            if node in self.dict_strict_gene_nodes:
                gene = self.dict_strict_gene_nodes[node]
                if gene in self.transition_rates_up.keys():
                    personalized_model.param['$u_'+node] = self.transition_rates_up[gene]
                    personalized_model.param['$d_'+node] = 1/self.transition_rates_up[gene]
            if len(self.initial_states)!=0:
                for node in self.initial_states:
                    personalized_model.network.set_istate(node, self.initial_states[node])
        self.model = personalized_model
        return personalized_model
    
    def run_simulation(self):
        self.results = self.model.run()
        print('done')

        
def format_data_CellSet(df_mutations, df_transition_rates, df_init_states, df_node_gene_mut, df_node_gene_tr):
    '''
    '''
    # mutations #
    dict_mut = df_mutations.transpose().to_dict()
    for key in dict_mut.keys():
        dict_mut[key] = {k: v for k, v in dict_mut[key].items() if v in ['ON','OFF']}

    cellnames = list(dict_mut.keys())
    # transition rates #
    dic_tr_up = df_transition_rates.transpose().to_dict()
    dic_tr_up = {k:v for k,v in dic_tr_up.items() if k in cellnames}
    for k2 in cellnames:
        if k2 not in dic_tr_up.keys():
            dic_tr_up[k2]={}
    # initial states #
    initial_states = {cellname:{} for cellname in cellnames}

    for cellname in cellnames:
        if cellname in df_init_states.index:
            for gene in df_init_states.columns:
                for node in df_node_gene_tr:
                    if gene in df_node_gene_tr[node]:
                        initial_states[cellname][node] = {0:1-df_init_states.loc[cellname, gene], 1:df_init_states.loc[cellname, gene]}

        else:
            initial_states[cellname] = {}
    # format all data in Cellline format #
    celllines = {}
    for cellname in cellnames:
        celllines[cellname] = {"name":cellname,
                               "mutations" : dict_mut[cellname],
                               "transition_rates_up":dic_tr_up[cellname],
                               "dict_gene_nodes":df_node_gene_mut,
                               'initial_states':initial_states[cellname],
                               'dict_strict_gene_nodes':df_node_gene_tr}
        
    return celllines


class CellEnsemble:
    '''
    '''
    def __init__(self, celllines_data, general_model):
        self.model = general_model
        self.data = celllines_data
        self.simu = {'base':{cellname:Cellline(**celllines_data[cellname])
                             for cellname in celllines_data}}
        self.update()
    def __repr__(self):
        return 'conditions : '+str(list(self.simu.keys()))+'\ncell lines : '+str(list(self.simu['base'].keys()))
    def resume(self):
        """Plot the names of the personalized models stored, under a pandas.DataFrame format."""
        return pd.DataFrame(self.simu)
    
    def add_condition(self, conditions, condition_name):
        """Add a condition (new version of each cell line personalized model with mutations) to the CellEnsembl object
        conditions : mutations in the MaBoSS format : (Node_name, effect). The effect can be 'ON' or 'OFF'. For mutliple mutation, a list 
        or tuple can be given.
        condition_name : name of the condition to call them and to define title of the output graphs.
        """
        self.simu[condition_name] = {cellname:Cellline(**self.data[cellname])
                                     for cellname in self.data}
        self.update()
        if type(conditions[0]) is not str:
            print('{} mutations for the condition {}'.format(len(conditions), condition_name))
            for condition in conditions:
                for k in self.simu[condition_name]:
                    self.simu[condition_name][k].model.mutate(*condition)
        else:
            for k in self.simu[condition_name]:
                self.simu[condition_name][k].model.mutate(*conditions)
    
    def update(self, new_model=None):
        """
        TO DO!! For now the conditions are not updated..
        By default, the method recreates personalized versions of the model which is stored as an attribute : self.model.
        new model : You can also give the new version of the general model directly as an argument in this method with this argument.
        It allow to keep the format of the CellEnsembl object (conditions and celllines) but to change the general model used.
        """
        if new_model is not None:
            self.model = new_model
            
        for k1 in self.simu:
            for k2 in self.simu[k1]:
                self.simu[k1][k2].personalize_model(self.model)
    
    def run_simulation(self, celllines='all', conditions='all', redo=False, mute=False):
        
        if celllines == 'all':
            celllines = list(self.simu['base'].keys())
        elif type(celllines) not in [list, tuple]:
            celllines = [celllines]
        if conditions == 'all':
            conditions = list(self.simu.keys())
        elif type(conditions) not in [list, tuple]:
            conditions = [conditions]
            
        for condition in conditions:
            for cellline in celllines:
                if redo==False:
                    try:
                        self.simu[condition][cellline].results
                        if mute==False:
                            print('the simulation {}|{} will not be re-computed'.format(cellline, condition))
                        continue
                    except:
                        pass
                if mute==False:
                    print('Simulating', cellline, 'in the condition', condition)
                self.simu[condition][cellline].run_simulation()
                
       
    def plot_piechart(self, celllines='all', conditions='all'):
        if celllines == 'all':
            celllines = list(self.simu['base'].keys())
        elif type(celllines) not in [list, tuple]:
            celllines = [celllines]
        if conditions == 'all':
            conditions = list(self.simu.keys())
        elif type(conditions) not in [list, tuple]:
            conditions = [conditions]
            
        
        if len(conditions)>1:
            for cellline in celllines:
                fig, axs = plt.subplots(1, len(conditions), figsize=(8*len(conditions),5), constrained_layout=True)
                for condition in conditions:
                    try: 
                        self.simu[condition][cellline].results.plot_piechart(axes = axs[conditions.index(condition)])
                        axs[conditions.index(condition)].set_title(cellline + ' | ' + condition)
                    except:
                        print('the simulation {}|{} seems not having been computed'.format(cellline, condition))
        else:
            for condition in conditions:
                for cellline in celllines:
                    try: 
                        self.simu[condition][cellline].results.plot_piechart()
                        plt.title(cellline + ' | ' + condition)
                    except:
                        print('the simulation {}|{} seems not having been computed'.format(cellline, condition))
    def plot_trajectory(self, celllines='all', conditions='all'):
        if celllines == 'all':
            celllines = list(self.simu['base'].keys())
        elif type(celllines) not in [list, tuple]:
            celllines = [celllines]
        if conditions == 'all':
            conditions = list(self.simu.keys())
        elif type(conditions) not in [list, tuple]:
            conditions = [conditions]
            
        
        if len(conditions)>1:
            for cellline in celllines:
                fig, axs = plt.subplots(1, len(conditions), figsize=(8*len(conditions),5), constrained_layout=True)
                for condition in conditions:
                    try: 
                        self.simu[condition][cellline].results.plot_trajectory(axes = axs[conditions.index(condition)])
                        axs[conditions.index(condition)].set_title(cellline + ' | ' + condition)
                    except:
                        print('the simulation {}|{} seems not having been computed'.format(cellline, condition))
        else:
            for condition in conditions:
                for cellline in celllines:
                    try: 
                        self.simu[condition][cellline].results.plot_trajectory()
                        plt.title(cellline + ' | ' + condition)
                    except:
                        print('the simulation {}|{} seems not having been computed'.format(cellline, condition))

                        
                        
    def compare_survival(self, celllines='all', conditions='all'):
        ## ajouter choix outputs
        outputs_df = pd.DataFrame(index=[], columns=['proliferation_rates', 'survival_rates'])
        
        if celllines == 'all':
            celllines = list(self.simu['base'].keys())
        elif type(celllines) not in [list, tuple]:
            celllines = [celllines]
        if conditions == 'all':
            conditions = list(self.simu.keys())
        elif type(conditions) not in [list, tuple]:
            conditions = [conditions]
            
        for condition in conditions:
            for cellline in celllines:
                outputs_dict = {'survival_rates' : {}, 'proliferation_rates' : {}}
                #??get_last_states_probtraj ?
                st = self.simu[condition][cellline].results.last_states_probtraj
                death_rate = float(sum(st[s] for s in st if 'Apoptosis' in s or 'Mitotic' in s))
                proliferation = float(sum(st[s] for s in st if 'Apoptosis' not in s and 'Mitotic' not in s and 'Prolif' in s))

                outputs_dict['survival_rates'][condition+'_'+cellline] =  1-death_rate
                outputs_dict['proliferation_rates'][condition+'_'+cellline] = proliferation
                outputs_df = pd.concat([pd.DataFrame(outputs_dict), outputs_df])
        return outputs_df
#__________________________________________________________________________________________________________#
              
                
