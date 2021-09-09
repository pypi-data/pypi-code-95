from rasa.nlu.components import Component
from rasa.nlu import utils
from rasa.nlu.model import Metadata
import os
from datetime import timedelta
import pandas as pd
import re
import typing
#from datetime import date
import dateutil.parser as dparser
import datefinder
import datetime
from dateutil.parser import parse
from typing import Any, Optional, Text, Dict
import numpy as np
from datetime import datetime as dt
import dateutil.parser as dparser
from pyarabic.number import text2number
import datefinder
from dateutil.parser import parse


class Extracteur_cdg(Component):
	
	name = "CDG_EXTRACTION"
	provides = ["entities"]
	requires = ["tokens"]
	defaults = {}
	language_list = ["en"]
	print('initialised the class')

	def __init__(self, component_config=None):
		super(Extracteur_cdg, self).__init__(component_config)

	def train(self, training_data, cfg, **kwargs):
		"""Load the sentiment polarity labels from the text
		   file, retrieve training tokens and after formatting
		   data train the classifier."""



	def convert_to_mois(self, value):
		"""Convert model output into the Rasa NLU compatible output format."""

		entity = {"value": value,
				  
				  "entity": "MOIS",
				  "extractor": "extractor"}

		return entity
	
	def convert_to_attest(self, value):
		"""Convert model output into the Rasa NLU compatible output format."""

		entity = {"value": value,
				  
				  "entity": "ATTESTATION",
				  "extractor": "extractor"}

		return entity

	def convert_to_heure(self, value):
		"""Convert model output into the Rasa NLU compatible output format."""

		entity = {"value": value,
				  
				  "entity": "HOUR",
				  "extractor": "extractor"}

		return entity

	def convert_to_jour(self, value):
		"""Convert model output into the Rasa NLU compatible output format."""

		entity = {"value": value,
				  
				  "entity": "JOUR",
				  "extractor": "extractor"}

		return entity
	
	def convert_to_numb(self, value):
		"""Convert model output into the Rasa NLU compatible output format."""

		entity = {"value": value,
				  
				  "entity": "NUMBER",
				  "extractor": "extractor"}

		return entity
	
		
    ## Extract mois
	

	def process(self, message, **kwargs):
		"""Retrieve the tokens of the new message, pass it to the classifier
			and append prediction results to the message class."""
		entit_mois = ""
		tokens = [t.text for t in message.get("tokens")]
		print(tokens)
		entit_attest = ""
		entit_jour = ""
		current_month = 0
		current_month = dt.now().month 

		if not self :
			entities = []
		else:
			entity_mois= []
#Detecter le jour 
		print("Day detection :::::::")
		stri = ""
		now = dt.now() 
			
		now_day_1 = now - timedelta(days=now.weekday())

		dates = {}
			

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
			
		for word in tokens:
			for key in ent_jour:
				if key == word:
					print(word)
					if len(dates[0]) < int(ent_jour[key]) :
						print("jour date out of range")
					else :
						entite_jour = dates[0][int(ent_jour[key])]
						datetimeobject = dt.strptime(entite_jour ,'%m/%d/%Y')
						entit_jour  = datetimeobject.strftime('%d/%m/%Y')
					

		print("entite_jour"+entit_jour)		
		if entit_jour == "":
			date = str(now).split(" ")
			print("today")
			print(date)
			for word in tokens: 
						if  word == "ليوم" :
							entit_jours = date[0]
							datetimeobject = dt.strptime(entit_jours ,'%Y-%m-%d')
							entit_jour  = datetimeobject.strftime('%d/%m/%Y')
						if word == "غدا" :
							entit_jours = str(datetime.date.today() + datetime.timedelta(days=1))
							datetimeobject = dt.strptime(entit_jours ,'%Y-%m-%d')
							entit_jour  = datetimeobject.strftime('%d/%m/%Y')
							print("*********************")
							print(str(datetime.date.today() + datetime.timedelta(days=1)))
		if entit_jour == "":
				for word in tokens:
					dates = re.search(r'(\d{1,2}([/])\d{1,2}([/])\d{1,4})',word)
					
					if dates == None :
						dates2 = re.search(r'(\d{1,2}([.\-])\d{1,2})',word)
						if dates2 != None :
							datetimeobject = dt.strptime(dates2.string ,'%d-%m-%Y') 
							entit_jour  = datetimeobject.strftime('%d/%m/%Y')
					else :
						entit_jour = dates.string 
		tok = ""
		for t in tokens :
			tok = tok + " " + t
		dates1 = re.search(r'(\d{1,2}([/])\d{1,2})',tok)
		print('okkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk')
		if entit_jour == "":
						print("nooooooooooooooooooooooooooooo")
						if dates1 == None :
							print('nooooooooooooooooooooooooooooooooooooooooooooooooooooooooo')
						else :
							print("ooooooooooooooooooooooooooooooooooooooooooooooooooooooook")
							entity_jour  = dates1.string.split(' ') 
							print(entity_jour)
							entit_jour = entity_jour[1] + "/2020"
							

		tok = ""
		for t in tokens :
			tok = tok + " " + t
		
		date3 = re.search(r'(\d{1,2}([\s])\d{1,2})',tok)
		date4 = re.search(r'(\d{1,2}([\s])\d{1,2}([\s])\b2020)',tok)	
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
									if  i!= "2020":
										print('i is digit')
										l.append(i)
										l.append("/")
									else :
										l.append(i)
								else :
									print("CLS")
							print(l)
							for t in l :
								if t != "2020" :
									bb = bb + t
							entit_jour = bb + "2020"
							print(entit_jour)

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
					if tokens[j] == "شهر" or tokens[j] == "الشهر" :
							n = j
							month_arab=1
				if n ==0:
					nb = ""
				else :
					nb = tokens[n+1]
	#detect month after the word 'month' written in digital numbers
				#for u in range(n,len(tokens)):
				#	reste= reste +" " + tokens[u]
				print("nb"+ nb)
				if nb.isdigit():
					entit_mois = nb
				else: 
					print("no digital ")
					for key in ent_nbre :
						if key == nb :
							entit_mois = str(ent_nbre[key])
							print("october")
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

		print(entit_jour)
		print("okkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk")
		## Extractor attestation :
		print("attest detection :::::::")
		print(tokens)
		tokens = [t.text for t in message.get("tokens")]
		datas = pd.read_csv('csv_files/type_attest.csv',sep=';',encoding="utf_8") 
		att= np.array(datas['attest'])
				
		val = np.array(datas['type'])
		print("okkk")
		ent_att = {}
		for i in range(len(att)):
					ent_att[att[i]] = val[i]
		print('ok')
				
		for word in tokens:
					for key in ent_att:
						if key == word:
							
							entit_attest = str(ent_att[key])
		print('okkkkkkkk')
		print(tokens)
			
	
