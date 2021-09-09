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


class Extracteure_ecommerce(Component):
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

			Electro = {"computer":}


			list1 = Electro_values_fr

			for i in range(len(Electro_values_ar)):
				print(Electro_values_ar[2][0])
				for j in range(len(Electro_values_ar[i])):
					list1[i].append(Electro_values_ar[i][j])
				for j in range(len(Electro_values_ang[i])):
					list1[i].append(Electro_values_ang[i][j])
				
			print("list1")
			print(list1)
				
			Electro_dictionary = dict(zip(Electro_keys, list1))
			#print(Type_dictionary)

			for w in tokens :
				for key in Electro_dictionary :
					if w in Electro_dictionary[key] :
						entities_Electro.append(key)
			
			entity_electro = self.convert_to_electro(entities_Electro)
			message.set("entities_Electro", entity_electro, add_to_output=True)
			
#Accessories		

			Watch_acc_keys= ["montre","collier","gourmette","bague","boucles","foulard","ceinture","lunette","gant","cravate"]
			Watch_acc_values_fr = [["montre"],["collier"],["gourmette","bracelet"],["bague"],["boucle"],["foulard","echarpe"],["ceinture"],["lunette"],["gant"],["cravate"]]
			Watch_acc_values_ar = [["ساعه"],["قلادة"],["براسلي"],["خاتم"],["حلق"],["وشاح","فولار"],["حزام","سمطه"],["ندادر","نظارات"],["قفاز"],["ربطة.عنق"]]
			Watch_acc_values_ang = [["watch"],["necklace"],["bracelet"],["ring"],["earring"],["scarf"],["belt"],["glasses","sunglasses"],["glove"],["tie"]]

			
			list2 = Watch_acc_values_fr
			print("list2")
			print(list2)


			for i in range(len(Watch_acc_ar_values)):
				print(Watch_acc_values_ar[2][0])
				for j in range(len(Watch_acc_values_ar[i])):
					list2[i].append(Watch_acc_values_ar[i][j])
				for j in range(len(Watch_acc_values_ar[i])):
					list2[i].append(Watch_acc_values_ar[i][j])
				
			
				
			Watch_acc_dictionary = dict(zip(Watch_acc_keys, list2))
			#print(Type_dictionary)

			for w in tokens :
				for key in Watch_acc_dictionary :
					if w in Watch_acc_dictionary[key] :
						entities_Access.append(key)
			
			entity_access = self.convert_to_access(entities_acc)
			message.set("entities_access", entity_Access, add_to_output=True)
			print("entities_access_Ecomm")




			Home_deco_keys = ["bougie","couverture","taie_oreiller","lampe"]
			Home_deco_values_fr = [["bougie"],["couette","drap"],["taie"],["lampe"]]
			Home_deco_values_ar = [["شمعه"],["لحاف"],["مصباح","لامبه"]]
			Home_deco_values_ang = [["candle"],["sheet","blanket"],["lamp"]]

			list3 = Home_deco_values_fr

			for i in range(len(Home_deco_values_ar)):
				print(Watch_acc_values_ar[2][0])
				for j in range(len(Home_deco_values_ar[i])):
					list3[i].append(Home_deco_values_ar[i][j])
				for j in range(len(Home_deco_values_ang[i])):
					list3[i].append(Home_deco_values_ang[i][j])

			
				
			print("list3")
			print(list3)
				
			Home_deco_dictionary = dict(zip(Home_deco_keys, list3))
			#print(Type_dictionary)

			for w in tokens :
				for key in Home_deco_dictionary :
					if w in Home_deco_dictionary[key] :
						entities_Home_deco.append(key)
			
			entity_home_deco = self.convert_to_home_deco(entities_Home)
			message.set("entities_home_deco", entity_home_deco, add_to_output=True)
			print("entities_home_deco")
			


			Metal_keys = ["or","fer","inox","argent","aluminium","bronze","plaque_or"]
			Metal_values_fr = [["or"],["fer"],["inox","inoxidable"],["argent"],["aluminium"],["bronze"],["plaque.or"]]
			Metal_values_ar = [["ذهب"],["حديد"],["انوكس"],["فضة","ارجونت"],["الومنيوم"],["برونز"],["بلاكيور"]]
			Metal_values_ang = [["gold"],["iron"],["stainless.steel"],["silver"],["aluminium"],["bronze"],["gold.plate"]]


			list4 = Metal_values_fr

			for i in range(len(Metal_values_ar)):
				print(Metal_values_ar[2][0])
				for j in range(len(Metal_values_ar[i])):
					list4[i].append(Metal_values_ar[i][j])
				for j in range(len(Metal_values_ang[i])):
					list4[i].append(Metal_values_ang[i][j])

			
				
			print("list4")
			print(list4)
				
			Metal_values_dictionary = dict(zip(Metal_keys, list4))
			#print(Type_dictionary)

			for w in tokens :
				for key in Metal_values_dictionary :
					if w in Metal_values_dictionary[key] :
						entities_Metal.append(key)
			
			entity_metal = self.convert_to_metal(entities_Metal)
			message.set("entities_Metal", entity_metal, add_to_output=True)
			



			Clothes_keys = ["haut","robe","veste","pantalon","jupe","chaussure","pyjama","sac"]
			list2 = []
			Clothes_values_fr = [["pull", "tshirt", "blouse", "chemise", "haut","tricot","top"],["robe"],["veste","manteau","doudoune"],["jean","pantalon","short","legging","jogging"],["jupe"],["bottes","chaussure","basket","espas","talons","sandale"],["pyjama"],["sac","cartable","pochette","sacoche"]]
			Clothes_values_ar = [["تشيرت", "بلوزة"],["كسوة","روب"],["معطف","فست"],["سروال","جين"],["تنورة","صاية"],["سباط","سنداله","طالون","سبرديلا"],["بيجاما"],["ساك"]]
			
			Clothes_values_ang = [["shirt"],["dress"],["coat"],["jeans"],["skirt"],["shoes"],["pyjama"],["purse","bag"]]
			list5 = Clothes_values_fr
			
			for i in range(len(Clothes_values)):
				print(Clothes_values_ar[2][0])
				for j in range(len(Clothes_values_ar[i])):
					list5[i].append(Clothes_values_ar[i][j])
				for j in range(len(Clothes_values_ang[i])):
					list5[i].append(Clothes_values_ang[i][j])
				
			print("list5")
			print(list5)
				
			Clothes_dictionary = dict(zip(Clothes_keys, list5))
			#print(Type_dictionary)

			for w in tokens :
				for key in Clothes_dictionary :
					if w in Clothes_dictionary[key] :
						entities_Clothes.append(key)
			
			entity_clothes = self.convert_to_clothes(entities_type)
			message.set("entities_type", entity_clothes, add_to_output=True)
			print("entities_type_Ecomm")
			



			
			Color_keys = ["noir","blanc","rouge","jaune","bleu","vert","orange","rose","marron","gris","mauve","beige"]

			Color_values_ar = [["noir"],["blanc"],["rouge"],["jaune"],["bleu"],["vert"],["orange"],["rose"],["marron"],["gris"],["mauve"],["beige"]]
			Color_values_fr = [["نوار"],["ابيض"],["روج"],["سفر"],["زرق"],["خدر"],["ليموني"],["روز"],["مارون"],["رمادي"],["موف"],["بيج"]]
			Color_values_ang = [["black"],["white"],["red"],["yellow"],["blue"],["green"],["orange"],["pink"],["brown"],["grey"],["mauve"],["beige"]]
			list_color = Color_values_fr
			
			for i in range(len(Types_values_fr)):
				print(Color_values_ar[2][0])
				for j in range(len(Color_values_ar[i])):
					list_color[i].append(Color_values_ar[i][j])
				for j in range(len(Color_values_ang[i])):
					list_color[i].append(Color_values_ang[i][j])
			Color_dictionary = dict(zip(Color_keys, list_color))
			
			for w in tokens :
				for key in Color_dictionary :
					if w in Color_dictionary[key] :
						entities_Color.append(key)
			
			entity_color = self.convert_to_type(entities_Color)
			message.set("entities_color", entity_color, add_to_output=True)
			print("entities_colors_Ecomm")
			print(entity_color)
			

