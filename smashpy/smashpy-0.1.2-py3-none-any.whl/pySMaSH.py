import os
import sys
import shap
import random
import matplotlib
import numpy as np
import plotly as py
import scanpy as sc
import pandas as pd
import seaborn as sns
import harmonypy as hm
import tensorflow as tf
import matplotlib.pyplot as plt

from sklearn.svm import SVC
from matplotlib import colors
from xgboost import XGBClassifier
from keras.models import Sequential
from sklearn.decomposition import PCA
from keras.utils import to_categorical
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import make_classification
from sklearn.metrics import classification_report
from sklearn.neighbors import KNeighborsClassifier
from keras import losses, optimizers, regularizers
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from keras.layers.normalization import BatchNormalization
from keras.callbacks import EarlyStopping, ModelCheckpoint
from imblearn.ensemble import BalancedRandomForestClassifier
from keras.layers.core import Dense, Dropout, Activation, Flatten

from _version import __version__
    
SEED = 42

###########################################################################################
myColors = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231',
			'#911eb4', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe',
			'#008080', '#e6beff', '#9a6324', '#fffac8', '#800000',
			'#aaffc3', '#808000', '#ffd8b1', '#000075', '#808080', 
			'#307D7E', '#000000', "#DDEFFF", "#000035", "#7B4F4B", 
			"#A1C299", "#300018", "#C2FF99", "#0AA6D8", "#013349", 
			"#00846F", "#8CD0FF", "#3B9700", "#04F757", "#C8A1A1", 
			"#1E6E00", "#DFFB71", "#868E7E", "#513A01", "#CCAA35"]

colors2 = plt.cm.Reds(np.linspace(0, 1, 128))
colors3 = plt.cm.Greys_r(np.linspace(0.7,0.8,20))
colorsComb = np.vstack([colors3, colors2])
mymap = colors.LinearSegmentedColormap.from_list('my_colormap', colorsComb)


###########################################################################################
class pySMaSH:
	def __init__(self):
		
		print(" * Initialising ...")

		os.environ['PYTHONHASHSEED']=str(SEED)
		random.seed(SEED)
		np.random.seed(SEED)
		tf.compat.v1.set_random_seed(SEED)
