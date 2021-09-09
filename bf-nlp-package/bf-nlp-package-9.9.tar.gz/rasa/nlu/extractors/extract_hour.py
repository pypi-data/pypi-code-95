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

	
	def convert_to_heure(self, value):
		"""Convert model output into the Rasa NLU compatible output format.""" 

		entity = {"value": value,
				  
				  "entity": "HOUR",
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


            print("Hour detection :::::::")
			toks = [t.text for t in message.get("tokens")]
			heure = ""
            entity_numb = ""
			for t in tokens :
				if t.isdigit() and t!= "2020" and t != '2021':
					entity_numb = t
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



            entity_heure = self.convert_to_heure(heure)
            message.set("entities_heure", [entity_heure], add_to_output=True)
			print("okk")