#Size extractor			

			Size_keys = ["M","S","L"]

			Size_values_fr = [["moyen", "moyenne", "m","medium"],["s","small","petit"],["l","large"]]
			Size_values_ar = [["مويان"],["صغير"],["لارج"]]
			Size_values_ang = [["medium"],["little"],["large,big"]]

			
			list_size = Size_values_fr
			for i in range(len(Size_values_fr)):
				
				for j in range(len(Size_values_ar[i])):
					list_color[i].append(Size_values_ar[i][j])
				for j in range(len(Size_values_ang[i])):
					list_color[i].append(Size_values_ang[i][j])
			Size_dictionary = dict(zip(Size_keys, list_color))

			for w in tokens :
				for key in Size_dictionary :
					if w in Size_dictionary[key] :
						entities_Size.append(key)

			print(Size_dictionary)
			entity_size = self.convert_to_type(entities_Size)
			message.set("entities_size", entity_size, add_to_output=True)
			print("entities_size_Ecomm")
			print(entity_size)


#Amount of money Extraction 

			amount = ""
			
			for t in tokens :
					toks += t  
					print(t+"token")
					w=re.search(r'((([\d|\d\.\d]+)+(dh|dhs|dirham|دراهم|mad)))', t)
					if w == None :
						print("No money amount")
					else :
						amt = w.string
						for i in amt :
							if i.isdigit():
								amount += i
							else:
								break
					print(amount)
			if amount == "" : 
				currency = ['dh','dhs','dirham','mad','دراهم','درهم']
				amt = ""
				numbers = []
				for word in tokens:
						print("word"+word)
						if word in currency :
							print("there is an amount of money")
							if tokens[tokens.index(word)-1].isdigit() :
								print("amount of money")
								amount = tokens[tokens.index(word)-1]
							elif tokens[tokens.index(word)+1].isdigit() :
								print("amount of money")
								amount = tokens[tokens.index(word)-1]
				
			entity_money = self.convert_to_amount(amount)
			message.set("entity_amount", entity_money, add_to_output=True)


