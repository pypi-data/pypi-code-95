from rasa.nlu.components import Component
from rasa.nlu import utils
from rasa.nlu.model import Metadata
import os
import spacy
import pandas as pd
import typing
from typing import Any, Optional, Text, Dict
import numpy as np
import regex as re
from rasa.nlu.training_data import Message, TrainingData


class Extracteur_oncf(Component):
	"""A custom sentiment analysis component"""
	name = "DATA_EXTRACTION"
	provides = ["entities"]
	requires = ["tokens"]
	defaults = {}
	language_list = ["en"]
	print('initialised the class')

	def _init_(self, component_config=None):
		super(Extracteur_omran, self)._init_(component_config)

	def train(self, training_data, cfg, **kwargs):
		"""Load the sentiment polarity labels from the text
		   file, retrieve training tokens and after formatting
		   data train the classifier."""



	def convert_to_rasa_gare(self, value):
		"""Convert model output into the Rasa NLU compatible output format."""

		
		entity = {"value": value,
				  
				"entity": "surface",
				"extractor": "extractor"}

		return entity
    
	def convert_to_rasa_prix(self, value):
		"""Convert model output into the Rasa NLU compatible output format."""
		
		entity = {"value": value,
				  
				"entity": "price",
				"extractor": "extractor"}

		return entity

	def convert_to_rasa_localite(self, value):
		"""Convert model output into the Rasa NLU compatible output format."""

		
		entity = {"value": value,
				  
				"entity": "localite",
				"extractor": "extractor"}

		return entity
	def convert_to_rasa_region(self, value):
		"""Convert model output into the Rasa NLU compatible output format."""

		
		entity = {"value": value,
				  
				"entity": "region",
				"extractor": "extractor"}

		return entity

	def convert_to_rasa_type(self, value):
		"""Convert model output into the Rasa NLU compatible output format."""

		
		entity = {"value": value,
				  
				"entity": "type",
				"extractor": "extractor"}

		return entity
		


	def process(self, message:Message , **kwargs):
		"""Retrieve the tokens of the new message, pass it to the classifier
			and append prediction results to the message class."""
		print(message.text)	
		if not self :
			entities = []
		else:
			
#detection cities	
			tokens = [t.text for t in message.get("tokens")]
			print('***********tokens*****')
			print(tokens)
			datas = pd.read_csv('csv_files/villes.csv',sep=';',encoding="utf_8")
			Tville= np.array(datas['ville'])
			Oville= np.array(datas['value'])
			ent_val = {}
			entity_conv_city = []
			entity_city = ""
			for i in range(len(Tville)):
				ent_val[Tville[i]] = Oville[i]
			for word in tokens:
				for key in ent_val:
					if key == word:
						entity_city = ent_val[key]
						print(" extracted Token ++++++++++ "+ word)
						
			entity_conv_city = self.convert_to_rasa_localite(entity_city)

#detection gare	
			tokens = [t.text for t in message.get("tokens")]
			print('***********tokens*****')
			print(tokens)
			datas = pd.read_csv('csv_files/regions.csv',sep=';',encoding="utf_8")
			Tville= np.array(datas['ville'])
			Oville= np.array(datas['value'])
			ent_val = {}
			entity_conv_region = []
			entity_region = ""
			for i in range(len(Tville)):
				ent_val[Tville[i]] = Oville[i]
			for word in tokens:
				for key in ent_val:
					if key == word:
						entity_region = ent_val[key]
						print(" extracted Token ++++++++++ "+ word)
						
			entity_conv_region = self.convert_to_rasa_region(entity_region)

#detection de surface !!!!
			tokens = [t.text for t in message.get("tokens")]
			ent_val = {}
			entity_conv_surf = []
			entity_surf = ""
            # liste des expressions
			exp = ['متر' ,'م','m²','m','mètre','mètres','metre','metres','ما']
			for word in tokens:
				if word.isdigit():
					if tokens[tokens.index(word)+1] in exp:
						print("l9ina surface")
						entity_surf = word
                    
			entity_conv_surf = self.convert_to_rasa_surf(entity_surf)
#detection de budget

			tokens = [t.text for t in message.get("tokens")]
			#print("flooooos")
			Prix = ['درهم','ده','دهس','dh','dhs','dirham','dirhams']
			million=['مليون','million']
			centime = ['سنتيم','centime']
			entity_conv_prix = []
			entity_prix = ""
			for word in tokens:
				print(" ALL Tokeens ++++++++++ "+ word)
				if word.isdigit():
					print("klmaaaaaaaaaaaaaaaa " + str(tokens.index(word)+1))
					if tokens[tokens.index(word)+1] in million:
						print("milooooooooooooooooooooooon " + word)
						entity_prix = str(int(word)*1000000)
					if tokens[tokens.index(word)+1] in centime:
						entity_prix = str(int(word)/100)	
					if tokens[tokens.index(word)+1] in Prix:
						entity_prix = word
						print("prices++++++++++++++++++ "+entity_prix)

			entity_conv_prix = self.convert_to_rasa_prix(entity_prix)

#detection type produit
			tokens = [t.text for t in message.get("tokens")]
			data_prod = pd.read_csv('csv_files/type_produit.csv',sep=';',encoding="utf_8")
			type_prod= np.array(data_prod['name'])
			prod= np.array(data_prod['value'])
			ent_val2 = {}
			entity_conv2 = []
			entity2 = ""
			for i in range(len(type_prod)):
				ent_val2[type_prod[i]] = prod[i]
			for w in tokens:
				for key2 in ent_val2:
					if key2 == w:
						entity2 = ent_val2[key2]

			entity_conv2 = self.convert_to_rasa_type(entity2)			

			message.set("entity_city", [entity_conv_city], add_to_output=True)
			message.set("entity_region", [entity_conv_region], add_to_output=True)
			message.set("entity_surface", [entity_conv_surf], add_to_output=True)
			message.set("entity_type", [entity_conv2], add_to_output=True)
			message.set("entity_prix", [entity_conv_prix], add_to_output=True)