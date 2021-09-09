from rasa.nlu.components import Component
from rasa.nlu import utils
from rasa.nlu.model import Metadata
import os
import pandas as pd
import typing
from typing import Any, Optional, Text, Dict
import numpy as np
import regex as re


class Extracteur_chrono(Component):
	"""A custom sentiment analysis component"""
	name = "FACT_EXTRACTION"
	provides = ["entities"]
	requires = ["tokens"]
	defaults = {}
	language_list = ["en"]
	print('initialised the class')

	def __init__(self, component_config=None):
		super(Extracteur_chrono, self).__init__(component_config)

	def train(self, training_data, cfg, **kwargs):
		"""Load the sentiment polarity labels from the text
		   file, retrieve training tokens and after formatting
		   data train the classifier."""



	def convert_to_rasa_pays(self, value):
		"""Convert model output into the Rasa NLU compatible output format."""

		
		entity = {"value": value,
				  
				"entity": "PAYS",
				"extractor": "extractor"}

		return entity

	def convert_to_rasa_poids(self, value):
		"""Convert model output into the Rasa NLU compatible output format."""

		
		entity = {"value": value,
				  
				"entity": "POIDS",
				"extractor": "extractor"}

		return entity

	def convert_to_rasa_product(self, value):
		"""Convert model output into the Rasa NLU compatible output format."""

		
		entity = {"value": value,
				  
				"entity": "VILLE",
				"extractor": "extractor"}

		return entity
		


	def process(self, message, **kwargs):
		"""Retrieve the tokens of the new message, pass it to the classifier
			and append prediction results to the message class."""
		if not self :
			entities = []
		else:
	
#detection pays	
			print("ok")
			tokens = [t.text for t in message.get("tokens")]
			datas = pd.read_csv('countries_ar.csv',sep=';',encoding="utf_8")
			code= np.array(datas['code'])
			pays= np.array(datas['name'])
			ent_val = {}
			entity_conv = []
			entity = ""
			for i in range(len(code)):
				ent_val[pays[i]] = code[i]
			for word in tokens:
				for key in ent_val:
					if key == word:
						print('pays trouvé !!!')
						entity = ent_val[key]
						
			entity_conv = self.convert_to_rasa_pays(entity)

#detection de poids !!!!
			weight =[]	
			toks = ""
			numb = ""

			for t in tokens :
				toks += t  
				print(t+"token")
				w=re.search(r'((([0-9]+).(kg|kilo|g)))', t)
				if w == None :
					print("no regex weight")
				else :
					weight = w.string
					for i in weight :
						if i.isdigit():
							numb += i
			
			if numb == "":
				print("no weight regex")
				exp = ['kg','kgs','g','kilos','kilo']
				for word in tokens:
					print("word"+word)
					if word in exp :
						print("there is a weight")
						if tokens[tokens.index(word)-1].isdigit() :
							print("l9ina weight")
							numb = tokens[tokens.index(word)-1]
						if tokens[tokens.index(word)+1].isdigit() :
							print("l9ina weight")
							numb = tokens[tokens.index(word)-1]
			else :
				print("weight regex ok")

#detection produit
			data_prod = pd.read_csv('csv_ville.csv',sep=';',encoding="utf_8")

			code_prod= np.array(data_prod['ville'])
			prod= np.array(data_prod['value'])
			ent_val2 = {}
			entity_conv2 = []
			entity2 = ""
			for i in range(len(code_prod)):
				ent_val2[prod[i]] = code_prod[i]
			for w in tokens:
				for key2 in ent_val2:
					if key2 == w:
						entity2 = ent_val2[key2]


			entity_conv2 = self.convert_to_rasa_product(entity2)			
			entity_conv = self.convert_to_rasa_pays(entity)
			entity_poids = self.convert_to_rasa_poids(numb)


			message.set("entity_pays", [entity_conv], add_to_output=True)
			message.set("entity_ville", [entity_conv2], add_to_output=True)
			message.set("entity_poids", [entity_poids], add_to_output=True)

