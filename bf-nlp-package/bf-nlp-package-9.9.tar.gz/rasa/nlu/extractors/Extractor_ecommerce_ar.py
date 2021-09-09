from builtins import vars
from rasa.nlu.components import Component
from rasa.nlu import utils
from rasa.nlu.model import Metadata
import os
import pandas as pd
import json
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


class Extractor_ecommerce_ar(Component):
	"""A custom Ecom analysis component"""
	name = "Ecommerce_EXTRACTION"
	provides = ["entities"]
	requires = ["tokens"]
	defaults = {}
	language_list = ["en","fr"]
	print('initialised the class')

	def _init_(self, component_config=None):
		super(Extractor_ecommerce_ar, self)._init_(component_config)

	def train(self, training_data, cfg, **kwargs):
		"""Load the sentiment polarity labels from the text
		   file, retrieve training tokens and after formatting
		   data train the classifier."""

	
	def convert_to_size(self, value):
		"""Convert model output into the Rasa NLU compatible output format.""" 

		entity = {"value": value,
				  
				  "entity": "SIZE",
				  "extractor": "extractor"}

		return entity
	
	def convert_to_amount_money(self, value):
		"""Convert model output into the Rasa NLU compatible output format.""" 

		entity = {"value": value,
				  
				  "entity": "AMOUNT_MONEY",
				  "extractor": "extractor"}

		return entity
	
	def convert_to_currency(self, value):
		"""Convert model output into the Rasa NLU compatible output format.""" 

		entity = {"value": value,
				  
				  "entity": "CURRENCY",
				  "extractor": "extractor"}

		return entity
	
	def convert_to_home_deco(self, value):
		"""Convert model output into the Rasa NLU compatible output format.""" 

		entity = {"value": value,
				  
				  "entity": "HOME_DECO",
				  "extractor": "extractor"}

		return entity
	
	def convert_to_metal(self, value):
		"""Convert model output into the Rasa NLU compatible output format.""" 

		entity = {"value": value,
				  
				  "entity": "METAL",
				  "extractor": "extractor"}

		return entity

	def convert_to_amount(self, value):
		"""Convert model output into the Rasa NLU compatible output format.""" 

		entity = {"value": value,
				  
				  "entity": "AMNT_MONEY",
				  "extractor": "extractor"}

		return entity

	def convert_to_fabric(self, value):
		"""Convert model output into the Rasa NLU compatible output format.""" 

		entity = {"value": value,
				  
				  "entity": "FABRIC",
				  "extractor": "extractor"}

		return entity

	def convert_to_clothes(self, value):
		"""Convert model output into the Rasa NLU compatible output format.""" 

		entity = {"value": value,
				  
				  "entity": "CLOTHES",
				  "extractor": "extractor"}

		return entity
	def convert_to_color(self, value):
		"""Convert model output into the Rasa NLU compatible output format.""" 

		entity = {"value": value,
				  
				  "entity": "COLOR",
				  "extractor": "extractor"}

		return entity	
	
	

	def convert_to_number(self, value):
		"""Convert model output into the Rasa NLU compatible output format.""" 

		entity = {"value": value,
				  
				  "entity": "NUMBER",
				  "extractor": "extractor"}

		return entity


	def convert_to_electro(self, value):
		"""Convert model output into the Rasa NLU compatible output format.""" 

		entity = {"value": value,
				  
				  "entity": "ELECTRO",
				  "extractor": "extractor"}

		return entity
	
	def convert_to_access(self, value):
		"""Convert model output into the Rasa NLU compatible output format.""" 

		entity = {"value": value,
				  
				  "entity": "ACCESS",
				  "extractor": "extractor"}

		return entity
	def convert_to_cosm(self, value):
		"""Convert model output into the Rasa NLU compatible output format.""" 

		entity = {"value": value,
				  
				  "entity": "COSMETICS",
				  "extractor": "extractor"}

		return entity
	
	def convert_to_product(self, dict):
		"""Convert model output into the Rasa NLU compatible output format.""" 
		entities = []
		for i in range(0,len(dict)):
			
			

			entities.append(dict[i])

		return entities
	
	def convert_to_variation(self, dict):
		"""Convert model output into the Rasa NLU compatible output format.""" 
		entities = []
		for i in range(0,len(dict)):
			
			entity = {	"value": dict[i]["value"],
				  
				  		"category": dict[i]["type"],

				  		"extractor": "extractor_categories_products"}

			entities.append(entity)

		return entities


	def process(self, message:Message , **kwargs):
		"""Retrieve the tokens of the new message, pass it to the classifier
			and append prediction results to the message class."""
		print(message.text)	
		if not self :
			entities = []
		else:
			tokens3 = message.text.split()
			tokens = [t.text for t in message.get("tokens")]
			print('***********tokens*****')
			print(tokens)
			
			
			
			entities_clothes = []
			entities_size = []
			entities_color = []
			entities_electro = []
			entities_metal = []
			entities_fabric = []
			entities_home_deco = []
			entities_access = []

			
			Electro_keys = ["COMPUTER","TV","PHONE","BEAUTYELECTRO","PHOTO","AUDIO","GAME","KITCHEN","TAB"]
			Electro_vals = '{ "computer":{"ar": ["بس ","حاسوب","كومبتر"] ,"fr":["pc","computer","ordinateur"],"ang":["computer"," pc "]} , "tv" : {"ar": ["تلفاز","تلفزيون"] ,"fr":["télé","tv","television"],"ang":[" tv "]},"phone": {"ar": ["تلفون","هاتف","سمارتفون"] ,"fr":["telephone","smartphone","portable","tel","iphone"],"ang":["phone","tablet"]},"beautyelectro" : {"ar": ["سشوار","ليسور","بروس","ابيلاتور","بروس"] ,"fr":["lisseur","sechoir","epilateur","tondeuse","seche.cheveu"],"ang":["brush","epilator","hair.straightener"]},"photo" : {"ar": ["كاميرا"] ,"fr":["appareil.photo"],"ang":["camera"]},"audio" :{"ar": ["سماعة","سماعات","اكوتور"] ,"fr":["casque","ecouteurs"],"ang":["headphone","earphone"]},"game":{"ar": ["بلاي"] ,"fr":["play"],"ang":["playstation"]},"kitchen" :{"ar": ["ميكسور"] ,"fr":["batteur"],"ang":["mixer"]},"tab":{"ar": ["تابليت"] ,"fr":["tablette"],"ang":["tablet"]}}' 
			msg = ''

			for t in tokens :
				if t == "__CLS__" :
					print(" ")
				else :
					msg = msg+" "+t

			list_electro = json.loads(Electro_vals)

			print(Electro_keys[0].lower())
		
			electro_fr = []
			electro_ar = []
			electro_ang = []
			group_types = []
			keys_types = []
			categories = []
			for key in Electro_keys :
				for i in range(len(list_electro[key.lower()]["fr"])):

					type_fr = re.search(list_electro[key.lower()]["fr"][i],msg)
					
					if type_fr != None :
						print(type_fr)

						group_types.append(type_fr.group(0))
						keys_types.append(key)
						electro_fr.append(key)
						categories.append("ELECTRO")

						
						break
				
					
				for i in range(len(list_electro[key.lower()]["ar"])):

					type_ar = re.search(list_electro[key.lower()]["ar"][i],msg)
					if type_ar != None :
						group_types.append(type_ar.group(0))
						electro_ar.append(key)
						keys_types.append(key)
						categories.append("ELECTRO")
						break
				for i in range(len(list_electro[key.lower()]["ang"])):
					
					type_ang = re.search(list_electro[key.lower()]["ang"][i],msg)
					if type_ang != None :
						group_types.append(type_ang.group(0))
						keys_types.append(key)
						electro_ang.append(key)
						categories.append("ELECTRO")
						break
			
			if electro_ar != []:
				for i in range(len(electro_ar)):

					entities_electro.append(electro_ar[i])
			if electro_fr != []:
				for i in range(len(electro_fr)):

					entities_electro.append(electro_fr[i])
			if electro_ang != []: 
				for i in range(len(electro_ang)):

					entities_electro.append(electro_ang[i])
			print(entities_electro)
			
			entities_electro = list(dict.fromkeys(entities_electro))
			
			
			print(entities_electro)
			while("" in entities_electro) :
				entities_electro.remove("")
			

			entity_electro = self.convert_to_electro(entities_electro)
			

			dict_entities_category = []
			






			Watch_acc_keys= ["WATCH","NECKLASS","BRACELET","RING","EARRINGS","SCARF","BELT","GLASSES","GLOVE","TIE","HAT"]
			
						
			Watch_vals = '{ "watch":{"ar": ["ساعه"] ,"fr":["montre"],"ang":["watch"]} , "necklass" : {"ar": ["قلادة","كولير"] ,"fr":["collier"],"ang":["necklace"]},"bracelet": {"ar": ["براسليت","كورميت"] ,"fr":["gourmette","bracelet"],"ang":["bracelet"]},"ring" : {"ar": ["خاتم","باج"] ,"fr":["bague"],"ang":["ring"]},"earrings" : {"ar": ["حلق","بوكل"] ,"fr":["boucle.oreille"],"ang":["earring"]},"scarf" :{"ar": ["وشاح","فولار","اشارب"] ,"fr":["foulard","echarpe"],"ang":["scarf"]},"belt":{"ar": ["حزام","سمطه"] ,"fr":["ceinture"],"ang":["belt"]},"glasses" :{"ar": ["ندادر","نظارات"] ,"fr":["lunette"],"ang":["glasses","sunglasses"]},"glove":{"ar": ["قفاز"] ,"fr":["gant"],"ang":["glove"]},"tie":{"ar": ["ربطة.عنق"] ,"fr":["cravate"],"ang":["tie"]},"hat":{"ar": ["كاسكيت","شابو"] ,"fr":["chapeau"],"ang":["hat"]} }' 

			list_access = json.loads(Watch_vals)
			msg = ''

			for t in tokens :
				if t == "__CLS__" :
					print(" ")
				else :
					msg = msg+" "+t+" "
			access_fr = []
			access_ar = []
			access_ang = []
			
			for key in Watch_acc_keys :
				for i in range(len(list_access[key.lower()]["fr"])):

					type_fr = re.search(list_access[key.lower()]["fr"][i],msg)
					if type_fr != None :
						group_types.append(type_fr.group(0))
						access_fr.append(key)
						keys_types.append(key)
						categories.append("WATCH_ACC")
						
						break
				
					
				for i in range(len(list_access[key.lower()]["ar"])):

					type_ar = re.search(list_access[key.lower()]["ar"][i],msg)
					if type_ar != None :
						group_types.append(type_ar.group(0))
						keys_types.append(key)
						access_ar.append(key)
						categories.append("WATCH_ACC")
						break
				for i in range(len(list_access[key.lower()]["ang"])):
					
					type_ang = re.search(list_access[key.lower()]["ang"][i],msg)
					if type_ang != None :
						group_types.append(type_ang.group(0))
						access_ang.append(key)
						keys_types.append(key)
						categories.append("WATCH_ACC")
						break
			
			
			

			print("access_fr")
			print(access_fr)
			print("access_ar")
			print(access_ar)
			print("access_ang")
			print(access_ang)
			print(entities_access)
			if access_ar != []:
				for i in range(len(access_ar)):
					entities_access.append(access_ar[i])
			if access_fr != []:
				for i in range(len(access_fr)):
					entities_access.append(access_fr[i])
			if	access_ang != []: 
				for i in range(len(access_ang)):
					entities_access.append(access_ang[i])
			print(entities_access)
			
			entities_access = list(dict.fromkeys(entities_access))
			
			
			
			while("" in entities_access) :
				entities_access.remove("")

			


			entity_access = self.convert_to_access(entities_access)
			



			Home_deco_keys = ["CANDLE","SHEET","PILLOW","LAMP","FURNITURE","MIRROR"]
			


			Home_deco_vals = '{ "candle":{"ar": ["شمعه"] ,"fr":["bougie"],"ang":["candle"]} , "sheet" : {"ar": ["لحاف"] ,"fr":["couette","drap"],"ang":["sheet","blanket"]},"pillow": {"ar": ["وسادة","مخدة"] ,"fr":["taie"],"ang":["pillow"]},"lamp" : {"ar": ["مصباح","لامبه"] ,"fr":["lampe"],"ang":["lamp"]},"furniture" : {"ar": ["موبل"] ,"fr":["meuble"],"ang":["furniture"]},"mirror" : {"ar": ["مرايا","ميروار"] ,"fr":["mirroir"],"ang":["mirror"]}}' 

			list_home_deco = json.loads(Home_deco_vals)


			home_fr = []
			home_ar = []
			home_ang = []
			
			for key in Home_deco_keys :
				for i in range(len(list_home_deco[key.lower()]["fr"])):

					type_fr_home = re.search(list_home_deco[key.lower()]["fr"][i],msg)
					if type_fr_home != None :
						
						home_fr.append(key)
						keys_types.append(key)
						group_types.append(type_fr_home.group(0))
						categories.append("HOME_DECO")
						
						break
				
					
				for i in range(len(list_home_deco[key.lower()]["ar"])):

					type_ar_home = re.search(list_home_deco[key.lower()]["ar"][i],msg)
					if type_ar_home != None :
						home_ar.append(key)
						keys_types.append(key)
						group_types.append(type_ar_home.group(0))
						categories.append("HOME_DECO")
						break
				for i in range(len(list_home_deco[key.lower()]["ang"])):
					
					type_ang_home = re.search(list_home_deco[key.lower()]["ang"][i],msg)
					if type_ang_home != None :
						group_types.append(type_ang_home.group(0))
						keys_types.append(key)
						home_ang.append(key)
						categories.append("HOME_DECO")
						break
			
			
			

			print("home_fr")
			print(home_fr)
			print("home_ar")
			print(home_ar)
			print("home_ang")
			print(home_ang)
			
			if home_ar != "":
				for i in range(len(home_ar)):
					
					entities_home_deco.append(home_ar[i])
			if home_fr != "":
				for i in range(len(home_fr)):
					
					entities_home_deco.append(home_fr[i])
			if home_ang != "": 
				for i in range(len(home_ang)):
					
					entities_home_deco.append(home_ang[i])
			print(entities_home_deco)
			
			entities_home_deco = list(dict.fromkeys(entities_home_deco))
			
			
			print(entities_home_deco)
			while("" in entities_home_deco) :
				entities_home_deco.remove("")

			entity_home_deco = self.convert_to_home_deco(entities_home_deco)
			


			keys_vars = []

			Metal_keys = ["GOLD","IRON","INOX","SILVER","ALUMINIUM","BRONZE","PLAQUEOR"]
			


			Metal_vals = '{ "gold":{"ar": ["ذهب"] ,"fr":[" or "],"ang":["gold"]} , "iron" : {"ar": ["حديد"] ,"fr":["fer"],"ang":["iron"]},"inox": {"ar": ["انوكس"] ,"fr":["inox","inoxidable"],"ang":["stainless.steel"]},"silver" : {"ar": ["فضة","ارجونت"] ,"fr":["argent"],"ang":["silver"]},"aluminium" : {"ar": ["الومنيوم"] ,"fr":["aluminium"],"ang":["aluminium"]},"bronze" : {"ar": ["برونز"] ,"fr":["bronze"],"ang":["bronze"]},"plaqueor" : {"ar": ["بلاكيور"] ,"fr":["plaque.or"],"ang":["gold.plate"]}}' 

			list_metal = json.loads(Metal_vals)
			variations =[]

			group_vars = []
			metal_fr = []
			metal_ar = []
			metal_ang = []
			for key in Metal_keys :
				for i in range(len(list_metal[key.lower()]["fr"])):

					type_fr = re.search(list_metal[key.lower()]["fr"][i],msg)
					if type_fr != None :
						
						metal_fr.append(key)
						keys_vars.append(key)
						group_vars.append(type_fr.group(0))
						variations.append("METAL")
						
						break
				
					
				for i in range(len(list_metal[key.lower()]["ar"])):

					type_ar = re.search(list_metal[key.lower()]["ar"][i],msg)
					if type_ar != None :
						metal_ar.append(key)
						keys_vars.append(key)
						group_vars.append(type_ar.group(0))
						variations.append("METAL")
						break
				for i in range(len(list_metal[key.lower()]["ang"])):
					
					type_ang = re.search(list_metal[key.lower()]["ang"][i],msg)
					if type_ang != None :
						metal_ang.append(key)
						keys_vars.append(key)
						group_vars.append(type_ang.group(0))
						variations.append("METAL")
						break
			
			
			if metal_ar != "":
				for i in range(len(metal_ar)):
					
					entities_metal.append(metal_ar[i])
			if metal_fr != "":
				for i in range(len(metal_fr)):
					
					entities_metal.append(metal_fr[i])
			if	metal_ang != "": 
				for i in range(len(metal_ang)):
					entities_metal.append(metal_ang[i])
			
			
			entities_metal = list(dict.fromkeys(entities_metal))
			
			while("" in entities_metal) :
				entities_metal.remove("")

			entity_metal = self.convert_to_metal(entities_metal)
			





			Clothes_keys = ["TOP","DRESS","BLAZER","PANTS","SKIRT","SHOES","PYJAMA","BAG","CAFTAN"]
			


			Clothes_vals = '{ "top":{"ar": ["تشيرت", "بلوزة","شوميز"] ,"fr":["tshirt","chemise","haut","pull","blouse","capuche"],"ang":["shirt","blouse","sweater"]} , "dress" : {"ar": ["كسوة","روب"] ,"fr":["robe"],"ang":["dress"]},"blazer": {"ar": ["معطف","فست","جاكيت"] ,"fr":["veste","manteau","doudoune"],"ang":["coat"]},"pants" : {"ar": ["سروال","جين"] ,"fr":["pantalon","short","legging","jogging"],"ang":["jeans"]},"skirt" : {"ar": ["تنورة","صاية","جوب"] ,"fr":["jupe"],"ang":["skirt"]},"shoes" : {"ar": ["سباط","سنداله","طالون","سبرديلا","ساندال","اسبا","اسكاربين"] ,"fr":["bottes","chaussure","basket","espas","talons","sandale"],"ang":["shoes","sneakers"]},"pyjama" : {"ar":["بيجاما"] ,"fr":["pyjama"],"ang":["pyjama"]},"bag" : {"ar": ["ساك"] ,"fr":["sac","cartable","pochette","sacoche","sac.dos"],"ang":["purse","bag"]}, "caftan" : {"ar": ["قفطان","كفتان"] ,"fr":["caftan"],"ang":["caftan"]}}' 

			list_clothes = json.loads(Clothes_vals)

			clothes_fr = []
			clothes_ar = []
			clothes_ang = []
			for key in Clothes_keys :
				for i in range(len(list_clothes[key.lower()]["fr"])):

					type_fr = re.search(list_clothes[key.lower()]["fr"][i],msg)
					if type_fr != None :
						
						clothes_fr.append(key)
						keys_types.append(key)
						group_types.append(type_fr.group(0))
						categories.append("CLOTHES")
						
						break
				
					
				for i in range(len(list_clothes[key.lower()]["ar"])):

					type_ar = re.search(list_clothes[key.lower()]["ar"][i],msg)
					if type_ar != None :
						clothes_ar.append(key)
						keys_types.append(key)
						group_types.append(type_ar.group(0))
						categories.append("CLOTHES")
						break
				for i in range(len(list_clothes[key.lower()]["ang"])):
					
					type_ang = re.search(list_clothes[key.lower()]["ang"][i],msg)
					if type_ang != None :
						clothes_ang.append(key)
						keys_types.append(key)
						group_types.append(type_ang.group(0))
						categories.append("CLOTHES")
						break
			
			
			if clothes_ar != "":
				for i in range(len(clothes_ar)):
					
					
					entities_clothes.append(clothes_ar[i])
			if clothes_fr != "":
				for i in range(len(clothes_fr)):
					
					entities_clothes.append(clothes_fr[i])
			if	clothes_ang != "": 
				for i in range(len(clothes_ang)):
					
					entities_clothes.append(clothes_ang[i])
			
			
			entities_clothes = list(dict.fromkeys(entities_clothes))
			
			while("" in entities_clothes) :
				entities_clothes.remove("")
			
			
				

			entity_clothes = self.convert_to_clothes(entities_clothes)
			



			Color_keys = ["BLACK","WHITE","RED","YELLOW","BLUE","GREEN","ORANGE","PINK","BROWN","GREY","PURPLE","BEIGE","COL_VAR"]
			Color_vals = '{"black":{"ar": ["نوار","كحلا","لكحل"] ,"fr":["noir","noire"],"ang":["black"]} , "white" : {"ar": ["ابيض","بلانك","لبيد"] ,"fr":["blanc","blanche"],"ang":["white"]},"red": {"ar": ["روج","حمر","لحمر","لروج"] ,"fr":["rouge"],"ang":[" red "]},"yellow" : {"ar": ["سفر"," جون ","فسفر","لجان"] ,"fr":["jaune"],"ang":["yellow"]},"blue" : {"ar": ["زرق","بلو"] ,"fr":["bleu"],"ang":["blue"]},"green" : {"ar": ["خدر","فرت","لخحدر"] ,"fr":["vert","verte"],"ang":["green"]},"orange" : {"ar":	["ليموني","ارونج","ورانج","لورانج"] ,"fr":["orange"],"ang":["orange"]},"pink" : {"ar": ["روز","وردي","روس"] ,"fr":["rose"],"ang":["pink"]},"brown" : {"ar": ["مارون","بني","لمارون"] ,"fr":["marron"],"ang":["brown"]},"grey" : {"ar": ["رمادي","جري","لجريس"] ,"fr":["gris","grise"],"ang":["grey"]},"purple" : {"ar": ["موف","لماف"] ,"fr":["mauve"],"ang":["purple"]},"beige" : {"ar": ["بيج"] ,"fr":["beige"],"ang":["beige"]}, "col_var" : {"ar": ["لون","كولر"] ,"fr":["couleur"],"ang":["color"]}}' 

			list_Color = json.loads(Color_vals)


			color_fr = []
			color_ar = []
			color_ang = []
			for key in Color_keys :
				for i in range(len(list_Color[key.lower()]["fr"])):

					type_fr = re.search(list_Color[key.lower()]["fr"][i],msg)
					if type_fr != None :
						group_vars.append(type_fr.group(0))
						keys_vars.append(key)
						color_fr.append(key)
						variations.append("COLOR")
						break
				
					
				for i in range(len(list_Color[key.lower()]["ar"])):

					type_ar = re.search(list_Color[key.lower()]["ar"][i],msg)
					if type_ar != None :
						group_vars.append(type_ar.group(0))
						keys_vars.append(key)
						color_ar.append(key)
						variations.append("COLOR")
						break
				for i in range(len(list_Color[key.lower()]["ang"])):
					
					type_ang = re.search(list_Color[key.lower()]["ang"][i],msg)
					if type_ang != None :
						color_ang.append(key)
						keys_vars.append(key)
						group_vars.append(type_ang.group(0))
						variations.append("COLOR")
						break
			
			
			if color_ar != "":
				for i in range(len(color_ar)):
					entities_color.append(color_ar[i])
			if color_fr != "":
				for i in range(len(color_fr)):
					
					
					entities_color.append(color_fr[i])
			if	color_ang != "": 
				for i in range(len(color_ang)):
					
					entities_color.append(color_ang[i])
			
			
			entities_color = list(dict.fromkeys(entities_color))
			
			while("" in entities_color) :
				entities_color.remove("")

			entity_color = self.convert_to_color(entities_color)
			


			Size_keys = ["M","S","L","SIZE_VAR"]
			


			Size_vals = '{ "m":{"ar": ["مويان"," م ","مديوم"] ,"fr":["moyen", "moyenne", " m ","medium"],"ang":["medium"]} , "s" : {"ar": ["صغير"," س ","سغيرا","سغير","سمال"] ,"fr":[" s ","small","petit"],"ang":["little"]},"l": {"ar": ["لارج"," ل ","كبير","كبيرا"] ,"fr":[" l ","large"],"ang":["large","big"]},"xs": {"ar": [" اكسترا.سمال "] ,"fr":[" xs ","xsmall"],"ang":["xs","extra.small"]},"size_var": {"ar": ["تايل","حجم"] ,"fr":["taille"],"ang":["size"]}}' 

			list_size = json.loads(Size_vals,strict=False)


			size_fr = []
			size_ar = []
			size_ang = []
			for key in Size_keys :
				for i in range(len(list_size[key.lower()]["fr"])):
					string = "\b"+list_size[key.lower()]["fr"][i]+"\b"
					print(string)
					type_fr = re.search(list_size[key.lower()]["fr"][i],msg)
					print("key"+list_size[key.lower()]["fr"][i]+".")
					print("msg"+msg+".")
					if type_fr != None :
						print("siiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiize")
						group_vars.append(type_fr.group(0))
						size_fr.append(key)
						keys_vars.append(key)
						variations.append("SIZE")
						break
				
					
				for i in range(len(list_size[key.lower()]["ar"])):

					type_ar = re.search(list_size[key.lower()]["ar"][i],msg)
					if type_ar != None :
						size_ar.append(key)
						group_vars.append(type_ar.group(0))
						keys_vars.append(key)
						variations.append("SIZE")
						break
				for i in range(len(list_size[key.lower()]["ang"])):
					
					type_ang = re.search(list_size[key.lower()]["ang"][i],msg)
					if type_ang != None :
						size_ang.append(key)
						group_vars.append(type_ang.group(0))
						keys_vars.append(key)
						variations.append("SIZE")
						break
			
			
			if size_ar != "":
				for i in range(len(size_ar)):
					
					entities_size.append(size_ar[i])
			if size_fr != "":
				for i in range(len(size_fr)):
					
					entities_size.append(size_fr[i])
			if	size_ang != "": 
				for i in range(len(size_ang)):
					
					entities_size.append(size_ang[i])
			
			
			entities_size = list(dict.fromkeys(entities_size))
			
			while("" in entities_size) :
				entities_size.remove("")

			entity_size = self.convert_to_size(entities_size)
			



			print("ok1")


			Fabric_keys = ["CHIFFON","COTTON","CREPE","DENIM","LEATHER","SATIN","VELVET","SILK"]
			print("ok2")
			Fabric_vals = '{ "chiffon":{"ar": ["موسلين"] ,"fr":["mousseline"],"ang":["chiffon"]}, "cotton" :{"ar": ["قطن"] ,"fr":["coton"],"ang":["coton"]} ,  "crepe": {"ar": ["كريب"] ,"fr":["crepe"],"ang":["crepe"]},"denim" : {"ar": ["دنيم"] ,"fr":["denim","jean"],"ang":["denim","jeans"]}, "leather" : {"ar": ["كوير","جلد"] ,"fr":["cuir"],"ang":["leather"]},"satin" : {"ar": ["ساتان"] ,"fr":["satin"],"ang":["satin"]},"velvet" : {"ar": ["مخمل","موبرا"] ,"fr":["velour"],"ang":["velvet"]},"silk" : {"ar": ["حرير"] ,"fr":["soie"],"ang":["silk"]} }'
			list_fabric = json.loads(Fabric_vals)
			print("ok3")

			fabric_fr = []
			fabric_ar = []
			fabric_ang = []

			for key in Fabric_keys :
				for i in range(len(list_fabric[key.lower()]["fr"])):

					type_fr = re.search(list_fabric[key.lower()]["fr"][i],msg)
					if type_fr != None :
						
						fabric_fr.append(key)
						group_vars.append(type_fr.group(0))
						keys_vars.append(key)
						variations.append("FABRIC")
						break
				
					
				for i in range(len(list_fabric[key.lower()]["ar"])):

					type_ar = re.search(list_fabric[key.lower()]["ar"][i],msg)
					if type_ar != None :
						fabric_ar.append(key)
						group_vars.append(type_ar.group(0))
						keys_vars.append(key)
						variations.append("FABRIC")
						break
				for i in range(len(list_fabric[key.lower()]["ang"])):
					
					type_ang = re.search(list_fabric[key.lower()]["ang"][i],msg)
					if type_ang != None :
						fabric_ang.append(key)
						group_vars.append(type_ang.group(0))
						keys_vars.append(key)
						variations.append("FABRIC")
						break
			
			
			if fabric_ar != "":
				for i in range(len(fabric_ar)):
					
					
					entities_fabric.append(fabric_ar[i])
			if fabric_fr != "":
				for i in range(len(fabric_fr)):
					
					
					entities_fabric.append(fabric_fr[i])
			if	fabric_ang != "": 
				for i in range(len(fabric_ang)):
					
					
					entities_fabric.append(fabric_ang[i])
			
			
			entities_fabric = list(dict.fromkeys(entities_fabric))
			
			while("" in entities_fabric) :
				entities_fabric.remove("")


		



			entity_Fabric = self.convert_to_fabric(entities_fabric)
			