## Extract number
		text1= ''
		texte= ''
		if n == 0 :
			print('ok')
			text1 = text1 + " " + tokens[0]
			print('ok')
		else : 
			for i in range(0,n):
				text1 = text1 + " " + tokens[i]
				print('ok')
		for i in range(0,len(tokens)):
				texte = texte + " " + tokens[i]
				print('ok')
		print("text1"+str(n))
		print(tokens[0])
		print(text1) 
		entity_numb = ""
		list_numb = []
		ph = ''
		texte11 = text1.split(" ")
		print(texte11)
#detect day if before word chhr and digit
		for word in texte11:
				ph = ph + " " + word
				if word.isdigit() :
					print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"+word)
					if word != '2020':
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
		if month_arab == 0 :
				conv_num = text2number(texte)
				if conv_num == 0 :
					print("no arabic number")
				else :
					if conv_num < 32 :
						entity_numb = conv_num
		
		
			
		nbre_ar = pd.read_csv('csv_files/nbre_ar.csv',sep=';',encoding="utf_8") 
		nbre= np.array(nbre_ar['nbre'])
			
		value= np.array(nbre_ar['value'])
		ent_nbre = {}
		for i in range(len(nbre)):
					ent_nbre[nbre[i]] = value[i]
		if entity_numb == 0:
				nbr = ""
				for w in tokens:
					for key in ent_nbre:
						if key == w :
							entity_numb = ent_nbre[key]
		if len(str(entity_numb)) == 1 :
			entity_numb = "0" + str(entity_numb)
		if entit_jour == "":
				if entity_numb != "":
					print(entity_numb)
					if entit_mois != "" :
						if int(entit_mois) < current_month and int(entity_numb) < 32 :
								entit_jour = str(entity_numb) + "/" + str(entit_mois) + "/" + "2021"
						print("month")
						entit_jour = str(entity_numb) + "/" + entit_mois + "/" + "2020"
					if entit_mois == "" and int(entity_numb) < 32:
						print("no month")
						entit_jour = str(entity_numb) + "/" + str(current_month)+ "/" + "2020"
						print("ok")
					
		if len(entit_jour) > 11 :
			entit_jour = ""	
		if entity_numb == "" :
			for word in tokens:
				if word.isdigit() :
					print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++entit_number"+word)
					if word != '2020':
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
				entit_jour = nhar +"/" + entit_mois + "/2020"
			if nhar.isdigit() and entit_mois == "":
				entit_jour = nhar +"/" + str(current_month) + "/2020"
			if nhar.isdigit() and ch.isdigit():
				entit_jour = nhar +"/" + ch + "/2020"

## Extract hour colles/sep
		print(entit_jour)
		print("okkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk")
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
				if toks[i] == "الساعة" or toks[i] == "ساعة" or toks[i] == "مع" or toks[i]== "معا" or toks[i] == "الساعه" or toks[i] == "ساعه":
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
		if entity_numb != "" and heure == "" :
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
		if len(numbers) == 1 or len(numbers) == 2   :
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
		if heure.startswith(":"):
			s = heure.split(':')
			print(s[1])
			l = []
			for i in s[1] :
				l.append(i)
			if len(l)==2 :
				heure = '0' +l[1] + ':' + l[0] + '0'

		if numb != "" and heure == "" :
				minut = "00"
				for j in range (len(toks)) :
					if toks[j] == 'دقيقة' or toks[j] == "دقيقه" :
						minut = toks[j-1]
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
		if heure.startswith("1") :
			heure = heure.replace("1:","13:")
		if heure.startswith("01") :
			heure = heure.replace("01:","13:")
		if heure.startswith("7") :
			heure = heure.replace("7:","19:")
		if heure.startswith("07") :
			heure = heure.replace("07:","19:")



#detect numbers in arabic:
		entity_heure = self.convert_to_heure(heure)
		entity_numbs = self.convert_to_numb(entity_numb)
		entity_jour = self.convert_to_jour(entit_jour)
		entity_mois = self.convert_to_mois(entit_mois)
		entity_attest = self.convert_to_attest(entit_attest)



		message.set("entities_heure", [entity_heure], add_to_output=True)
		message.set("entities_jour", [entity_jour], add_to_output=True)
		message.set("entities_numb", [entity_numbs], add_to_output=True)
		message.set("entities_mois", [entity_mois], add_to_output=True)
		message.set("entity_attestation", [entity_attest], add_to_output=True)