from rasa.nlu.components import Component
from rasa.nlu import utils
from rasa.nlu.model import Metadata
import os
import pandas as pd
import typing
from typing import Any, Optional, Text, Dict
import numpy as np
import regex as re
from time import strftime
from datetime import datetime as dt
from typing import Any, Optional, Text, Dict
import numpy as np
import dateutil.parser as dparser
import datefinder

from dateutil.parser import parse
import datetime
import dateutil.parser as dparser
from pyarabic.number import text2number
import datefinder
from dateutil.parser import parse
from datetime import timedelta
from dateutil.relativedelta import relativedelta


from rasa.nlu.training_data import Message, TrainingData


class Extracteur_ecommerce(Component):
	"""A custom Ecom analysis component"""
	name = "Ecommerce_EXTRACTION"
	provides = ["entities"]
	requires = ["tokens"]
	defaults = {}
	language_list = ["en","fr"]
	print('initialised the class')

	def _init_(self, component_config=None):
		super(Extracteur_oncf, self)._init_(component_config)

	def train(self, training_data, cfg, **kwargs):
		"""Load the sentiment polarity labels from the text
		   file, retrieve training tokens and after formatting
		   data train the classifier."""

	
	def convert_to_size(self, value):
		"""Convert model output into the Rasa NLU compatible output format.""" 

		entity = {"value": value,
				  
				  "entity": "ENTITY_size",
				  "extractor": "extractor"}

		return entity
	def convert_to_amount(self, value):
		"""Convert model output into the Rasa NLU compatible output format.""" 

		entity = {"value": value,
				  
				  "entity": "ENTITY_amnt_money",
				  "extractor": "extractor"}

		return entity

	def convert_to_fabric(self, value):
		"""Convert model output into the Rasa NLU compatible output format.""" 

		entity = {"value": value,
				  
				  "entity": "ENTITY_fabric",
				  "extractor": "extractor"}

		return entity

	def convert_to_clothes(self, value):
		"""Convert model output into the Rasa NLU compatible output format.""" 

		entity = {"value": value,
				  
				  "entity": "ENTITY_Clothes",
				  "extractor": "extractor"}

		return entity
	def convert_to_color(self, value):
		"""Convert model output into the Rasa NLU compatible output format.""" 

		entity = {"value": value,
				  
				  "entity": "ENTITY_color",
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
			print('***********tokens*****')
			print(tokens)
            
			entities_clothes = []
			entities_Size = []
			entities_Color = []
			entities_Electro = []
			entities_Metal = []
			entities_Fabric = []
			entities_Home_deco = []
			entities_Access = []
			Electro_keys = ["computer","TV","phone","beauty_electr","photo","audio","jeux","cuisine","tablette"]
			Electro_values_fr = [["pc","computer","ordinateur"],["télé","tv","television"],["telephone","smartphone","portable","tel","iphone"],["lisseur","sechoir","epilateur","tondeuse"],["appareil.photo","camera","cam"],["casque","ecouteurs"],["play"],["batteur"],["tablette"]]
			Electro_values_ang = [["computer","pc"],["tv"],["phone"],["hairdryer","hair.straightener"],["brush","epilator"],["camera"],["headphone","earphone"],["playstation"],["mixer"],["tablet"] ]
			Electro_values_ar = [["بس","حاسوب"],["تلفاز","تلفزيون"],["تلفون","هاتف"],["سشوار","ليسور","بروس","ابيلاتور"],["كاميرا"],["سماعة","سماعات"],["بلاي"],["ميكسور"],["تابليت"] ]

			Electro = {"computer":
                            {"ar":["بس","حاسوب"],
                            "fr":["pc","computer","ordinateur"],
                            'ang':["computer","pc"]
                            }
                       }

            list_electro = json.loads(Electro)

            print(list_electro)



				
			
			