#Extract Beauty_cosmetics

			entities_cosm = []
			Beauty_cosm_keys = ["SHAMPOING","MASQUE","PARFUM","CREME"]
			print("ok2")
			Beauty_cosm_vals = '{ "shampoing":{"ar": ["شامبوينج"] ,"fr":["shampoing"],"ang":["shampoo"]}, "masque" :{"ar": ["ماسك"] ,"fr":["masque"],"ang":["hair.mask"]}, "parfum" :{"ar": ["بارفوم"] ,"fr":["parfum"],"ang":["perfum"]}, "creme" :{"ar": ["كريم"] ,"fr":["creme"],"ang":["cream"]}}'
			list_cosm = json.loads(Beauty_cosm_vals)
			print("ok3")

			cosm_fr = ''
			cosm_ar = ''
			cosm_ang = ''

			for key in Beauty_cosm_keys :
				for i in range(len(list_cosm[key.lower()]["fr"])):

					type_fr = re.search(list_cosm[key.lower()]["fr"][i],msg)
					if type_fr != None :
						
						cosm_fr = key
						
						break
				
					
				for i in range(len(list_cosm[key.lower()]["ar"])):

					type_ar = re.search(list_cosm[key.lower()]["ar"][i],msg)
					if type_ar != None :
						cosm_ar = key
						break
				for i in range(len(list_cosm[key.lower()]["ang"])):
					
					type_ang = re.search(list_cosm[key.lower()]["ang"][i],msg)
					if type_ang != None :
						cosm_ang = key
						break
			
			
			if cosm_ar != "":

				entities_cosm.append(cosm_ar)
			if cosm_fr != "":
				entities_cosm.append(cosm_fr)
			if	cosm_ang != "": 
				entities_cosm.append(cosm_ang)
			
			
			if len(entities_cosm) == 2 :
				if entities_cosm[0] == entities_cosm[1]:
					entities_cosm[1] = ""
			
			while("" in entities_cosm) :
				entities_cosm.remove("")



			entity_cosm = self.convert_to_cosm(entities_cosm)
			dict_entities_variations = []
			
			if entities_electro != []:
				dict_entities_category.append({"value": entities_electro , "type" :"ELECTRONICS"})
			if entities_access != []:
				dict_entities_category.append({"value": entities_access , "type" :"ACCESSORIES"})
			if entities_clothes != []:
				dict_entities_category.append({"value": entities_clothes , "type" :"CLOTHES"})
			if entities_home_deco != []:
				dict_entities_category.append({"value": entities_home_deco , "type" : "HOME_DECO"})

			
			if entities_size != []:
				dict_entities_variations.append({"value": entities_size , "type" :"SIZE"})
			if entities_color != []:
				dict_entities_variations.append({"value": entities_color , "type" :"COLOR"})
			if entities_fabric != []:
				dict_entities_variations.append({"value": entities_fabric , "type" :"FABRIC"})
			
			if entities_metal != []:
				dict_entities_variations.append({"value": entities_metal , "type" :"METAL"})

			
			print(dict_entities_category)
			print(dict_entities_variations)
			
			types_index = []
			vars_index = []
			group_types = list(dict.fromkeys(group_types))
			group_vars = list(dict.fromkeys(group_vars))

			message.text.lower()

			
			print("tokens")
			print(tokens)


			for w in group_types :
				types_index.append(tokens.index(w))
			for w in group_vars:
				vars_index.append(tokens.index(w))
			
			
			print("group_types")
			print(group_types)
			print("group_vars")
			print(group_vars)
			print(types_index)
			print(vars_index)

			keys_types = list(dict.fromkeys(keys_types))
			keys_vars = list(dict.fromkeys(keys_vars))



			print("keys_types")
			print(keys_types)
			print("keys_vars")
			print(keys_vars)
			
			
			dict_categories = []
			dict_variations = []
			orders_categories = []
			orders_variations = []
			for i in range (len(group_types)):
				dict_categories.append({"word": group_types[i], "INDEX" : types_index[i]  , "CATEGORY" : keys_types[i] , "TYPE" : categories[i] })
			
			for i in range (len(group_vars)):
				
				dict_variations.append({"word": group_vars[i], "INDEX" : vars_index[i]   , "VARIATION" : keys_vars[i] , "TYPE" : variations[i] })
				
			for k in range(len(dict_categories)):
				orders_categories.append(dict_categories[k]['INDEX'])
			for n in range(len(dict_variations)):
				orders_variations.append(dict_variations[n]['INDEX'])

			print(orders_variations)
			print(orders_categories)
			orders_categories.sort()
			orders_variations.sort()
			print(orders_categories)
			print(orders_variations)
			new_dict_categories = []
			new_dict_variations = []


			for z in range(len(orders_categories)):
				for x in range(len(dict_categories)) :
					if dict_categories[x]["INDEX"] == orders_categories[z] :
						new_dict_categories.append(dict_categories[x])
			
			for z in range(len(orders_variations)):
				for x in range(len(dict_variations)) :
					if dict_variations[x]["INDEX"] == orders_variations[z] :
						new_dict_variations.append(dict_variations[x])

			print(new_dict_variations)
			print(new_dict_categories)

			dict_categories = new_dict_categories
			dict_variations = new_dict_variations

			products = []

			
			
			
			print("ok7")
			
			products = []
			print(dict_variations)
			print(dict_categories)
			if len(dict_categories) < 2  :
				print("< 2")
				
				products.append({ dict_categories[0]['TYPE'] : dict_categories[0]['CATEGORY']})
				for j in range(len(dict_variations)) :
					products[0][dict_variations[j]["TYPE"]] = dict_variations[j]["VARIATION"]
				print(products)
			
			else :
				for i in range(len(dict_categories)) :
					products.append({ dict_categories[i]['TYPE'] : dict_categories[i]['CATEGORY']})
					for j in range(len(dict_variations)) :
						print('ok77')
						print(dict_variations[j])
						print(dict_categories[i])
						if dict_variations[j]['INDEX'] != -1 :
							if dict_variations[j]['INDEX'] < dict_categories[i]['INDEX']   :
								print("avant index")
								
							else :
								print("apres index")
								print(i)
								print(j)
								if len(dict_categories) > i+1 :
									print("len")
									if  dict_variations[j]['INDEX']  > dict_categories[i+1]["INDEX"] :
										print("greater than")
									else :
										products[i][dict_variations[j]["TYPE"]] = dict_variations[j]["VARIATION"]
										dict_variations[j] = {"word": "", "INDEX" :  -1 , "VARIATION" : "" , "TYPE" : "" }
								else :
										print("done")
										products[i][dict_variations[j]["TYPE"]] = dict_variations[j]["VARIATION"]
										dict_variations[j] = {"word": "", "INDEX" :  -1 , "VARIATION" : "" , "TYPE" : "" }
										
							
						print("products1")
						print(products)

			print("products")
			print(products)
				

									

										



						
						


			

			





			


			
			
			
			

			#dict_entities_category =[{"value": entities_electro , "type" :"ELECTRONICS"},{"value": entities_access , "type" :"ACCESSORIES"},{"value": entities_clothes , "type" :"CLOTHES"},{"value": entities_home_deco , "type" : "HOME_DECO"}]
			#print("dictionary")
			#print(dict_entities_category)
			#dict_entities_variations = []
			#dict_entities_variations =[{"value": entities_size , "type" :"SIZE"},{"value": entities_color , "type" :"COLOR"},{"value": entities_fabric , "type" :"FABRIC"}]
			#print("dictionary2")
			#print(dict_entities_variations)


			entity_category = self.convert_to_product(products)
			message.set("products", entity_category, add_to_output=True)
			


			
