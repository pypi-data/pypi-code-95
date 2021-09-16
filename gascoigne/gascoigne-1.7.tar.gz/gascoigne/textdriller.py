import numpy as np
import json
import pdfplumber as pf
from PIL import Image
from pdf2image import convert_from_path
import pytesseract
from langdetect import detect_langs
import language_tool_python
import requests


class converter():
    
    def __init__(self,language,tesseract_url,treshold_words,treshold_language,image_extensions=[".jpg",".jpeg",".png",".PNG",".JPG","bmp"],corrector='it'):
        self.language=language
        self.tesseract_url=tesseract_url
        self.treshold_words=treshold_words
        self.treshold_language=treshold_language
        self.image_extensions=image_extensions
        ## locate tesseract
        pytesseract.pytesseract.tesseract_cmd = (self.tesseract_url)
        ## download converter tool
        self.tool=language_tool_python.LanguageTool(corrector)
        
    def pdf_machine(self,url):
        """
        url: url of the pdf file
        return: a text string
        """
        ## create a text container
        text=[]
        ## read file
        try:
            filepf=pf.open(url)
            ## create list of pages
            list_pages=filepf.pages
            ## number of pages
            numb_pages=len(list_pages)
            ## extract text
            for page in list_pages:
                text.append(page.extract_text())
            text=" ".join([str(x) for x in text])
        except:
            text="cannot retrieve text from pdf try extract_text method"
        
        return text


    def pdf_tesseract(self,url):
        """
        url: url of the pdf file from where you want to extract the file
        return: a text strings
        """
        text=[]
        try:        
            collection_of_images=convert_from_path(url)
            for image in collection_of_images:
                    text.append(pytesseract.image_to_string(image))
        except:
            text.append("error")
        text=" ".join([str(x) for x in text])
        return text

    def language_controller(self,text):

        """
        text: a text string
        return: boolean true  if language is correct above the treshold
        """

        try: 
            results=self.detect_langs(text)
            response=(results[0].lang==self.language)&(results[0].prob>=self.treshold_language)
        except:
            response=False
        return response

    
    def run_checks(self,text):
        """
        text: a text string
        """
        status=True

        ## simple check if string is empty
        if len(text)<=self.treshold_words:
            status=False
        ## first check
        if text==None:
            status=False
        ### second check
        if status==True:
            status=self.language_controller(text)
        return status

    def immtex(self,url):
        
        """
        url: url of the image you want to convert
        """
        rot=90
        c=False
        img=Image.open(url)
        vv=pytesseract.image_to_string(img)
        try:
            c=detect_langs(vv)[0].prob>=0.95
        except:
            c=False

        if c==False:
            img.rotate(rot)
            vv=pytesseract.image_to_string(img.rotate(rot))
            try:
                c=detect_langs(vv)[0].prob>=0.95
            except:
                c=False
            rot+=90

        if c==False:

            vv=pytesseract.image_to_string(img.rotate(rot))
            try:
                c=detect_langs(vv)[0].prob>=0.95
            except:
                c=False
            rot+=90

        if c==False:
            img.rotate(rot)
            vv=pytesseract.image_to_string(img.rotate(rot))
            try:
                c=detect_langs(vv)[0].prob>=0.95
            except:
                c=False
            rot+=90

        return vv
    
    
    
    
    
    def extract_text(self,url,correction=False):
        """
        url: the url of the pdf or the image file you want to extract the text
        correction:  correct the text using the languate tool. Note default language is italian.

        """
        if url.endswith(tuple(self.image_extensions)):
            ## it is a web url ?
            if url.startswith("htt"):
                text=self.immtex(requests.get(url, stream=True).raw)
            else:
                text=self.immtex(url)
        else:

            lang_to_search=self.language
            limit_language_probability=self.treshold_language
            ## try pdf machine
            text=self.pdf_machine(url)
            ## drop empty text object
            ## run checks
            if self.run_checks(text)==False:
                text=self.pdf_tesseract(url)    

        
        ## correction
        if correction==True:
            text=self.tool.correct(text)

        return text
    
    
        