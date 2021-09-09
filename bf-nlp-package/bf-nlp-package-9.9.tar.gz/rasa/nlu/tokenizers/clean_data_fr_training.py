import os
import json 
import jellyfish
def clean_data_fr_training(liste_text):

#Remove punctuation :
    new_texte = ""
    punct='''!()-[]{};:'"\,<>./?#$%^&*_~+='''
    
    
    for t in liste_text :
            if t not in punct :
                
                new_texte = new_texte + " " +  t 
            
#Remove stop word :
    
    new_texte = new_texte.split(" ")
    file1 = open('../stopwords_file_fr.txt', 'r')
    count = 0
    list_stop_words = []
    
    for line in file1:
        
        stop_word = line.strip()
        list_stop_words.append(stop_word)
    
    
    # Closing files
    file1.close()
    text = new_texte
    
    stopwords = []
    for word in text :
        
        if word in list_stop_words :
            
            stopwords.append(word)
    
    for w in stopwords :
        new_texte.remove(w)

    print(new_texte)
    new_list = new_texte.split(' ')
    


    return new_list