# Extract Numbers 

			numbers = []
			for t in tokens :
				if t.isdigit():
					numbers.append(t)
			
			entity_numb = self.convert_to_number(numbers)
			if numbers != []:

				message.set("Numbers", entity_numb, add_to_output=True)


#Extract amount of money & currencies
			print(tokens)
			amount = ''
			currency_entity = ''
			for s in tokens :
				print(s)
				money = re.search(r'(([0-9]+)+(dh|dhs|mad|euro|eu|€|$|usd))',s)
				if money !=  None :
					print("yes")
					print(money.string)
					for t in money.string :
						if t.isdigit():
							amount = amount + t 
						else :
							currency_entity = currency_entity + t
			

			if amount != None or currency_entity != None :

				currencies_keys = ["MAD","EU","USD"]
				currency = {"MAD":["dh","dhs","mad","dirham","درهم","دم","دحس"],"EU":['euro',"eu","€","اورو"],"USD":["$","usd","دولار"]}
				print(currency["USD"])
				print(tokens)
				for i in range(0,len(tokens)) :
					if tokens[i].isdigit():
						for key in currencies_keys :	
							print(key)
							print("ok3")
							
							print(currency[key])
							if tokens[i+1] in currency[key]  :
								print("ok4")
								amount = tokens[i]
								
								currency_entity = key
								print("currency")
								print(currency)
			
			print("amount")
			print(amount)
			print("currency")
			print(currency_entity)

			

			entity_money = self.convert_to_amount(amount)
			if amount != "" :

				message.set("Amount_Money", entity_money, add_to_output=True)
			
			entity_currency = self.convert_to_currency(currency_entity)

			if currency_entity != "" :

				message.set("Currency", entity_currency, add_to_output=True)
















