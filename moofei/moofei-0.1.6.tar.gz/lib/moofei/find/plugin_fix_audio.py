#!/usr/bin/python
# -*- coding: utf-8 -*-
# editor: mufei(ypdh@qq.com tel:+086 15712150708)
'''
Mufei _ __ ___   ___   ___  / _| ___(_)
| '_ ` _ \ / _ \ / _ \| |_ / _ \ |
| | | | | | (_) | (_) |  _|  __/ |
|_| |_| |_|\___/ \___/|_|  \___|_|
'''



import warnings

try:
    import speech_recognition as sr
except ImportError:
    warnings.warn('Please Import SpeechRecognition pocketsphinx TO pip')
        
try:
    import pocketsphinx
except ImportError:
    pocketsphinx = None
    warnings.warn('Please Import pocketsphinx TO pip')
    
    
from moofei._find import _py, _strtypes,_find_func,_search_func
from moofei.find.cplugin_fix import _StringIO, StringIO, cPlugin_Fix



class cPlugin_Fix_Audio(cPlugin_Fix):
    def all_texts(self):
        Ls = []
        r = sr.Recognizer()
 
        ob = sr.AudioFile(self.fp or self.fpath)
         
        with ob as source:
            audio = r.record(source)
            #print(audio, 'aaaaaaa')
         
        #print(type(audio))
        if pocketsphinx: 
            Ls = r.recognize_sphinx(audio, language='zh-cn')     #识别输出
        else:
            Ls = r.recognize_google(audio, language='zh-CN', show_all= True)
        #print(Ls)
        '''
            SpeechRecognition对语音文件格式有一定要求
            WAV: 必须是 PCM/LPCM 格式
            AIFF
            AIFF-C
            FLAC: 必须是初始 FLAC 格式；OGG-FLAC 格式不可用
        '''
        text = '\n'.join(Ls)
        #print(text)
        return text
        
    def test(self):
        # obtain audio from the microphone
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)  # listen for 1 second to calibrate the energy threshold for ambient noise levels
            print('say something')

            # print("")
            audio = r.listen(source)
        #
        # # recognize speech using Sphinx
        try:
            print("Sphinx thinks you said " + r.recognize_sphinx(audio))
        except sr.UnknownValueError:
            print("Sphinx could not understand audio")
        except sr.RequestError as e:
            print("Sphinx error; {0}".format(e))
            
if __name__ == "__main__":
    cPlugin_Fix_Audio(None).test()        
        