# 		tf.random.set_seed(SEED)

		#Configure a new global `tensorflow` session
		session_conf = tf.compat.v1.ConfigProto(intra_op_parallelism_threads=1, inter_op_parallelism_threads=1)
		sess = tf.compat.v1.Session(graph=tf.compat.v1.get_default_graph(), config=session_conf)
		tf.compat.v1.keras.backend.set_session(sess)
            
		py.offline.init_notebook_mode(connected=True)
		sc.settings.verbosity = 0


	###########################################################################################
	def __loadDNNmodel(self, X, num_classes):
		"""\
			...
    
			Parameters
			----------
			X : anndata.AnnData
				The AnnData matrix of shape `n_obs` × `n_vars`.
				Rows correspond to cells and columns to genes.
			num_classes : integer (default: None)
                
			Returns
			-------
			model : Keras model
				...
		"""
		dnn_model = Sequential()

		dnn_model.add(Dense(32, input_shape=(X.shape[1],))) #1°layer
		dnn_model.add(BatchNormalization())
		dnn_model.add(Activation('sigmoid'))
		dnn_model.add(Dropout(0.2))

		dnn_model.add(Dense(16, input_shape=(32,))) #2°layer
		dnn_model.add(BatchNormalization())
		dnn_model.add(Activation('sigmoid'))
		dnn_model.add(Dropout(0.1))

		dnn_model.add(Dense(num_classes, activation='softmax')) #output
		
		dnn_model.compile(loss=losses.categorical_crossentropy,
						  optimizer=optimizers.Adam(learning_rate=0.001, amsgrad=False),
						  metrics=['accuracy', 'AUC', 'Precision', 'Recall'])
		
		return dnn_model


	###########################################################################################
	def __network_history_plot(self, network_history):
		"""\
			Plot ...
    
			Parameters
			----------
			network_history : anndata.AnnData
				...
		"""
		
		f, axs = plt.subplots(1,2,figsize=(20,8))
		sns.despine(offset=10, trim=False)
		sns.set(font_scale=1.5)
		sns.set_style("white")

		axs[0].semilogy(network_history.history['loss'])
		axs[0].semilogy(network_history.history['val_loss'])
		axs[0].set_title('Model Complexity Graph:  Training vs. Validation Loss')
		axs[0].set_ylabel('loss')
		axs[0].set_xlabel('epoch')
		axs[0].legend(['train', 'validate'], loc='upper right')

		axs[1].semilogy(network_history.history['accuracy'])
		axs[1].semilogy(network_history.history['val_accuracy'])
		axs[1].set_title('Model Complexity Graph:  Training vs. Validation Accuracy')
		axs[1].set_ylabel('accuracy')
		axs[1].set_xlabel('epoch')
		axs[1].legend(['train', 'validate'], loc='upper right')

		plt.tight_layout()
		plt.show(block=False)
		plt.close("all")


	###########################################################################################
	def __confusionM(self, y_pred, y_test, labels=None, title=None, save=False):
		"""\
			Plot ...
    
			Parameters
			----------
			y_pred : list ()
				...
			y_test : list ()
				...
			labels : list (default: None)
				...
			title : string (default: None)
				...
			save : boolean (default: False)
				...
		"""
		sns.set(font_scale=1.4)
		sns.set_style("white")
		
		sns.despine(offset=10, trim=False)
        
		f, axs = plt.subplots(1,1,figsize=(8,8))
		if labels != None:
			df_cm = pd.DataFrame(confusion_matrix(y_test, y_pred), index=labels, columns=labels)
		else:        
			df_cm = pd.DataFrame(confusion_matrix(y_test, y_pred))
		sns.heatmap(df_cm, annot=True, annot_kws={"size": 12}, fmt='d', cbar=False, cmap=mymap, ax=axs)
		axs.set(xlabel='Predicted labels', ylabel='True labels')
		axs.set_title("Confusion matrix")

        
		f, axs = plt.subplots(1,1,figsize=(9.5,8))
		if labels != None:
			df_cm = pd.DataFrame(confusion_matrix(y_test, y_pred, normalize="true"), index=labels, columns=labels)*100
		else:
			df_cm = pd.DataFrame(confusion_matrix(y_test, y_pred, normalize="true"))*100
		sns.heatmap(df_cm, annot=True, annot_kws={"size": 10}, fmt='.2f', cbar=True, cmap=mymap, ax=axs, cbar_kws={'label': 'Classification rate (%)'})
		axs.set(xlabel='Predicted labels', ylabel='True labels')
		axs.set_title(title)
		axs.set_xticklabels(axs.get_xticklabels(), rotation=45) 
		plt.show(block=False)
		if save:
			plt.tight_layout()
			f.savefig('Figures/%s_ConfMat.pdf'%title, bbox_inches='tight')
		plt.close("all")

        
