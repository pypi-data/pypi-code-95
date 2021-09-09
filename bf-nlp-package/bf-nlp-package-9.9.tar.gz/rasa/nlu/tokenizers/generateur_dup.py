import os
import json
def generateur_dup(direc):
        os.remove("dictionaries/dict_dupont.txt")
        
        mon_fich = open("dictionaries/dict_dupont.txt", "a")
        for fichie in os.listdir(direc):
                
                with open(direc+'/'+fichie, "r",encoding="utf_8") as f:
                        list_dic = json.load(f)
                        
                
                for i in list_dic["rasa_nlu_data"]["common_examples"]:
                        mon_fichier.write(i["text"]+"\n")
                        mon_fich.write(i["text"]+"\n")

        
        
        mon_fich.close()