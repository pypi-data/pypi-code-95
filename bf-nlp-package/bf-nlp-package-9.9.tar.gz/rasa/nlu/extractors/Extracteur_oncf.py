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


class Extracteur_oncf(Component):
	"""A custom sentiment analysis component"""
	name = "DATA_EXTRACTION"
	provides = ["entities"]
	requires = ["tokens"]
	defaults = {}
	language_list = ["en"]
	print('initialised the class')

	def _init_(self, component_config=None):
		super(Extracteur_oncf, self)._init_(component_config)

	def train(self, training_data, cfg, **kwargs):
		"""Load the sentiment polarity labels from the text
		   file, retrieve training tokens and after formatting
		   data train the classifier."""



	
    
	

	def convert_to_rasa_day(self, value):
		"""Convert model output into the Rasa NLU compatible output format."""

		
		entity = {"value": value,
				  
				"entity": "date",
				"extractor": "extractor"}

		return entity

	def convert_to_rasa_month(self, value):
		"""Convert model output into the Rasa NLU compatible output format."""

		
		entity = {"value": value,
				  
				"entity": "mois",
				"extractor": "extractor"}

		return entity
	def convert_to_rasa_horaire(self, value):
		"""Convert model output into the Rasa NLU compatible output format."""

		
		entity = {"value": value,
				  
				"entity": "tr_horaire",
				"extractor": "extractor"}

		return entity
	
	def convert_to_rasa_numbers(self, value):
		"""Convert model output into the Rasa NLU compatible output format."""

		
		entity = {"value": value,
				  
				"entity": "number",
				"extractor": "extractor"}

		return entity
	

	
		
	def convert_ville_dep(self, liste):
		"""Convert model output into the Rasa NLU compatible output format."""
		n = len(liste)
		print(n)
		entities= []
		for val in range(n) :
			entities.append({"value" : liste[val],
				  
				"entity": "GARE_DEP",
				"extractor": "extractor"})
		
		return entities
	def convert_gare_dep(self, liste):
		"""Convert model output into the Rasa NLU compatible output format."""
		n = len(liste)
		print(n)
		entities= []
		for val in range(n) :
			entities.append({"value" : liste[val],
				  
				"entity": "GARE_DEP",
				"extractor": "extractor"})

		return entities
	def convert_gare_arr(self, liste):
		"""Convert model output into the Rasa NLU compatible output format."""
		n = len(liste)
		print(n)
		entities= []
		for val in range(n) :
			entities.append({"value" : liste[val],
				  
				"entity": "GARE_ARR",
				"extractor": "extractor"})

		return entities
	def convert_ville_arr(self, liste):
		"""Convert model output into the Rasa NLU compatible output format."""
		n = len(liste)
		print(n)
		entities= []
		for val in range(n) :
			entities.append({"value" : liste[val],
				  
				"entity": "GARE_ARR",
				"extractor": "extractor"})

		return entities

	
	def convert_to_heure(self, value):
		"""Convert model output into the Rasa NLU compatible output format.""" 

		entity = {"value": value,
				  
				  "entity": "HOUR",
				  "extractor": "extractor"}

		return entity


	def convert_to_classe(self, value):
		"""Convert model output into the Rasa NLU compatible output format.""" 

		entity = {"value": value,
				  
				  "entity": "CLASSE",
				  "extractor": "extractor"}

		return entity


	def convert_to_card(self, value):
		"""Convert model output into the Rasa NLU compatible output format.""" 

		entity = {"value": value,
				  
				  "entity": "CARD",
				  "extractor": "extractor"}

		return entity
	
	def convert_to_code_card(self, value):
		"""Convert model output into the Rasa NLU compatible output format."""

		
		entity = {"value": value,
				  
				"entity": "code_card",
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
 
			
			cities_dep = []
			cities_arr = []


#replacing indou arabic numbers
			string = ""
			for t in tokens :
				string = string + t + ' '


			if '۰' in string :
				string = string.replace('۰','0')
			if '١' in string :
				string = string.replace('١','1')
			if '٢' in string :
				string = string.replace('٢','2')
			if '۳' in string :
				string = string.replace('۳','3')
			if '۴' in string :
				string = string.replace('۴','4')
			if '۵' in string :
				string = string.replace('۵','5')
			if '۶' in string :
				string = string.replace('۶','6')
			if '۷' in string :
				string = string.replace('۷','7')
			if '۸' in string :
				string = string.replace('۸','8')
			if '۹' in string :
				string = string.replace('۹','9')
			
			print("string")
			print(string)
			
			tokens = string.split(" ")
			




#detection cities


			#tokens = [t.text for t in message.get("tokens")]
			print('***********tokens*****')
			print(tokens)

#delete unecessary de
			for i in range(len(tokens)):
				if tokens[i] == 'de' :
					if tokens[i-1] == 'gare' or tokens[i-1] == 'gares':
						tokens[i] = ""
					
			print('***********new    tokens*****')
			print(tokens)



			datas = pd.read_csv('csv_files/villes_oncf.csv',sep=';',encoding="utf_8")
			Tville= np.array(datas['ville'])
			Oville= np.array(datas['value'])
			ent_val = {}
			city_dep_conv = []
			print("1")
			ville_dep= ""
			ville_arr =""
			entities_city = []
			name_city = []
			print("2")
			for i in range(len(Tville)):
				ent_val[Tville[i]] = Oville[i]
			for word in tokens:
				for key in ent_val:
					if key == word:
						
						name_city.append(word)
						entities_city.append(ent_val[key])
						print(" extracted Token ++++++++++ "+ word)
						break
			print("list city names")
			print(name_city)
			print("list city entities")
			print(entities_city)
			cities_dep = []
			cities_arr = []
			
			if len(entities_city) > 1:
				if tokens[tokens.index(name_city[0])-1] == "من" or tokens[tokens.index(name_city[0])-2] == "من" or tokens[tokens.index(name_city[0])-1] == "de" or tokens[tokens.index(name_city[0])-2] == "de" or tokens[tokens.index(name_city[0])-1] == "depuis" or tokens[tokens.index(name_city[0])-2] == "depuis" or tokens[tokens.index(name_city[0])-2] == "quitter" or tokens[tokens.index(name_city[0])-1] == "quitter":
					ville_dep= entities_city[0]
					ville_arr = entities_city[1]
				elif tokens[tokens.index(name_city[1])-1] == "من" or tokens[tokens.index(name_city[1])-1] == "quitter" or  tokens[tokens.index(name_city[1])-2] == "quitter" or tokens[tokens.index(name_city[1])-2] == "من" or tokens[tokens.index(name_city[1])-1] == "de" or tokens[tokens.index(name_city[1])-2] == "de" or tokens[tokens.index(name_city[1])-1] == "depuis" or tokens[tokens.index(name_city[1])-2] == "depuis"  :
					ville_dep= entities_city[1]
					ville_arr = entities_city[0]
				else :
					ville_dep = entities_city[0]
					ville_arr = entities_city[1]
			if 	len(entities_city) ==1:
				if tokens[tokens.index(name_city[0])-1] == "من" or tokens[tokens.index(name_city[0])-2] == "من" or tokens[tokens.index(name_city[0])-1] == "de" or  tokens[tokens.index(name_city[0])-2] == "de" or tokens[tokens.index(name_city[0])-1] == "quitter" or tokens[tokens.index(name_city[0])-1] == "depuis" or tokens[tokens.index(name_city[0])-2] == "depuis" or tokens[tokens.index(name_city[0])-2] == "quitter" :
					print("yess ville depp")
					ville_dep= entities_city[0]
				else :
					ville_arr = entities_city[0]
			
			
			lt = ville_dep.split(",")
			lt2 = ville_arr.split(",")
			for i in lt :

				cities_dep.append(i)
			for i in lt2 :
				cities_arr.append(i)
			print("villes arrivee")	
			print(cities_arr)
			print("villes de depart")
			print(cities_dep)
			
			


#detection gare	
			
			msg = ""
			for t in tokens :
				if t == "__CLS__" :
					print(" ")
				else :
					msg = msg+" "+t
			
			print(msg+".")
			data_gare = pd.read_csv('csv_files/gare_comp.csv',sep=';',encoding="utf_8")
			exp = np.array(data_gare['gare'])
			gare_nom= np.array(data_gare['value'])
			ent_val = {}
			entity_conv_city = []
			
			entitie_gares = []
			entities_gares = []
			name_gares= []
			entit_gare = ""
			
			for i in range(len(exp)):
				ent_val[exp[i]] = gare_nom[i]
			print(tokens)
			match = ''
			names_word =[]
			for key in ent_val:
				gare = re.search(key,msg)
				
				if gare != None :
					match = gare.group()
					print("MATCH")
					
					entitie_gares.append(ent_val[key])
					name_gares.append(key)
					names_word.append(gare.group())
					break
			match = ''
			print("second gare")
			for key in ent_val:
				
				gare2 = re.search(key,msg)
				
				
				if gare2 != None :
					match = gare2.group()
					print("MATCH2")
					
					
					
				if gare2 != None and ent_val[key] != entitie_gares[0] :
					entitie_gares.append(ent_val[key])
					name_gares.append(key)
					names_word.append(gare2.group())
					break
				else :
					continue
			
			print("gare_names")
			print(name_gares)
			print(names_word)
			
#modiiiiiiiiiiiifiiiiiiiiiiiiicatiooooooooooon
			name_gares = names_word

			
			



			
			
			
			print("entities_gares")
			print(entitie_gares)
			gare1_splitted = []
			gare2_splitted = []
			gare_splitted = []
			gare_dep = []
			gare_arr = []
			
			liste = []
			for i in entitie_gares:
				if i not in liste:
					liste.append(i)
			
			entities_gares = liste
			print("gare_names")
			print(name_gares)
			print("entities_gares")
			print(entities_gares)
			print("entities_city")
			print(entities_city)
			print(cities_arr)
			print(cities_dep)
			print("name_city")
			print(name_city)
			
			print("entitie_gares")
			print(entitie_gares)
			print(entities_city)
			print(cities_dep)
			print(cities_arr)
			
			ind = -1
			ind2 = -1

			for g in entitie_gares :
				if len(entities_city) != 0 :
					if g in entities_city[0]:
							print(entities_city[0])

							ind = 0
					
			print("ok1")
					
			print(entities_city)
			for g in entitie_gares :
				print("ok8")
				print(entities_city)
				if len(entities_city) ==2:
					if g in entities_city[1]:
							print(entities_city[1])
							ind2 = 1
					
				print("ok2")
					
			if ind2 == 1 :
				entities_city.pop(1)
				name_city.pop(1)
			if ind == 0 :
				entities_city.pop(0)
				name_city.pop(0)

			print("entities_city")
			print(entities_city)

			p = 0
			if cities_dep != []:
				for city in cities_dep :
					if city not in entities_city:
						p = 1
						print("1")
						break
				
			z = 0
			if cities_arr != []:
				for city in cities_arr :
					if city not in entities_city:
						z = 1
						print("2")
						break
			
			
			
					

			'''


			index1 = -1
			index2 = -1
			cities_dep_new = []
			cities_dep_text = ''

			
					if city in entities_city[0]:
						
						index1 = 0
						break
				print("indew1")
				print(index1)
				for city in cities_dep :
					if city in entities_city[1]:
						index1 = 1
						break
				print("indew1")
				print(index1)

			print(entities_city)
			if cities_arr != []:
				for city in cities_arr :
					if city in entities_city[0]:
						
						index2 = 0
						break
				print("indeww1")
				print(index2)
						
				for city in cities_arr :
					if city in entities_city[1]:
						index2 = 1
						break
				print("indeww2")
				print(index2)

			print(index1)
			print(index2)
			print(entities_city)

			if index1 == 0 or index2 == 0:
				entities_city.pop(0)
			if index1 == 1 or index2 == 1:
				entities_city.pop(1)
			print("new entities_city")
			print(entities_city)
			
			if cities_dep == [] :
				entities_city.pop(0)
			if cities_arr == [] :
			entities_city.pop(1)

			entities_city=[]
			if cities_dep != []:

				entities_city.append(cities_dep)
			if cities_arr != []:

				entities_city.append(cities_arr)
			

			


			cities_det1 = []
			var = 0

			if len(entities_city) != 0 and entities_city[0] != [] :
				cities_det1 = entities_city[0].split(",")
				print(cities_det1)
			if len(entities_city) != 0 and entities_city[0] != [] :
				cities_det1 = entities_city[0].split(",")
				print(cities_det1)
			
			
			
			for gare in entitie_gares :
				if gare in cities_det1:
					var = 1
			
			print("var")
			print(var)
			
			if len(entities_gares) == 1 and len(entities_city) == 1 and var == 1:
						print("yes entitycity == entity gare")
						entities_city = []
						cities_arr = []
						cities_dep = []
						print(entities_city)
						print(entities_gares)

						print()
		'''
			if len(entities_gares) == 2 :
				if entities_gares[1] == entities_gares[0]:
					entities_gares[1] == ''
			print("ok")
			if len(entities_gares) == 1 : 
				if len(entities_city) == 0 :
					print("ok1")
					if " من" in msg or  "de " in msg or  "depuis " in msg or "quitter" in msg:
							print("depuiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiis")
							gare_dep.append(str(entities_gares[0]))
					if gare_dep == []:
						gare_arr.append(str(entities_gares[0]))
				elif len(entities_city) == 1 :
					print("ok 1 ville 1 gare")
					
					print(entities_gares)
					print(entities_city)
					gare_splitted = name_gares[0].split(" ")
					print(gare_splitted)
					print("ok2")
#CHECKER SI LA GARE DETECTEE EST UNE GARE DE DEP OU PAS
					print(tokens[tokens.index(gare_splitted[0])])
					print("ok3")
					print(name_city[0])
					if tokens[tokens.index(gare_splitted[0])-1] == 'de' or tokens[tokens.index(gare_splitted[0])-1] == 'من' or tokens[tokens.index(gare_splitted[0])-1] == 'depuis' or tokens[tokens.index(gare_splitted[0])-1] == 'quitter':
						print("depuiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiis")
						gare_dep.append(str(entities_gares[0]))
					elif tokens[tokens.index(name_city[0])-1] == 'de' or tokens[tokens.index(name_city[0])-1] == 'من' or tokens[tokens.index(name_city[0])-1] == 'depuis' or tokens[tokens.index(name_city[0])-1] == 'quitter':
						gare_arr.append(str(entities_gares[0]))
						cities_dep= entities_city[0].split(",")
					else :
						print("non depuiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiis")
						k = tokens.index(name_city[0])
						j = tokens.index(gare_splitted[0])
##MODIIIIFIICAAATIOOON
						cities_dep = []
						cities_arr = []
						print(k)
						print(j)
#cas (casa port)
						if j == k :
									cities_arr = []
									print("alike")
									gare_arr.append(str(entities_gares[0]))
									print(gare_arr)
#cas (fes casa port)
						elif j > k :
									gare_arr.append(str(entities_gares[0]))
									cities_dep= entities_city[0].split(",")
									print('j > k')
									print(gare_arr)
									print(cities_dep)
# cas (casa port fes)
						else : 
									gare_dep.append(str(entities_gares[0]))
									cities_arr= entities_city[0].split(",")
									print('k > j')
									print(gare_dep)
									print(cities_arr)
#2 VILLES ET UNE GARE , l'une des villes doit etre enlevee
				elif len(entities_city) == 2 :
					gare_splitted = name_gares[0].split(" ")
					print("ok 2 ville 1 gare")
					print(entities_gares)
					print(entities_city)
					k = tokens.index(name_city[0])
					print(k)
					l = tokens.index(name_city[1])
					print(l)
					j = tokens.index(gare_splitted[0])
					print(j)
					if j == k :
									phr = entities_city[1].split(",")
									print(phr)

									print(entities_gares)
									print(entities_city)
									print('k===j')
									name_city[0] = ''
									print(name_city)
									if j > l :
										print("j suppp")
										print(entities_city[1])
										for i in phr :
											cities_dep.append(i)
										gare_arr.append(entities_gares[0])
									
										print(cities_dep)
										print(gare_arr)
									if l> j : 
										print("l suupp")
										print(entities_city[1])
										
										if tokens[l-1] == 'de' or tokens[l-1] == 'من' or tokens[l-1] == 'depuis' or tokens[l-1] == 'quitter':

											gare_arr.append(entities_gares[0])
											for p in phr:
												cities_dep.append(p)
										else :
											for i in phr :
												cities_arr.append(i)
											gare_dep.append(entities_gares[0])
										print("cities_arr")
										print(cities_arr)
										print("gare_dep")
										print(gare_dep)
					if j == l :
									phr = entities_city[0].split(",")
									print(phr)
									print("j==l")
									name_city[1] = ''
									if j > k :
										if tokens[j-1] == 'de' or tokens[j-1] == 'من' or tokens[j-1] == 'depuis' or tokens[j-1] == 'quitter' :

											gare_dep.append(entities_gares[0])
											for p in phr:
												cities_arr.append(p)


										else :
											for i in phr :

												cities_dep.append(i)
										
											gare_arr.append(entities_gares[0])
									if k > j : 
										for i in phr :
											cities_arr.append(i)
										gare_dep.append(entities_gares[0])
					

					if len(cities_dep) == 2 :
								if cities_dep[0] == cities_dep[1]:
									cities_dep.remove(cities_dep[1])
					if len(cities_arr) == 2 :
								
								if cities_arr[0] == cities_arr[1]:
									cities_arr.remove(cities_arr[1])
					cities_arr = list(dict.fromkeys(cities_arr))
					cities_dep = list(dict.fromkeys(cities_dep))
					print("okkkkkkkkkkkkkkkkkkkkkkk")
					print(cities_dep)
					print(cities_arr)
					print(gare_dep)
					print(gare_arr)
			

#le cas de 2 gares
			print("entities_city")
			print(entities_city)
			print("cities_arr")
			print(cities_arr)
			print("cities_dep")
			print(cities_dep)
			
			if len(entities_gares) > 1 and entities_gares[0] != entities_gares[1] :
				print("2 gares")
				print(name_gares)
				gare1_splitted = name_gares[0].split(" ")
				gare2_splitted = name_gares[1].split(" ")
				print("gare1_splitted")
				print(gare1_splitted)
				print("gare2_splitted")
				print(gare2_splitted)
				i1 = msg.find(gare1_splitted[0])
				i2 = msg.find(gare2_splitted[0])
				if i1 > i2 :
					m = gare1_splitted
					gare1_splitted = gare2_splitted
					gare2_splitted = m
					p = entities_gares[0]
					entities_gares[0] =entities_gares[1]
					entities_gares[1] = p
				
				if i2 > i1 :
					print("no")
				if i2 == i1 :
					if gare1_splitted[1] != "" and gare2_splitted[1] != "" :
						i3 = msg.find(gare1_splitted[1])
						i4 = msg.find(gare2_splitted[1])
						if i3 > i4 :
							m = gare1_splitted
							gare1_splitted = gare2_splitted
							gare2_splitted = m
							p = entities_gares[0]
							entities_gares[0] =entities_gares[1]
							entities_gares[1] = p
				print("second")
				print("gare1_splitted")
				print(gare1_splitted)
				print("gare2_splitted")
				print(gare2_splitted)
#take the phrase before both station names
				pre_gare1 = ""
				for i in range(tokens.index(gare1_splitted[0])):
					pre_gare1 = pre_gare1 + " " + tokens[i]
				print("pre_gare1")
				print(pre_gare1)
				pre_gare2 = ""
				gare1splitted_fin = ''
				if len(gare1_splitted) == 1 :
					print("ok1")
					gare1splitted_fin = gare1_splitted[0]
					print(gare1splitted_fin)
					print(gare1_splitted)
					print(gare1_splitted[0])
				if len(gare1_splitted) == 2 :
					print("ok2")
					
					gare1splitted_fin = gare1_splitted[1]
					print(gare1splitted_fin)
				print("okk")
				for i in range(tokens.index(gare1splitted_fin),tokens.index(gare2_splitted[0])):
					print(i)
					pre_gare2 = pre_gare2 + " " + tokens[i]
					
				print("pre_gare2")
				print(pre_gare2)
				

			

				if  "من" in pre_gare1 or  "de" in pre_gare1 or "depuis" in pre_gare1 or  "quitter" in pre_gare1:
					print("de in pregare1")
					gare_dep.append(str(entities_gares[0]))
					print(str(entities_gares[1]))
					gare_arr.append(str(entities_gares[1]))
					print(str(entities_gares[0]))
				elif  "من" in pre_gare2 or  "de" in pre_gare2 or  "depuis" in pre_gare2 or  "quitter" in pre_gare2:
					print("de in pregare2")
					gare_dep.append(str(entities_gares[1]))
					print(str(entities_gares[1]))
					gare_arr.append(str(entities_gares[0]))
					print(str(entities_gares[0]))
				else :
					gare_dep.append(str(entities_gares[0]))
					gare_arr.append(str(entities_gares[1]))
			print("gare_dep")
			print(gare_dep)
			print("gare_arrr")
			print(gare_arr)
			
			cities_arr = list(dict.fromkeys(cities_arr))
			cities_dep = list(dict.fromkeys(cities_dep))

			print('cities_arr')
			print(cities_arr)
			print("cities_dep")
			print(cities_dep)
			
			
			
			
			
			
			
			
			
									
									



			



#Detection Date
			stri = ""
			now = dt.now() 
			date = str(now).split(" ")
				
			now_day_1 = now - timedelta(days=now.weekday())
			current_year = dt.now().year

			dates = {}
			entit_jour = ""
			entit_mois = ""
#detection du jour de la semaine
			for n_week in range(1):
				dates[n_week] = [(now_day_1 + timedelta(days=d+n_week*7)).strftime("%m/%d/%Y") for d in range(7)]
			print(dates)
				
			datas_jour = pd.read_csv('csv_files/jour_dict.csv',sep=';',encoding="utf_8") 
			jour= np.array(datas_jour['jour'])
			print("ok")
			value_jour= np.array(datas_jour['value'])
			print("ok")
			ent_jour = {}
			for i in range(len(jour)):
				ent_jour[jour[i]] = value_jour[i]
			
			stri = ''
			for t in tokens :
				stri = stri + ' ' + t
			print(stri)
			print(match)
			if match != '' :
				toks = stri.replace(match,' ')
			else :
				toks = tokens
			print(toks)
			if isinstance(toks, list):
				print("array")
				tok = toks
			else :
				tok = toks.split(' ')
			print(tok)
			
				
			for word in tok:
				print(word)
				for key in ent_jour:
					if key == word:
						
						print("ok3")
						today_n = datetime.datetime.today().weekday()
						print(today_n)
						print(ent_jour[key])
						if int(ent_jour[key]) < today_n or int(ent_jour[key]) == today_n:
							print("prochain jouuuuuur")
							print(today_n)
							print(ent_jour[key])
							entite_jour = dates[0][int(ent_jour[key])]
							datetimeobject = dt.strptime(entite_jour ,'%m/%d/%Y')
							entit_jour  = datetimeobject.strftime('%d/%m/%Y')
							date_1 = dt.strptime(entit_jour, "%d/%m/%Y")
							date_next_week = date_1 + relativedelta(days=7)
							print(date_next_week)
							date_next = str(date_next_week).split(' ')[0]

							datetimeobject = dt.strptime(date_next ,'%Y-%m-%d')
							entit_jour  = datetimeobject.strftime('%d/%m/%Y')

						else :
							print('jouur de la semaiiine')
							entite_jour = dates[0][int(ent_jour[key])]
							datetimeobject = dt.strptime(entite_jour ,'%m/%d/%Y')
							entit_jour  = datetimeobject.strftime('%d/%m/%Y')
							print(entit_jour)



			
			
					
				
			
						
# "prochain" 
			print("apres midi")
			print(tokens)
			indexs = []
			for j in range(0,len(tokens)):
				if tokens[j] == "après" or tokens[j] == "apres" or tokens[j] == "بعد" or tokens[j] == "باعد":
					indexs.append(j)
					print(j)
					print("apres")
			
			for ind in indexs :
				if  tokens[ind+1] == "midi" or tokens[ind+1] == "الزوال" or tokens[ind+1] == "الظهيرة" or tokens[ind+1] == "زوالا" :
						print("midi")
						print(tokens[j])
						del tokens[ind]


			print(tokens)
			proch = ['prochain','prochaine','suivant','suivante','après','apres','جاي','الجاي','الماجي','الجايا','جايا','الماجيا',"بعد","باعد","جيي"]
			prochain = 0
			for t in tokens :
					if t in proch :
						prochain = 1


			if entit_jour != "" :
				det_date = entit_jour.split("/")
				j = det_date[0]
				m = det_date[1]
				print(j)
				print(m)
				date_jour = str(now).split(" ")
				
				datetimeobjecte = dt.strptime(date_jour[0] ,'%Y-%m-%d')
				jour_t  = datetimeobjecte.strftime('%d/%m/%Y')
				detect_date = jour_t.split("/")
				j_auj = detect_date[0]
				m_auj = detect_date[1]
				print(m_auj)
				print(j_auj)
				
				if int(m_auj) == int(m):
					if int(j_auj) > int(j) :
						print("lundi next week")
						date_2 = dt.strptime(entit_jour, "%d/%m/%Y")
						date_next_w = date_2 + relativedelta(days=7)
						print(date_next_w)
						date_nxt = str(date_next_w).split(' ')[0]
						datetimeobjectee = dt.strptime(date_nxt ,'%Y-%m-%d')
						entit_jour = datetimeobjectee.strftime('%d/%m/%Y')

			

					
						
			print('entitjouur'+entit_jour) 

#detection d'aujourdhui et lyoum		
						
			
				
			if entit_jour == "":
				date = str(now).split(" ")
				print("today")
				print(date)
				for word in tokens: 
							if  word == "ليوم" or word == "aujourd" or word == "aujourdhui" or word == "maintenant" or word == "دابا" or word == "اليوم" or word == "الان" or word == "aujourd'hui":
								entit_jours = date[0]
								datetimeobject = dt.strptime(entit_jours ,'%Y-%m-%d')
								entit_jour  = datetimeobject.strftime('%d/%m/%Y')
							if word == "غدا" or word== "demain" or word== 'غادا' or word =="غادان" or word== "غد" or word == "دماين" or word == "دومان" or word == "غحدا" or word == "dem1" or word== "دوماين" or word =="دمان":
								if prochain == 0 :
									entit_jours = str(datetime.date.today() + datetime.timedelta(days=1))
									datetimeobject = dt.strptime(entit_jours ,'%Y-%m-%d')
									entit_jour  = datetimeobject.strftime('%d/%m/%Y')
									print("*********************1")
									print(str(datetime.date.today() + datetime.timedelta(days=1)))
								if prochain == 1 :
									entit_jours = str(datetime.date.today() + datetime.timedelta(days=2))
									datetimeobject = dt.strptime(entit_jours ,'%Y-%m-%d')
									entit_jour  = datetimeobject.strftime('%d/%m/%Y')
									print("*********************2")
									print(str(datetime.date.today() + datetime.timedelta(days=2)))
							if word== "lendemain":
								entit_jours = str(datetime.date.today() + datetime.timedelta(days=2))
								datetimeobject = dt.strptime(entit_jours ,'%Y-%m-%d')
								entit_jour  = datetimeobject.strftime('%d/%m/%Y')
								print("*********************")
								print(str(datetime.date.today() + datetime.timedelta(days=2)))
							if word== "surlendemain":
								entit_jours = str(datetime.date.today() + datetime.timedelta(days=3))
								datetimeobject = dt.strptime(entit_jours ,'%Y-%m-%d')
								entit_jour  = datetimeobject.strftime('%d/%m/%Y')
								print("*********************")
								print(str(datetime.date.today() + datetime.timedelta(days=3)))
							if word== "hier" or word == "لبارح" or word == "الامس":
								entit_jours = str(datetime.date.today() - datetime.timedelta(days=1))
								datetimeobject = dt.strptime(entit_jours ,'%Y-%m-%d')
								entit_jour  = datetimeobject.strftime('%d/%m/%Y')
								print("*********************")
								print(str(datetime.date.today() - datetime.timedelta(days=1)))
#detection des formats


#format jj/mm/yyyy jj.MM
			list_words = tokens
			
			if entit_jour == "" :
				for i in range(len(list_words)):
					if list_words[i] == "هاد" or list_words[i] == "هذا" :
						if list_words[i+1] == "نهار" or list_words[i+1] == "النهار" :
							entit_jours = date[0]
							datetimeobject = dt.strptime(entit_jours ,'%Y-%m-%d')
							entit_jour  = datetimeobject.strftime('%d/%m/%Y')

			if entit_jour == "": 
					for word in tokens:
						dates = re.search(r'(\d{1,2}([/])\d{1,2}([/])\d{1,4})',word)
						date7 = re.search(r'(\d{1,2}([.])\d{1,2})',word)
						if dates == None :
							print("----------------------------------")
							if date7 != None :
								print("date......... found")
								datetimeobject = dt.strptime(date7.string ,'%d.%m.%Y') 
								entit_jour  = datetimeobject.strftime('%d/%m/%Y')
						else :	
							entit_jour = dates.string 
			tok = ""
			for t in tokens :
				tok = tok + " " + t
#DETECTION DE JJ/MM
			dates1 = re.search(r'(\d{1,2}([/])\d{1,2})',tok)
			print('okkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk')
			if entit_jour == "":
							print("nooooooooooooooooooooooooooooo")
							if dates1 == None :
								print('nooooooooooooooooooooooooooooooooooooooooooooooooooooooooo')
							else :
								print("ooooooooooooooooooooooooooooooooooooooooooooooooooooooook")
								entity_jour  = dates1.group()
								print(dates1.group())
								print("entity_jour")
								print(entity_jour)
								listt = entity_jour.split("/")
								j=listt[0]
								m=listt[1]
								print("JJ/MM")
								print(entity_jour)
								
								entit_jour = entity_jour +"/" +str(current_year)
								
#DETECTION DE JJ-MM-YYYY

			datess = re.search(r'(\d{1,2}([-])\d{1,2}([-])\d{1,4})',tok)
			print('okkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk')
			if entit_jour == "":
							print("nooooooooooooooooooooooooooooo")
							if datess == None :
								print('nooooooooooooooooooooooooooooooooooooooooooooooooooooooooo')
							else :
								print("ooooooooooooooooooooooooooooooooooooooooooooooooooooooook")
								entity_jour  = datess.group()
								tt = datess.group().split()
								print(tt[0])
								datetimeobject = dt.strptime(tt[0] ,'%d-%m-%Y')
								print(datetimeobject)
								entit_jour  = datetimeobject.strftime('%d/%m/%Y')
#DETECTION DE JJ-MM		
							dates2 = re.search(r'(\d{1,2}([-])\d{1,2})',tok)
							if dates2 != None :
								print("----------------------------------")
								tt = dates2.group().split()
								print(tt[0])
								datetimeobject = dt.strptime(tt[0],'%d-%m')
								print(datetimeobject)
								entit_jour_sans_annee  = datetimeobject.strftime('%d/%m')
								listt = entit_jour_sans_annee.split("/")
								j=listt[0]
								m=listt[1]
								entit_jour = entit_jour_sans_annee  + "/" +str(current_year)
								
								print(entit_jour)
							else : 
								print("no")
			#DETECTETION DE 06 12 COMME DATE
							'''dates3 = re.search(r'(\d{1,2}.\d{1,2})',tok)
							print(tok)
							if dates3 != None :
								print('date3')
								tt = dates3.group().split()
								text = tt[0] +' ' +tt[1]
								datetimeobject = dt.strptime(text,'%d %m')
								print(datetimeobject)
								entit_jour_sans_anne  = datetimeobject.strftime('%d/%m')
								entit_jour = entit_jour_sans_anne + "/2020"
								print(entit_jour)

							'''	

			tok = ""
			for t in tokens :
				tok = tok + " " + t
#DETECTION DE JJ MM ET JJ MM 2020

			date3 = re.search(r'(\d{1,2}([\s])\d{1,2})',tok)
				
			l = []
			bb = ""
			if entit_jour == "":
							print('date full-------------------------------------------------------------------------')
							if date3 != None :
								print('date full-------------------------------------------------------------------------')
								entitee_jour = date3.string
								print(entitee_jour)
								entitees_jour= entitee_jour.split(" ")
								print(entitees_jour)
								for i in entitees_jour :
									if i.isdigit() :
										if  i!= "2021":
											print('i is digit')
											l.append(i)
											l.append("/")
										else :
											l.append(i)
									else :
										print("CLS")
								print(l)
								for t in l :
									if t != "2021" :
										bb = bb + t
								entiti_jour = bb 
								print(entiti_jour)
								listt = entiti_jour.split("/")
								j=listt[0]
								m=listt[1]
								
								entit_jour = entiti_jour   +str(current_year)

			print("entite_jour"+entit_jour)

		
## Extractor mois :
			print("month detection :::::::")
				#detect month written in arabic words 	
			datas = pd.read_csv('csv_files/mois_dict.csv',sep=';',encoding="utf_8") 
			mois= np.array(datas['mois'])
				
			value= np.array(datas['value'])
			ent_mois = {}

			for i in range(len(mois)):
					ent_mois[mois[i]] = value[i]

			if entit_mois == "" :
				
					for word in tokens:
						for key in ent_mois:
							if key == word:
							
								entit_mois = str(ent_mois[key])
				
			if entit_mois == "" :
					print("there is no month !!!!!!")
			else : 
					print("***********************month in arabic words"+entit_mois)
				# detect month
				
			n = 0
			nb = ""
	#detect the word chhr in the sentence and take the following word if entit_mois is not already full
			
			nbre_ar = pd.read_csv('csv_files/nbre_ar.csv',sep=';',encoding="utf_8") 
			nbre= np.array(nbre_ar['nbre'])
				
			value= np.array(nbre_ar['value'])
			ent_nbre = {}
			month_arab = 0
			for i in range(len(nbre)):
					ent_nbre[nbre[i]] = value[i]
			if entit_mois == "":
					month_arab=0
					for j in range(len(tokens)):
						if tokens[j] == "شهر" or tokens[j] == "الشهر" or tokens[j] =="شحر" :
								n = j
								month_arab=1
					nb = tokens[n+1]
		#detect month after the word 'month' written in digital numbers 
					#for u in range(n,len(tokens)):
					#	reste= reste +" " + tokens[u]
					print("nb"+ nb)
					if nb.isdigit() and int(nb) < 13:
						entit_mois = nb
					else: 
						print("no digital ")
						for key in ent_nbre :
							if key == nb :
								entit_mois = str(ent_nbre[key])
								print("october")
			mois_fr = -2
			if entit_mois == "" :
				for j in range(len(tokens)):
						if tokens[j] == "mois" :
								mois_fr= j
								print(mois_fr)
								print("----------------------------------------")
								print(tokens[mois_fr+1])
				if tokens[mois_fr+1].isdigit() and int(tokens[mois_fr+1]) < 13:
						entit_mois = tokens[mois_fr+1]
		#detect month after 'month' written in arabic numbers
			if entit_mois == '':
						print("*******************************************************still no month")
						conv_mon = text2number(nb)
						if conv_mon != 0:
							print("converted month number")
							print(conv_mon)
							entit_mois = conv_mon
						else :
							print('no month in arabic numbers')
			else : 
						print("********************************************************month"+entit_mois)


			current_month = dt.now().month
			current_year = dt.now().year
			print(entit_jour)
			print("okkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk")
			
				
		
	## Extract number
			entity_numb = ""
			for t in tokens :
				if t.isdigit() and t!= "2020" and t != '2021':
					entity_numb = t
			

			text1= ''
			texte= ''
			if n == 0 :
				text1 = text1 + " " + tokens[0]
			else : 
				for i in range(0,n):
					text1 = text1 + " " + tokens[i]
			for i in range(0,len(tokens)):
					texte = texte + " " + tokens[i]
			print("text1"+str(n))
			print(tokens[0])
			print(text1) 
			
			list_numb = []
			ph = ''
			texte11 = text1.split(" ")
			print(texte11)
	#detect day if before word chhr and digit
			for word in texte11:
					ph = ph + " " + word
					if word.isdigit() :
						print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"+word)
						if word != '2020' and word != "2021":
							entity_numb = word
			if len(entity_numb) == 1 :
					entity_numb = "0"+entity_numb
				
	#detect day if before word chhr and written in arabic words
			print(entit_jour)
			print("okkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk")
			conv_num = text2number(text1)
			print(conv_num)
			if conv_num == 0 :
					print("no")
			else : 
					entity_numb = conv_num
			print(entity_numb)
			print("entitynumb")
			print("------------------------------list nombres en arabe")
			print(entity_numb)
			#if month_arab == 0 :
					#conv_num = text2number(texte)
					#if conv_num == 0 :
						#print("no arabic number")
					#else :
						#if conv_num < 32 :
							#entity_numb = conv_num
			print("entitynumbbb")
			print(entity_numb)
#dans 2 jours / dans deux jours
			nbre_ar = pd.read_csv('csv_files/nbre_ar.csv',sep=';',encoding="utf_8") 
			nbre= np.array(nbre_ar['nbre'])
				 
			value= np.array(nbre_ar['value'])
			ent_nbre = {}
			for i in range(len(nbre)):
						ent_nbre[nbre[i]] = value[i]
			key_numb= ''
			key_val = ''
			for w in tokens:
					for key in ent_nbre:
							if key == w :
								print('keeeeeeeeeey')
								print(w)
								print(key)
								key_numb = key
								key_val = ent_nbre[key]
			print(key_numb)
			print(key_val)
			if entit_jour == "":
				d = -1
				for j in range(len(tokens)):
					if tokens[j] =="jour" or tokens[j] =='jours' or tokens[j] == 'أيام' or tokens[j] == 'يوم':
						d = j

				if tokens[d-1].isdigit():
					dig = tokens[d-1]
				
					entit_jours = str(datetime.date.today() + datetime.timedelta(days=int(dig)))
					datetimeobject = dt.strptime(entit_jours ,'%Y-%m-%d')
					entit_jour  = datetimeobject.strftime('%d/%m/%Y')


				print(tokens[d-1])

				if tokens[d-1] == key_numb :
					print('d-1')
					dig = key_val
					entit_jours = str(datetime.date.today() + datetime.timedelta(days=int(dig)))
					datetimeobject = dt.strptime(entit_jours ,'%Y-%m-%d')
					entit_jour  = datetimeobject.strftime('%d/%m/%Y')
			print("dans queeelqueeees jouuurs")
			print(entit_jour)
			print(key_numb)
			

				
			nbre_ar = pd.read_csv('csv_files/nbre_ar.csv',sep=';',encoding="utf_8") 
			nbre= np.array(nbre_ar['nbre'])
				 
			value= np.array(nbre_ar['value'])
			ent_nbre = {}
			for i in range(len(nbre)):
						ent_nbre[nbre[i]] = value[i]
			if entity_numb == 0:
					print("entitynumber 0")
					nbr = ""
					for w in tokens:
						for key in ent_nbre:
							if key == w :
								print("w")
								print(w)
								entity_numb = ent_nbre[key]
#if entit_mois is more than 12 
			print("yeeeeeeeeeeeeeeeees heeeeeeeeeeere")
			print(entity_numb)
			#if entit_mois != "" :
				#if int(entit_mois) > 12 :
					#entit_mois = ""
			if len(str(entity_numb)) == 1 :
				entity_numb = "0" + str(entity_numb)

#entit_mois or entity_numb 
			if entit_jour == "":
					if entity_numb != "":
						print(entity_numb)
						if entit_mois != "" :
							print("yes month")
							print(current_month)
							print(entit_mois)
							
							entit_jour = str(entity_numb) + "/" + str(entit_mois) +"/" +str(current_year)
						else :
							entit_jour = str(entity_numb) + "/" + str(current_month) +"/" +str(current_year)
							
						
						
			if len(entit_jour) > 11 :
				entit_jour = ""	
			if entity_numb == "" :
				for word in tokens:
					if word.isdigit() :
						print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++entit_number"+word)
						if word != '2020' and word != "2021":
							entity_numb = word
			if entity_numb == "" :
				for word in tokens:
					for key in ent_nbre:
							if key == word :
								entity_numb = ent_nbre[key]

			if entit_jour =="" :
				nhar = ''
				ch = ''
				for i in range(len(tokens)):
						if tokens[i] == "نهار" or tokens[i] == "يوم" :
									
							nhar = tokens[i+1]
							print("nhaaaar"+ nhar)
							ch = tokens[i+2]
				if nhar.isdigit() and entit_mois != "":
					entit_jour = nhar +"/" + entit_mois +"/" +str(current_year)
				if nhar.isdigit() and entit_mois == "":
					entit_jour = nhar +"/" + str(current_month) +"/" +str(current_year)
				if nhar.isdigit() and ch.isdigit():
					entit_jour = nhar +"/" + ch +"/" +str(current_year)

			entit_jours = date[0]
			datetimeobject = dt.strptime(entit_jours ,'%Y-%m-%d')
			auj  = datetimeobject.strftime('%d/%m/%Y')
			print(entit_jour+"entitjouuuuur")
			print(auj)


#detect moments of the day


			terms = ['عشيه','لعشيا','ليل','soir','midi','matin','العشيه']
			if entit_jour == "" :
				for t in tokens :
					if t in terms :
						entit_jours = date[0]
						datetimeobject = dt.strptime(entit_jours ,'%Y-%m-%d')
						entit_jour  = datetimeobject.strftime('%d/%m/%Y')
			
			

#delete wrong dates with wrong months

			'''if entit_jour != "":
				det_date = entit_jour.split("/")
				mon = det_date[1]
				jouur = det_date[0]
				print(mon)
				if int(mon) > 12 :
					entit_jour = ""
				if int(jouur) > 31 :
					entit_jour = ""
			'''

#delete date anterieurs :
			

			numbers = []
			aujourdhui = str(now).split(" ")
#جوج شهر خمسة
			numbers_ar = []
			if entit_jour == '':
				for t in tokens :
					for key in ent_nbre:
							if t == key :
								numbers_ar.append(ent_nbre[key])
				print("numbers_ar")
				print(numbers_ar)
			
				for t in toks :
					if t.isdigit():
						numbers.append(t)
				print("numbeeers")
				print(numbers)

			




			print("Hour detection :::::::")
			toks = [t.text for t in message.get("tokens")]
			heure = ""
	#Extract regular formats 
			for t in toks:
					print(t)
					hour1=re.search(r'(([0-9]+)+(h|heure|heures).([0-9]+))', t)
					if hour1 == None :
						print("no hour(h)")
						hour1 = re.search(r'(([0-9]+)+(h|heure|heures))',t)
						if hour1 == None :
							
							hour1 = re.search(r'(([0-9]+):([0-9]+))', t)
							if hour1 == None :
								print("no hour(:) detected in extractor")
							else :
								heure = hour1.string
								if len(heure) < 5:
									heure = "0"+heure
								
						else :
							heure1 = hour1.string
							for i in heure1 :
								print(i)
								if i.isdigit():
									heure += i
							heure = heure +":00"
							if len(heure) < 5:
									heure = "0"+heure

					else :
						heure1 = hour1.string
						for i in heure1 :
								print(i)
								if i.isdigit():
									heure += i
								if i == "h" :
									heure = heure + ":"
									continue
						if len(heure) < 5:
									heure = "0"+heure

						print("heur(h) found")
			h=-1






	#Extract heure after sa3a and ma3a 


			if heure == "" :
				for i in range(len(toks)) : 
					if toks[i] == "الساعة" or toks[i] == "ساعة" or toks[i] == "مع" or toks[i]== "معا" or toks[i] == "الساعه" or toks[i] == "ساعه" or toks[i] == "vers":
						h= i
			print(toks[h+1])
			if h == -1 :
				print("no heure")
			else :
				print("yeeeeeeeeeeeees heure !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
				if toks[h+1].isdigit():
					heure = toks[h+1]
					print(heure)
					print('yeeeeeeeeeeeees heure !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
				else :
					for key in ent_nbre:
							if key == toks[h+1] :
								print("//////////////////////////////////////////////////////////////////////////////////"+heure)
								heure = ent_nbre[key]



	#Extract heure with minutes written in darija 

			dat = pd.read_csv('csv_files/minutes.csv',sep=';',encoding="utf_8") 
			mins= np.array(dat['mins'])
				
			vale= np.array(dat['value'])
			ent_min = {}
			for o in range(len(dat)):
				ent_min[mins[o]] = vale[o]
			dats = pd.read_csv('csv_files/moins_minutes.csv',sep=';',encoding="utf_8") 
			mi= np.array(dats['min'])
			vals= np.array(dats['value'])
			ent_moins_mins = {}
			for o in range(len(dat)):
						ent_moins_mins[mi[o]] = vals[o]
			moins = 0 
			for t in toks : 
				if t == 'قل':
					moins = 1
			hh = [0]
			if len(heure)> 2 :
				hh = heure.split(":")
				h = hh[0]
			else :
				h = 0
			print(h)
			print(hh)
			if heure != "" and int(h) < 19:
				print("111111111111111111111111111111111111111111")
				for t in toks :
					for key in ent_min:
						if key == t and moins == 0 :
								if len(str(ent_min[key]))!= 1 :
									heure = heure + ':' + str(ent_min[key])
									#print("ok2")

								else :
									minute = str(ent_min[key])

									heure = heure + ':0' + str(ent_min[key])
			print(heure)	
			if heure != "" and int(h) < 19:
				for t in toks :
					for key in ent_moins_mins:
							if key == t and moins == 1 :
								if len(str(ent_moins_mins[key]))!= 1 :
									minute = str(ent_moins_mins[key])
									heure = heure + ':' + str(ent_moins_mins[key])

								else :
									minute = str(ent_moins_mins[key])

									heure = heure + ':0' + str(ent_moins_mins[key])
			print("heur"+heure)


#detect hour from entity_number

			if entity_numb != "" and heure == "" and int(entity_numb) < 24  :
				#print(moins)
				for t in toks :
					#print(t)
					for key in ent_min:
						if moins == 0 :
							if key == t  :
								print("ok4")
								if len(str(ent_min[key]))!= 1 :
									minute = str(ent_min[key])
									heure = entity_numb+ ':' + str(ent_min[key])

								else :
									minute = str(ent_min[key])

									heure = entity_numb + ':0' + str(ent_min[key])
			if entity_numb != "" and heure == "" :
				for t in toks :
					for key in ent_moins_mins:
							if key == t and moins == 1 :
								print("ok5")
								if len(str(ent_moins_mins[key]))!= 1 :
									minute = str(ent_moins_mins[key])
									heure = entity_numb + ':' + str(ent_moins_mins[key])

								else :
									minute = str(ent_moins_mins[key])

									heure = entity_numb + ':0' + str(ent_moins_mins[key])
			d = 0
			k = -1
			if heure.isdigit():
				if int(h) < 19 :
					if len(heure) == 1 or len(heure) ==2 :
						for tt in toks :
							if tt.isdigit():
								print("lol")
								k = tt
								print(k)
								d = 1
			print('last ok')
			print(heure)
			if k != -1 :
				if k != heure :
					heure = heure + ':' + k 
				else :
					heure = heure + ':00'
			if len(heure)== 3 :
				if entity_numb!= "" and int(entity_numb) < 19 and entity_numb != heure:
					heure =  heure + entity_numb  
			print(entity_numb)
			print(heure)
			if d == 0 and len(heure) < 3 and heure != "":
				heure = heure + ":00"
			
	#Extract heure with minutes sous forme daqiqa 
			numbers = []
			for i in toks :
				if i.isdigit():
					numbers.append(i)
			phrase = ""
			for t in tokens :
				phrase = phrase + " " + t
			numb = ""
			for word in tokens:
					for key in ent_nbre:
							if key == word :
								numb = ent_nbre[key]
			print(numbers)
			print(len(numbers))
			minu = 0
			print('[((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((((')
			if len(numbers) == 1 or len(numbers) == 2   :
				print("yes")
				if  heure == "":
					print("55555")
					minut = "00"
					for j in range (len(toks)) :
						if toks[j] == 'دقيقة' or toks[j] == "دقيقه" :
							minut = toks[j-1]
							minu = 1
					if minut.isdigit() :
						if numbers[0] != minut :
							heure = numbers[0] + ':' + minut
						else :
							heure = numb + ':' + minut
					else : 
						min_ar = text2number(phrase)
						print(min_ar)
						if min_ar == 0 :
								print("no")
						else :
							if numbers[0] != minut :
								heure = numbers[0] + ":" + str(min_ar)
							else :
								heure = numb + ":" + str(min_ar)
			print('yees')
			if heure.startswith(":"):
				s = heure.split(':')
				print(s[1])
				l = []
				for i in s[1] :
					l.append(i)
				if len(l)==2 :
					heure = '0' +l[1] + ':' + l[0] + '0'
			print("yeees")
			if numb != "" and heure == "" :
					minut = "00"
					for r in range (len(toks)) :
						if toks[r] == 'دقيقة' or toks[r] == "دقيقه" :
							minut = toks[r-1]
					if minut.isdigit():

						heure = numb + ":" +minut
					else :
						min_ar = text2number(phrase)
						print(min_ar)
						if min_ar == 0 :
								print("no")
						else : 
								heure = numb + ":" + str(min_ar)
#tranche d'horaire


			horaire = pd.read_csv('csv_files/horaires_oncf.csv',sep=';',encoding="utf_8") 
			horaires= np.array(horaire['horaire'])
			print("ok")
			value_horaire= np.array(horaire['value'])
			print("ok")
			ent_hor = {}
			tranche_horaire = ""
			for i in range(len(horaire)):
				ent_hor[horaires[i]] = value_horaire[i]
			for word in tokens:
				for key in ent_hor:
					if key == word:
						tranche_horaire = ent_hor[key]


			if entit_jour == "":
				if tranche_horaire != "":
					entits_jour = date[0]
					datetimeobject = dt.strptime(entits_jour ,'%Y-%m-%d')
					entit_jour  = datetimeobject.strftime('%d/%m/%Y')

						
						
			



			print("yeeees")
			if heure.startswith("3") :
				heure = heure.replace("3:","15:")
			if heure.startswith("03") :
				heure = heure.replace("03:","15:")
			if heure.startswith("2") :
				heure = heure.replace("2:","14:")
			if heure.startswith("02") :
				heure = heure.replace("02:","14:")
			if heure.startswith("4") :
				heure = heure.replace("4:","16:")
			if heure.startswith("04") :
				heure = heure.replace("04:","16:")
			if heure.startswith("5") :
				heure = heure.replace("5:","17:")
			if heure.startswith("05") :
				heure = heure.replace("05:","17:")
			if heure.startswith("6") :
				heure = heure.replace("6:","18:")
			if heure.startswith("06") :
				heure = heure.replace("06:","18:")
			if heure.startswith("01") :
				heure = heure.replace("01:","13:")
			if heure.startswith("7") :
				heure = heure.replace("7:","19:")
			if heure.startswith("07") :
				heure = heure.replace("07:","19:")

			print("yeeeeees")

#detection de classe_carte


			data_classe = pd.read_csv('csv_files/classe_carte.csv',sep=';',encoding="utf_8")
			print("ok11")
			classe_val = np.array(data_classe['classe'])
			print("ok12")
			classe_code = np.array(data_classe['value'])
			print("ok13")
			ent_cl = {}
			entity_classe = ""

			for i in range(len(classe_val)):
				ent_cl[classe_val[i]] = classe_code[i]

			print("ok1")
			match = ''
			names_word =[]
			
			for key in ent_cl:
				classe = re.search(key,msg)
				
				if classe != None :
					print("ok2")
					match_cl = classe.group()
					print("MATCH")
					
					entity_classe = str(ent_cl[key])
					print("entity_class")
					
					break
			

			if entity_classe == "":
				txt = message.text
				
				print("txt")
				for key in ent_cl:
					classe = re.search(key,txt)
				
					if classe != None :
						print("ok2")
						match_cl = classe.group()
						
						
						entity_classe = str(ent_cl[key])
						print("entity_class!!!!!!!!!!!!!!!!!!!!!!!")
						print(entity_classe)
				




			



			


#Detection des cartes d'abonnement




			data_carte = pd.read_csv('csv_files/carte_oncf.csv',sep=';',encoding="utf_8")
			print("ok11")
			carte_val = np.array(data_carte['carte'])
			print("ok12")
			carte_code = np.array(data_carte['value'])
			print("ok13")
			ent_card = {}
			entity_carte = ""

			for i in range(len(carte_val)):
				ent_card[carte_val[i]] = carte_code[i]

			print("ok1")
			match_card = ''
			names_word =[]
			
			for key in ent_card:
				card = re.search(key,msg)
				
				if card != None :
					print("ok2")
					match_card = card.group()
					print("MATCH")
					
					entity_carte = str(ent_card[key])
					print("entity_carte")
					print(entity_carte)
					break
				else :
					print("oknew00")
			print("oknew")
			code_card = ""
			if entity_classe=="1":
				if entity_carte == "NGC":
					code_card = "NGC1"
				
				if entity_carte == "NB":
					code_card = "NB1"
				
				if entity_carte == "NH":
					code_card = "NH1"

				if entity_carte == "NRS":
					code_card = "NRS1"

				if entity_carte == "FF":
					code_card = "FP"
				
				if entity_carte == "DB":
					code_card = "DB"
				
				if entity_carte == "N":
					code_card = "AC"
				
				if entity_carte == "10ZEN":
					code_card = "DA"
				if entity_carte == "DM":
					code_card = "DM"
			print("oknew2")
			if entity_classe=="2":
				if entity_carte == "NGC":
					code_card = "NGC2"
				
				if entity_carte == "NH":
					code_card = "NH2"

				if entity_carte == "NRS":
					code_card = "NRS2"

				if entity_carte == "FF":
					code_card = "FD"
				
				if entity_carte == "DB":
					code_card = "DQ"
				
				if entity_carte == "N":
					code_card = "AY"
				
				if entity_carte == "NB":
					code_card = "NB2"
				
				if entity_carte == "10ZEN":
					code_card = "DZ"
				if entity_carte == "DM":
					code_card = "MD"
			
			if entity_classe == "":
				code_card = entity_carte

			print("oknew3")

			entity_code_card = self.convert_to_code_card(code_card)

			entity_card = self.convert_to_card(entity_carte)
			entity_classe = self.convert_to_classe(entity_classe)
					

			entity_heure = self.convert_to_heure(heure)
			entity_tranche_horaire = self.convert_to_rasa_horaire(tranche_horaire)

			month = []
			month = self.convert_to_rasa_month(entit_mois)
			
			date_conv = self.convert_to_rasa_day(entit_jour)
			numbers = self.convert_to_rasa_numbers(entity_numb)
			
			


			if cities_dep == [''] and gare_dep != []:
				gare_dep_conv = self.convert_gare_dep(gare_dep)
				print("yes1")
			if gare_dep == [] and cities_dep != ['']:
				print("yes2")
				gare_dep_conv = self.convert_ville_dep(cities_dep)
			if cities_dep == [''] and gare_dep == []:
				print("yes3")
				gare_dep_conv = self.convert_gare_dep(cities_dep)
			if cities_dep != [''] and gare_dep != []:
				print("yes4")
				print(cities_dep)
				print(gare_dep)
				gare_dep_conv = self.convert_gare_dep(gare_dep)
			if cities_arr == [''] and gare_arr != []:
				print("yes5")
				gare_arr_conv = self.convert_gare_arr(gare_arr)
			if cities_arr != [''] and gare_arr ==[]:
				print("yes6")
				gare_arr_conv = self.convert_ville_arr(cities_arr)
			if cities_arr == [''] and gare_arr ==[]:
				print("yes7")
				gare_arr_conv = self.convert_gare_arr(cities_arr)
			if cities_arr != [''] and gare_arr != []:
				print("yes8")
				print(cities_arr)
				print(cities_dep)
				gare_arr_conv = self.convert_gare_arr(gare_arr)
			
			


			print("ok0")
			for t in tokens :
				print(t)
				print(len(t))
			print("ok1")
			print(gare_arr)
			print("1")
			print(cities_arr)
			print("2")
			print(gare_dep)

			print(entit_mois)
			

		

			print(gare_dep_conv)
			print(gare_arr_conv)
			print([entity_classe])
			#message.set("city_arr", [city_arr_conv], add_to_output=True)
			print("ok1")
			#message.set("city_depart", [city_dep_conv], add_to_output=True)
			print("ok1")
			
			
			message.set("gare_depart", gare_dep_conv, add_to_output=True)
			print("ok1")
			message.set("CODE_CARD", code_card, add_to_output=True)
			print("ok2")
			message.set("gare_arr", gare_arr_conv, add_to_output=True)
			print("ok2")
			message.set("date", [date_conv], add_to_output=True)
			print("ok1")
			message.set("number", numbers, add_to_output=True)
			print("ok1")
			message.set("mois", month, add_to_output=True)
			
			print("okk")
			message.set("tranche_horaire", entity_tranche_horaire, add_to_output=True)
			print("okk2")
			message.set("Classe", [entity_classe], add_to_output=True)
			print("ok1")
			message.set("Card_oncf", [entity_card], add_to_output=True)
			print("ok1")
			