#Fabric extractor

			Fabric_keys = ["chiffon","cotton","crepe","denim","leather","satin","silk","velvet"]

			Fabric_values_fr = [["mousseline"],["coton"],["crepe"],["denim","jean"],["cuir"],["satin"],["soie"],["velour"]]
			Fabric_values_ar = [["موسلين"],["قطن"],["كريب"],["دنيم"],["كوير","جلد"],["ساتان"],["حرير"],["مخمل","موبرا"]]
			Fabric_values_ang = [["chiffon"],["cotton"],["crepe"],["denim","jeans"],["leather"],["satin"],["silk"]]

			
			list5 = Fabric_values_fr
			for i in range(len(Fabric_values_fr)):
				
				for j in range(len(Fabric_values_ar[i])):
					list5[i].append(Fabric_values_ar[i][j])
				for j in range(len(Fabric_values_ang[i])):
					list5[i].append(Fabric_values_ang[i][j])
			Fabric_dictionary = dict(zip(Fabric_keys, list5))

			for w in tokens :
				for key in Fabric_dictionary :
					if w in Fabric_dictionary[key] :
						entities_Fabric.append(key)

			print(Fabric_dictionary)
			entity_Fabric = self.convert_to_fabric(entities_Fabric)
			message.set("entities_Fabric", entity_Fabric, add_to_output=True)
			print("entities_Fabric_Ecomm")
			print(entity_Fabric)




#Numbers Extraction