###########################################################################################
	def data_preparation(self, adata, sparse=False):
		"""\
			Preparing AnnData object with counts, norm, log, scale data in layers. AnnData.X as scale data and AnnData.raw with log-counts data.
    
			Parameters
			----------
			adata : anndata.AnnData
				The AnnData matrix of shape `n_obs` × `n_vars`.
				Rows correspond to cells and columns to genes.
			sparse : boolean (default False)
				to do

			Returns
			-------
			adata : anndata.AnnData
				The AnnData with transformed and saved data into .X, .raw.X, and layers.
		"""
		# save counts into the layer
		adata.layers["counts"] = np.asarray(adata.X)

		# normilise and save the data into the layer
		sc.pp.normalize_per_cell(adata, counts_per_cell_after=1e4)
		adata.layers["norm"] = np.asarray(adata.X).copy()

		# logarithmise and save the data into the layer
		sc.pp.log1p(adata)
		adata.layers["log"] = np.asarray(adata.X.copy())
		# save in adata.raw.X normilise and logarithm data
		adata.raw = adata.copy()

		sc.pp.scale(adata, max_value=10)
		adata.layers["scale"] = np.asarray(adata.X.copy())
        
        
	###########################################################################################
	def harmonise_data(self, adata):
		"""\
			Harmonise AnnData.X for a given batch saved into the AnnData object.
    
			Parameters
			----------
			adata : anndata.AnnData
				The AnnData matrix of shape `n_obs` × `n_vars`.
				Rows correspond to cells and columns to genes.

			Returns
			-------
			adata : anndata.AnnData
				The AnnData with the harmonise data into .obsm["harmonise"].
		"""

		if "batch" not in adata.obs.columns:
			print("batch is not present in .obs")
			return
		
		ho = hm.run_harmony(adata.X, 
							adata.obs, 
							["batch"], 
							max_iter_kmeans=25, 
							max_iter_harmony=100)
		
		# store harmonise data into .obsm["harmonise"]
		adata.obsm["harmonise"] = ho.Z_corr.T
		
		return adata


	###########################################################################################
	def remove_general_genes(self, adata, species='human'):
		"""\
			Removing general genes as general genes connected to mitochondrial activity, ribosomal biogenesis, cell-surface protein regulation of the immune system from AnnData object.
    
			Parameters
			----------
			adata : anndata.AnnData
				The AnnData matrix of shape `n_obs` × `n_vars`.
				Rows correspond to cells and columns to genes.
			species : string (default: human)
				human or mouse
                
			Returns
			-------
			adata : anndata.AnnData
				The AnnData without general genes.
		"""
		if species not in ['human','mouse']:
			print("Warning: species must be human or mouse")
			return
        
		if species=='human':
			adata.var["general"] = ((adata.var_names.str.startswith("MT")) |
									(adata.var_names.str.startswith("RPS")) | 
									(adata.var_names.str.startswith("RPL")) | 
									(adata.var_names.str.startswith("HSP")) | 
									(adata.var_names.str.startswith("HLA")))
		if species=='mouse':        
			adata.var["general"] = ((adata.var_names.str.startswith("mt")) |
									(adata.var_names.str.startswith("rps")) | 
									(adata.var_names.str.startswith("rpl")) | 
									(adata.var_names.str.startswith("hsp")) | 
									(adata.var_names.str.startswith("hla")))
		
		new_gen = []
		for i in adata.var["general"]:
			if i == True:
				new_gen.append(False)
			else: 
				new_gen.append(True)
		adata.var["general"] = new_gen
		
		adata = adata[:, adata.var["general"]]
		
		adata.X   = adata.layers["log"]
		adata.raw = adata.copy()
		adata.X   = adata.layers["scale"]
		
		return adata


	###########################################################################################
	def remove_housekeepingenes(self, adata, path=None):
		"""\
			Removing biological housekeeping genes from AnnData object.
    
			Parameters
			----------
			adata : anndata.AnnData
				The AnnData matrix of shape `n_obs` × `n_vars`.
				Rows correspond to cells and columns to genes.
			path : string (default: None)
				Path where list of housekeeping genes are stored.
                
			Returns
			-------
			adata : anndata.AnnData
				The AnnData without housekeeping genes.
		"""
		if path is None:
			print("path must be passed")
			return
		
		hkg = np.loadtxt(path, dtype="str")

		new_gen = []
		for i in adata.var.index.tolist():
			if i in hkg:
				new_gen.append(False)
			else: 
				new_gen.append(True)
		adata.var["general"] = new_gen
		
		adata = adata[:, adata.var["general"]]
		
		adata.X   = adata.layers["log"]
		adata.raw = adata.copy()
		adata.X   = adata.layers["scale"]
		
		return adata  


	###########################################################################################
	def remove_features_pct(self, adata, group_by=None, pct=0.3):
		"""\
			Removing ... from AnnData object.
    
			Parameters
			----------
			adata : anndata.AnnData
				The AnnData matrix of shape `n_obs` × `n_vars`.
				Rows correspond to cells and columns to genes.
			group_by : string (default: None)
				...
			pct : flaot (default: 0.3)
				... 
                
			Returns
			-------
			adata : anndata.AnnData
				The AnnData without ... genes.
		"""
		# raw.X should be log trasformed
		if group_by is None:
			print("select a group_by in .obs")
			return
		if group_by not in adata.obs.columns:
			print("group_by must be in .obs")
			return 
		
		adata.X   = adata.layers["counts"]
		adata.raw = adata.copy()
		
		list_keep_genes = []
		
		df = pd.DataFrame(data=False, 
						  index=adata.var.index.tolist(),
						  columns=adata.obs[group_by].cat.categories)
		for g in adata.obs[group_by].cat.categories: 
			reduced = adata[adata.obs[group_by]==g]
			boolean, values = sc.pp.filter_genes(reduced, min_cells = reduced.n_obs*pct, inplace=False)
			df[g] = boolean
		dfT = df.T
		for g in dfT.columns:
			if True in dfT[g].tolist():
				list_keep_genes.append(True)
			else:
				list_keep_genes.append(False)
		
		adata.var["general"] = list_keep_genes
		
		adata = adata[:, adata.var["general"]]
		
		adata.X   = adata.layers["log"]
		adata.raw = adata.copy()
		adata.X   = adata.layers["scale"]
		
		return adata  


	###########################################################################################
	def remove_features_pct_2groups(self, adata, group_by=None, pct1=0.9, pct2=0.5):
		"""\
			Removing ... from AnnData object.
    
			Parameters
			----------
			adata : anndata.AnnData
				The AnnData matrix of shape `n_obs` × `n_vars`.
				Rows correspond to cells and columns to genes.
			group_by : string (default: None)
				...
			pct1 : flaot (default: 0.9)
				... 
			pct2 : flaot (default: 0.5)
				... 
                
			Returns
			-------
			adata : anndata.AnnData
				The AnnData without ... genes.
		"""
		# raw.X should be log trasformed
		if group_by is None:
			print("select a group_by in .obs")
			return
		if group_by not in adata.obs.columns:
			print("group_by must be in .obs")
			return 
		
		adata.X   = adata.layers["counts"]
		adata.raw = adata.copy()
		
		list_keep_genes = []
		
		df = pd.DataFrame(data=False, 
						  index=adata.var.index.tolist(),
						  columns=adata.obs[group_by].cat.categories)
		for g in adata.obs[group_by].cat.categories: 
			reduced = adata[adata.obs[group_by]==g]
			boolean, values = sc.pp.filter_genes(reduced, min_cells = reduced.n_obs*(pct1), inplace=False)
			df[g] = boolean
		dfT = df.T
		for g in dfT.columns:
			if (sum(dfT[g].tolist())/len(dfT[g].tolist())) >= pct2:
				list_keep_genes.append(False)
			else:
				list_keep_genes.append(True)
		
		adata.var["general"] = list_keep_genes
		
		adata = adata[:, adata.var["general"]]
		
		adata.X   = adata.layers["log"]
		adata.raw = adata.copy()
		adata.X   = adata.layers["scale"]
		
		return adata


	###########################################################################################
	def scale_filter_features(self, adata, n_components=None, filter_expression=True):
		"""\
			Scaling ... from AnnData object.
    
			Parameters
			----------
			adata : anndata.AnnData
				The AnnData matrix of shape `n_obs` × `n_vars`.
				Rows correspond to cells and columns to genes.
			n_components : integer (default: None)
				...
			filter_expression : boolean (default: True)
				... 
                
			Returns
			-------
			adata : anndata.AnnData
				The AnnData without ... genes.
		"""
		X = adata.X
		if n_components==None:
			n_components=X.shape[1]
		
		if n_components>X.shape[0]:
			n_components=X.shape[0]
		
		ss = StandardScaler()
		pca = PCA(n_components=n_components)
		X_scaled = ss.fit_transform(X)
		X_pca = pca.fit(X_scaled)
		explained_variances = pca.explained_variance_ratio_

		# Count up the components explaining 80 % of the variance
		p_comp = 0
		tot_variance = 0
		for i in range(len(explained_variances)):
			p_comp += 1
			tot_variance += explained_variances[i]
			if tot_variance > 0.80:
				break

		# Get the top five most relevant features for each principal component
		components_features = pca.components_[:p_comp,:] # Shape is n_components * n_features
		all_indices = np.array(list())
		for comp in range(p_comp):
			pc = np.array([abs(i) for i in components_features[comp, :]])
			indices = np.argpartition(pc, -20)[-20:] # Calculate indices for the top 20 features per PC
			all_indices = np.concatenate((all_indices, indices))

		# Final get the unique feature indices which we will keep
		all_indices = np.unique(all_indices)
		all_indices = np.array([int(i) for i in all_indices])

		print("Fraction passing PCA:", len(all_indices)/X.shape[1])
		
		list_keep_genes = []
		for i_idx, i in enumerate(adata.var.index.tolist()):
			if i_idx in all_indices:
				list_keep_genes.append(True)
			else:
				list_keep_genes.append(False)
		adata.var["general"] = list_keep_genes
		
		adata = adata[:, adata.var["general"]]
		
		adata.X   = adata.layers["log"]
		adata.raw = adata.copy()
		adata.X   = adata.layers["scale"]
		
		return adata


	###########################################################################################
	def DNN(self, adata, group_by=None, model=None, test_size=0.2, balance=True, verbose=True, save=True):
		"""\
			Applying DNN to AnnData.X.
    
			Parameters
			----------
			adata : anndata.AnnData
				The AnnData matrix of shape `n_obs` × `n_vars`.
				Rows correspond to cells and columns to genes.
			group_by : string (default: None)
				...
			model : Keras model (default: None)
				... 
			test_size : float (default: 0.2)
				...
			balance : boolean (default: True)
				... 
			verbose : boolean (default: True)
				...
			save : boolean (default: True)
				... 
		"""
		if group_by is None:
			print("select a group_by in .obs")
			return
		if group_by not in adata.obs.columns:
			print("group_by must be in .obs")
			return 
		
		X = np.array(adata.X)
		y = np.array(adata.obs[group_by].tolist())
		
		myDict = {}
		for idx, c in enumerate(adata.obs[group_by].cat.categories):
			myDict[c] = idx
		labels = []
		for l in adata.obs[group_by].tolist():
			labels.append(myDict[l])
		labels = np.array(labels)
		y = labels
		
		weight = []
		n = len(np.unique(y))
		for k in range(n):
			if balance:
				w = len(y)/float(n*len(y[y==k]))
				weight.append(w)
			else:
				weight.append(1)
			class_weight = dict(zip(range(n), weight))
			
		X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=SEED, stratify=y)
		
		num_classes = len(np.unique(adata.obs[group_by]))
		names = adata.obs[group_by].cat.categories.tolist()

		# ecoding labels
		le = LabelEncoder()
		le.fit(y_train)
		le.fit(y_test)
		yy_train = le.transform(y_train)
		yy_test = le.transform(y_test)
		
		# convert class vectors to binary class matrices
		y_train = to_categorical(yy_train, num_classes)
		y_test = to_categorical(yy_test, num_classes)
		
		
		early_stop = EarlyStopping(monitor='val_loss', patience=5, verbose=1)

		fBestModel = 'weights/best_model_%s.h5'%group_by
		best_model = ModelCheckpoint(fBestModel, verbose=1, save_best_only=True)

		batch_size = 100
		
		# the user can define and compile a Sequental DNN
		if model is None:
			model = self.__loadDNNmodel(X, num_classes)

		if verbose:
			verbose_dnn = 1
			print(model.summary())
		
		
		network_history = model.fit(X_train, y_train, 
									batch_size=batch_size, 
									epochs=100, 
									verbose=verbose, 
									validation_data=(X_test, y_test),
									callbacks=[early_stop, best_model], 
									class_weight=class_weight)

		self.__network_history_plot(network_history)

		pred = model.predict_classes(X_test)

		self.__confusionM(pred, yy_test, labels=names, title="DNN", save=save)
		print(classification_report(yy_test, pred, target_names=names))


		model.load_weights('weights/best_model_%s.h5'%group_by)
		score = model.evaluate(X_test, y_test, verbose=1)


	###########################################################################################
	def run_shap(self, adata, group_by=None, model=None, verbose=True, pct=0.05, restrict_top=("global", 10)):
		"""\
			Applying shaply value to model weight obtained by training DNN using DNN() method.
    
			Parameters
			----------
			adata : anndata.AnnData
				The AnnData matrix of shape `n_obs` × `n_vars`.
				Rows correspond to cells and columns to genes.
			group_by : string (default: None)
				...
			model : Keras model (default: None)
				... 
			verbose : boolean (default: True)
				...
			pct : float (default: 0.05)
				... 
			restrict_top : set(string, integer) (default: ("global", 10))
				...
                    
			Returns
			-------
			selectedGenes : list
				...
			selectedGenes_dict : dict
				...
		"""
		if group_by is None:
			print("select a group_by in .obs")
			return
		if group_by not in adata.obs.columns:
			print("group_by must be in .obs")
			return   
		
		if restrict_top[0] != "global" and restrict_top[0] != "local":
			print("First element of restrict_top must be 'global' or 'local'")
			return  
		
		if not isinstance(restrict_top[1], int):
			print("Second element of restrict_top must be an integer value")
			return  
		
		X = np.array(adata.X)
		y = np.array(adata.obs[group_by].tolist())
		
		myDict = {}
		for idx, c in enumerate(adata.obs[group_by].cat.categories):
			myDict[c] = idx
		labels = []
		for l in adata.obs[group_by].tolist():
			labels.append(myDict[l])
		labels = np.array(labels)
		y = labels
		
		num_classes = len(np.unique(adata.obs[group_by]))
		
		if model is None:
			model = self.__loadDNNmodel(X, num_classes)
		
		model.compile(loss=losses.categorical_crossentropy,
					  optimizer=optimizers.Adam(learning_rate=0.001, amsgrad=False),
					  metrics=['accuracy', 'AUC', 'Precision', 'Recall'])
		model.load_weights('weights/best_model_%s.h5'%group_by)
		
		X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=SEED, stratify=y)
		
		if pct is None:
			X_tr1  = X_train
			x_val2 = X_test
		else:
			X_tr1, x_val1, Y_tr1, y_val1 = train_test_split(X_train, y_train, test_size=(1-pct), random_state=SEED, stratify=y_train)
			X_tr2, x_val2, Y_tr2, y_val2 = train_test_split(X_test, y_test, test_size=pct, random_state=SEED, stratify=y_test)
		
		explainer = shap.DeepExplainer(model, X_tr1)
		shap.explainers._deep.deep_tf.op_handlers["AddV2"] = shap.explainers._deep.deep_tf.passthrough
		shap_values = explainer.shap_values(x_val2)
		shap.summary_plot(shap_values, adata.var.index.tolist(), max_display=30)
		
		top = restrict_top[1]
		selectedGenes = []
		selectedGenes_dict = {}
		
		if restrict_top[0] == "global":
			vals = np.abs(shap_values).mean(0)
			feature_importance = pd.DataFrame(list(zip(adata.var.index.tolist(),sum(vals))),columns=['col_name','feature_importance_vals'])
			feature_importance.sort_values(by=['feature_importance_vals'],ascending=False,inplace=True)
			selectedGenes += feature_importance["col_name"].tolist()[:top]
			selectedGenes_dict["group"] = feature_importance["col_name"].tolist()[:top]  

		elif restrict_top[0] =="local":
			for i, name in zip(range(len(shap_values)), adata.obs[group_by].cat.categories):
				vals = np.abs(shap_values[i]).mean(0)
				feature_importance = pd.DataFrame(list(zip(adata.var.index.tolist(),vals)),columns=['col_name','feature_importance_vals'])
				feature_importance.sort_values(by=['feature_importance_vals'],ascending=False,inplace=True)
				selectedGenes += feature_importance["col_name"].tolist()[:top]
				selectedGenes_dict[name] = feature_importance["col_name"].tolist()[:top]
		
		return selectedGenes, selectedGenes_dict


	###########################################################################################
	def ensemble_learning(self, adata, group_by=None, classifier=None, test_size=0.2, balance=True, verbose=True, save=True):
		"""\
			Applying ensemble_learning to AnnData.X.
    
			Parameters
			----------
			adata : anndata.AnnData
				The AnnData matrix of shape `n_obs` × `n_vars`.
				Rows correspond to cells and columns to genes.
			group_by : string (default: None)
				...
			classifier : RandomForest, BalancedRandomForest, XGBoost (default: None)
				... 
			test_size : float (default: 0.2)
				...
			balance : boolean (default: True)
				... 
			verbose : boolean (default: True)
				...
			save : boolean (default: True)
				... 
                
			Returns
			-------
			clf : classifier
				...
		"""
		if group_by is None:
			print("select a group_by in .obs")
			return
		if group_by not in adata.obs.columns:
			print("group_by must be in .obs")
			return 
		
		if classifier not in ["RandomForest", "BalancedRandomForest", "XGBoost"]:
			print("classifier must be 'RandomForest', 'BalancedRandomForest', or 'XGBoost'")
			return 
		
		data = adata.X
		N, d = adata.shape

		names = adata.obs[group_by].cat.categories.tolist()

		myDict = {}
		for idx, c in enumerate(adata.obs[group_by].cat.categories):
			myDict[c] = idx

		labels = []
		for l in adata.obs[group_by].tolist():
			labels.append(myDict[l])

		labels = np.array(labels)

		X = data
		y = labels

		weight = []
		n = len(np.unique(y))
		for k in range(n):
			if balance:
				w = len(y)/float(n*len(y[y==k]))
				weight.append(w)
			else:
				weight.append(1)
			class_weight = dict(zip(range(n), weight))

		X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=SEED, stratify=y)

		if classifier=="RandomForest":
			print("Running with (Weighted) Random Forest")
			clf = RandomForestClassifier(n_estimators=100, random_state=SEED, class_weight=class_weight)
		elif classifier=="BalancedRandomForest":
			print("Running with Balanced Random Forest")
			clf = BalancedRandomForestClassifier(n_estimators=200, max_depth=50, sampling_strategy='all', random_state=SEED ,class_weight=class_weight)
		elif classifier=="XGBoost":
			print("Running with XGBoost (as of now, class_weight not implemented)")
			if n == 2:
				# due to the XGBoost version
