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
        
            string = ""
			for t in tokens :
				string = string + t + ' '

#change egyptian numbers

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
							if  word == "ليوم" or word == "aujourd" or word == "aujourdhui" or word == "maintenant" or word == "دابا" or word == "اليوم":
								entit_jours = date[0]
								datetimeobject = dt.strptime(entit_jours ,'%Y-%m-%d')
								entit_jour  = datetimeobject.strftime('%d/%m/%Y')
							if word == "غدا" or word== "demain" or word== 'غادا' or word== "غد" or word == "دماين" or word == "دومان":
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
##################detection des formats


#format jj/mm/yyyy jj.MM
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
#DETECTION DE JJ MM ET JJ MM 2021

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
								
								entit_jour = entiti_jour  + "/" +str(current_year)

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
			if month_arab == 0 :
					conv_num = text2number(texte)
					if conv_num == 0 :
						print("no arabic number")
					else :
						if conv_num < 32 :
							entity_numb = conv_num
			
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
#if entit_mois is more than 12 
			print("yeeeeeeeeeeeeeeeees heeeeeeeeeeere")
			print(entity_numb)
			if entit_mois != "" :
				if int(entit_mois) > 12 :
					entit_mois = ""
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

			if entit_jour != "":
				det_date = entit_jour.split("/")
				mon = det_date[1]
				jouur = det_date[0]
				print(mon)
				if int(mon) > 12 :
					entit_jour = ""
				if int(jouur) > 31 :
					entit_jour = ""

#delete date anterieurs :
			'''if entit_jour != '' :

				l = entit_jour.split("/")
				j=l[0]
				m=l[1]
				y=l[2]
				aujourdhui = str(now).split(" ")	
				datetimeobjecte = dt.strptime(aujourdhui[0] ,'%Y-%m-%d')
				jour_t  = datetimeobjecte.strftime('%d/%m/%Y')
				detect_date = jour_t.split("/")
				j_j= detect_date[0]
				j_m = detect_date[1]
				j_y = detect_date[2]

				if m > j_m :
					print("next month")
				if m == j_m :
					print("this month")
					if j_j > j :
						entit_jour = ""
					else :
						print(entit_jour)
			numbers = []

			print("entity_numb")
			print(entity_numb)
			print(entit_mois)'''

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



            date_conv = self.convert_to_rasa_day(entit_jour)
            message.set("date", [date_conv], add_to_output=True)
			print("ok1")