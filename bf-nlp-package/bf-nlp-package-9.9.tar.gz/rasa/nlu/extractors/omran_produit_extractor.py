from rasa.nlu.components import Component
from rasa.nlu import utils
from rasa.nlu.model import Metadata
import os
import pandas as pd
import typing
from typing import Any, Optional, Text, Dict
import numpy as np
import regex as re
from rasa.nlu.training_data import Message, TrainingData


class Extracteur_omran(Component):
	"""A custom sentiment analysis component"""
	name = "DATA_EXTRACTION"
	provides = ["entities"]
	requires = ["tokens"]
	defaults = {}
	language_list = ["en"]
	print('initialised the class') 

	def __init__(self, component_config=None):
		super(Extracteur_omran, self).__init__(component_config)

	def train(self, training_data, cfg, **kwargs):
		"""Load the sentiment polarity labels from the text
		   file, retrieve training tokens and after formatting
		   data train the classifier."""



	def convert_to_rasa_surf(self, value):
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

	def convert_to_rasa_city(self, value):
		"""Convert model output into the Rasa NLU compatible output format."""

		
		entity = {"value": value,
				  
				"entity": "city",
				"extractor": "extractor"}

		return entity

	def convert_to_rasa_type(self, value):
		"""Convert model output into the Rasa NLU compatible output format."""

		
		entity = {"value": value,
				  
				"entity": "type",
				"extractor": "extractor"}

		return entity
	
	def convert_to_rasa_localite(self, value):
		"""Convert model output into the Rasa NLU compatible output format."""

		
		entity = {"value": value,
				  
				"entity": "localite",
				"extractor": "extractor"}

		return entity
		
	


	def process(self, message:Message , **kwargs):
		"""Retrieve the tokens of the new message, pass it to the classifier
			and append prediction results to the message class."""
		print(message.text)	
		if not self :
			entities = []
		else:
			tokens = [t.text for t in message.get("tokens")]
			print('******************************tokens****************')
			print(tokens)
			for t in tokens :
				print(t)

#detection cities	
		
			datas = pd.read_csv('csv_files/ville_csv.csv',sep=';',encoding="utf_8")
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
						
			entity_conv_city = self.convert_to_rasa_city(entity_city)

#detection region	
			tokens = [t.text for t in message.get("tokens")]
			print('***********tokens*****')
			print(tokens)
			data = pd.read_csv('csv_files/region_csv.csv',sep=';',encoding="utf_8")
			Treg= np.array(data['ville'])
			Oval= np.array(data['value'])
			print("okkkkkkkkkkkkkkk88888888888888888888888888888")
			ent_va = {}
			entity_conv_region = []
			entity_region = ""
			for i in range(len(Treg)):
				ent_va[Treg[i]] = Oval[i]
			
			for word in tokens:
				for key in ent_va:
					if key == word:
						entity_region = ent_va[key]
			print("okkkkkkkkkkkkkkk88888888888888888888888888888")
			print(entity_region)
			if entity_region == '' :
				print("8888888888888888888888888888888888888888888888888888888888888888888")
						
						
			entity_conv_region = self.convert_to_rasa_localite(entity_region)

#detection de surface !!!!
			tokens = [t.text for t in message.get("tokens")]
			""" datas = pd.read_csv('csv_files/jour_csv.csv',sep=';',encoding="utf_8")
			Tville= np.array(datas['jour'])
			Oville= np.array(datas['value']) """
			ent_val = {}
			entity_conv_surf = []
			entity_surf = ""
			surf = ''
			sur = ''
            # liste des expressions
			exp = ['متر' ,'م','m²','m','m2','ما','م2']
			for word in tokens:
				if word in exp :
					print("there is a surf")
					if tokens[tokens.index(word)+1].isdigit():
						print("l9ina surface")
						surf = tokens[tokens.index(word)+1]
			if surf == '' :
				print("no surface")
				for t in tokens:
					w_s=re.search(r'((([0-9]+).(m|m²|م)))', t)
					if w_s != None :
						surf =w_s.group()
						print("***********none************")
			
			if surf != '':
				
				for i in surf :
					if i.isdigit() :
						sur = sur + i
						print("suuuuuuuuuurfaaace"+sur)
					
                    
			entity_conv_surf = self.convert_to_rasa_surf(sur)
#detection de budget

			tokens = [t.text for t in message.get("tokens")]
			Prix = ['درهم','ده','dh','dhs','دحس','درهم']
			Million = ['مليون','million']
			Mille = ['الف','ألف']
			numb = ''
			for t in tokens:
				w=re.search(r'((([0-9]+).(dh|million|دحس|دح|درهم|مليون|mlyoun)))', t)
				if w != None :
					numb =w.group()
					print(w.group())
			if numb == '':
				entity_conv_prix = []
				entity_prix = ""
				for word in tokens:
					print(" ALL Tokeens ++++++++++ "+ word)
					if  word in Prix :
							print('in priiiiiiiiiiiiiiix')
							if tokens[tokens.index(word)+1].isdigit() : 
								print("prrrrrrrrrrrrrrrrrriiiiiiice")
								print("prices++++++++++++++++++"+entity_prix)
								numb = tokens[tokens.index(word)+1] 
					if word in Million :
							print('millionnnns')
							if tokens[tokens.index(word)+1].isdigit() : 
								print("prrrrrrrrrrrrrrrrrriiiiiiice")
								print("prices++++++++++++++++++"+entity_prix)
								numb = tokens[tokens.index(word)+1] + '0000'
					if word in Mille:
							print("Miiiiiiiillless")
							if tokens[tokens.index(word)+1].isdigit() : 
								print("prrrrrrrrrrrrrrrrrriiiiiiice")
								print("prices++++++++++++++++++"+entity_prix)
								numb = tokens[tokens.index(word)+1] + '000'

					else:
						print('no maaaaaaaaaaaaaatch for priiiice')
			number = ''				
			if numb != '':
				print("priiicee")
				for i in numb :
					if i.isdigit() :
						number = number + i

			
			entity_prix = number
			

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
			message.set("entity_surface", [entity_conv_surf], add_to_output=True)
			message.set("entity_type", [entity_conv2], add_to_output=True)
			message.set("entity_prix", [entity_conv_prix], add_to_output=True)
			message.set("entity_localite", [entity_conv_region], add_to_output=True)