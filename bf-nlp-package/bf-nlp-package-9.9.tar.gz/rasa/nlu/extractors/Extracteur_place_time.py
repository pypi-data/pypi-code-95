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


class Extracteur_place_time(Component):
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

	def convert_cities(self, value):
		"""Convert model output into the Rasa NLU compatible output format.""" 

		entity = {"value": value,
				  
				"entity": "CITY",
				"extractor": "extractor"}		
		return entity

	def convert_to_date(self, value):
		"""Convert model output into the Rasa NLU compatible output format.""" 

		entity = {"value": value,
				  
				"entity": "DATE",
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
 
			
			cities = []
			


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
			print('***********Extraction des villes*****')
			print(tokens)

#delete unecessary de
			

			datas = pd.read_csv('csv_files/villes_maroc.csv',sep=';',encoding="utf_8")
			Tville= np.array(datas['ville'])
			Oville= np.array(datas['value'])
			ent_val = {}
			city_dep_conv = []
			
			entities_city = []
			name_city = []
			for i in range(len(Tville)):
				ent_val[Tville[i]] = Oville[i]
			for word in tokens:
				for key in ent_val:
					if key == word:
						print(word)
						name_city.append(word)
						entities_city.append(ent_val[key])
						print(" extracted Token ++++++++++ "+ word)
						break
			print("list city names")
			print(name_city)
			print("list city entities")
			print(entities_city)
			cities_conv = self.convert_cities(entities_city)
			message.set("Cities", cities_conv, add_to_output=True)



#Extraction des dates/jour
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
			
			
				
			for word in tokens:
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
			if entit_jour == "":
				date = str(now).split(" ")
				print("today")
				print(date)
				for word in tokens: 
							if  word == "ليوم" or word == "aujourd" or word == "aujourdhui" or word == "maintenant" or word == "دابا" or word == "اليوم" or word == "الان":
								entit_jours = date[0]
								datetimeobject = dt.strptime(entit_jours ,'%Y-%m-%d')
								entit_jour  = datetimeobject.strftime('%d/%m/%Y')
							if word == "غدا" or word== "demain" or word== 'غادا' or word =="غادان" or word== "غد" or word == "دماين" or word == "دومان":
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

			print(entit_jour)
			entity_jour = self.convert_to_date(entit_jour)
			message.set("DATE", entity_jour, add_to_output=True)