# 				clf = XGBClassifier(max_depth=9, num_class=n, n_estimators=200, objective="binary:logistic", learning_rate=0.25, booster="dart", random_state=SEED)
				clf = XGBClassifier(max_depth=9, num_class=n, n_estimators=200, objective="multi:softmax", learning_rate=0.25, booster="dart", random_state=SEED)
			else:
				clf = XGBClassifier(max_depth=9, num_class=n, n_estimators=200, objective="multi:softmax", learning_rate=0.25, booster="dart", random_state=SEED)
		clf.fit(X_train, y_train)
		y_pred = clf.predict(X_test)

		acc = accuracy_score(y_pred, y_test)

		self.__confusionM(y_pred, y_test, labels=names, title=classifier, save=save)
        
		print("Accuracy: %s: Misclassification: %s"%(acc, 1-acc))
		print(classification_report(y_test, y_pred, target_names=names))

		return clf


	###########################################################################################
	def gini_importance(self, adata, clf, group_by=None, verbose=True, restrict_top=("global", 10)):
		"""\
			Applying gini to trained classifier by using ensemble_learning() method.
    
			Parameters
			----------
			adata : anndata.AnnData
				The AnnData matrix of shape `n_obs` × `n_vars`.
				Rows correspond to cells and columns to genes.
			clf : returned by ensemble_learning() method
				... 
			group_by : string (default: None)
				... 
			verbose : boolean (default: True)
				...
			restrict_top : set(string, integer) (default: ("global", 10))
				... 
                
			Returns
			-------
			selectedGenes : list
				...
			selectedGenes_dict : dict
				...
		"""
		if group_by is None:
			print("select a group_by in .obs")
			return
		if group_by not in adata.obs.columns:
			print("group_by must be in .obs")
			return   
		
		if restrict_top[0] != "global" and restrict_top[0] != "local":
			print("First element of restrict_top must be 'global' or 'local'")
			return  
		
		if not isinstance(restrict_top[1], int):
			print("Second element of restrict_top must be an integer value")
			return  
		
		
		if restrict_top[0] =="local":
			data = adata.X
			N, d = adata.shape

			myDict = {}
			for idx, c in enumerate(adata.obs[group_by].cat.categories):
				myDict[c] = idx

			labels = []
			for l in adata.obs[group_by].tolist():
				labels.append(myDict[l])

			labels = np.array(labels)

			X = data
			y = labels

			X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=SEED, stratify=y)
		
		genes = adata.var.index.tolist()
		
		top = restrict_top[1]
		selectedGenes = []
		selectedGenes_dict = {}
		
		if restrict_top[0] == "global":
			importances = clf.feature_importances_
			indices = np.argsort(importances)[::-1]
			for f in range(top):
				selectedGenes.append(genes[indices[f]])
			selectedGenes_dict["group"] = selectedGenes

		elif restrict_top[0] =="local":
			feature_importances = clf.feature_importances_
			N, M = X_train.shape

			out = {}
			for c in set(y_train):
				out[c] = dict(zip(genes, np.mean(X_train[y_train==c, :], axis=0)*feature_importances))
				
			out = pd.DataFrame.from_dict(out)
			out.columns = adata.obs[group_by].cat.categories.tolist()
			
			for cls in out.columns:
				selectedGenes += pd.DataFrame(out[cls]).sort_values(by=cls, ascending=False).index.tolist()[:top]
				selectedGenes_dict[cls] = pd.DataFrame(out[cls]).sort_values(by=cls, ascending=False).index.tolist()[:top]
				
		return selectedGenes, selectedGenes_dict


	###########################################################################################
	def run_classifiers(self, adata, group_by=None, genes=None, classifier="KNN", balance=False, title=None, save=True):
		"""\
			Applying gini to trained classifier by using ensemble_learning() method.
    
			Parameters
			----------
			adata : anndata.AnnData
				The AnnData matrix of shape `n_obs` × `n_vars`.
				Rows correspond to cells and columns to genes.
			group_by : string (default: None)
			genes : list (default: None)
				...
			classifier : sklearn.classifier (default: KNN)
				...
			balance : boolean (default: False)
				...
			title : string (default: None)
				... 
			save : boolean (default: True)
				...
		"""
		if group_by is None:
			print("select a group_by in .obs")
			return
		if group_by not in adata.obs.columns:
			print("group_by must be in .obs")
			return 

		markers_boolean = []
		for gene in adata.var.index:
			if gene in genes:
				markers_boolean.append(True)
			else:
				markers_boolean.append(False)
		adata.var["markers"] = markers_boolean

		data = adata[:, adata.var.markers].X.copy()
		N, d = adata.shape

		names = adata.obs[group_by].cat.categories.tolist()

		myDict = {}
		for idx, c in enumerate(adata.obs[group_by].cat.categories):
			myDict[c] = idx

		labels = []
		for l in adata.obs[group_by].tolist():
			labels.append(myDict[l])

		labels = np.array(labels)

		X = data
		y = labels
		
		weight = []
		n = len(np.unique(y))
		for k in range(n):
			if balance:
				w = len(y)/float(n*len(y[y==k]))
				weight.append(w)
			else:
				weight.append(1)
			class_weight = dict(zip(range(n), weight))

		X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=SEED, stratify=y)
		
		if classifier=="KNN":
			if balance == True:
				print("Warning: class_weight cannot be applied on KNN.")
			neigh = KNeighborsClassifier(n_neighbors=3)
			neigh.fit(X_train, y_train)
			acc = neigh.score(X_test, y_test)
			y_pred = neigh.predict(X_test)
		elif classifier=="RF":
			rf = RandomForestClassifier(max_depth=2, random_state=SEED, class_weight=class_weight)
			rf.fit(X_train, y_train)
			acc = rf.score(X_test, y_test)
			y_pred = rf.predict(X_test)
		elif classifier=="SVM":
			svm = SVC(gamma='auto', class_weight=class_weight)
			svm.fit(X_train, y_train)
			acc = svm.score(X_test, y_test)
			y_pred = svm.predict(X_test)
			
		self.__confusionM(y_pred, y_test, labels=names, title=title, save=save)
		print("Accuracy: %s: Misclassification: %s"%(acc, 1-acc))
		print(classification_report(y_test, y_pred, target_names=names))

        

	###########################################################################################
	def sort_and_plot(self, adata, selectedGenes, group_by=None, group_by2=None, top=5, figsize=(5,8), restricted=True):
		"""\
			Applying gini to trained classifier by using ensemble_learning() method.
    
			Parameters
			----------
			adata : anndata.AnnData
				The AnnData matrix of shape `n_obs` × `n_vars`.
				Rows correspond to cells and columns to genes.
			selectedGenes : list (default: None)
				... 
			group_by : string (default: None)
				... 
			group_by2 : string (default: None)
				... 
			top : integer (default: 5)
				...
			figsize : set(float, float) (default: (5,8))
				... 
 			restricted : boolean (default: True)
				... 
                
			Returns
			-------
			selectedGenes : list
				...
			selectedGenes_dict : dict
				...
		"""
		if group_by is None:
			print("select a group_by in .obs")
			return
		if group_by not in adata.obs.columns:
			print("group_by must be in .obs")
			return 
		if group_by2 is not None:
			if group_by2 not in adata.obs.columns:
				print("group_by must be in .obs")
				return 
		
		markers_boolean = []
		for gene in adata.var.index:
			if gene in selectedGenes:
				markers_boolean.append(True)
			else:
				markers_boolean.append(False)
		adata.var["markers"] = markers_boolean
		
		adata = adata[:, adata.var.markers]

		adata.X   = adata.layers["log"]
		adata.raw = adata.copy()
		adata.X   = adata.layers["scale"]
		
		sc.tl.rank_genes_groups(adata,
								groupby=group_by, 
								n_genes=adata.n_vars,
								method='wilcoxon',
								key_added="rank_genes_groups",
								corr_method='bonferroni')
		if restricted:
			sc.tl.filter_rank_genes_groups(adata,
										   min_in_group_fraction=0.3,
										   min_fold_change=0.0,
										   key="rank_genes_groups",
										   key_added="rank_genes_groups_filtered",
										   max_out_group_fraction=1)

		if restricted:
			df = pd.DataFrame(adata.uns["rank_genes_groups_filtered"]["names"])
		else:
			df = pd.DataFrame(adata.uns["rank_genes_groups"]["names"])

		finalSelectedGenes_dict = {}
		finalSelectedGenes_dict_top ={}
		cleanedLists = []
		for col in df.columns:
			cleanedList = [x for x in df[col].tolist() if str(x) != 'nan']
			cleanedLists += cleanedList
			finalSelectedGenes_dict[col] = cleanedList
			finalSelectedGenes_dict_top[col] = cleanedList[:top]
		
		if group_by2 is None:
			groups = group_by
		else:
			groups = group_by2
		matplotlib.rcdefaults()
		matplotlib.rcParams.update({'font.size': 11})
		ax = sc.pl.DotPlot(adata,
						   finalSelectedGenes_dict_top,
						   groupby=groups,
						   standard_scale='var',
						   use_raw=True,
						   figsize=figsize,
						   linewidths=2).style(cmap=mymap, color_on='square', grid=True, dot_edge_lw=1)
		ax.swap_axes(swap_axes=True)
		ax.show()
		return ax, finalSelectedGenes_dict_top

