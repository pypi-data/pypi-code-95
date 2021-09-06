__name__ = "voice_comm"
__version__ = "0.0.3"

__author__ = "Da4ndo"
__discord__ = "Da4ndo#0934"
__youtube__ = "https://www.youtube.com/channel/UCdhZa-JISiqwd913nhB8cAw?"
__github__ = "https://github.com/Mesteri05"
__licence__ = "MIT"

# Imports for voice comm
import pyttsx3
import sys
import speech_recognition as sr
import importlib
from . import errors
from . import utils

class VoiceComm():
    def __init__(self, language="hu-HU", rate=140, volume=1.0, voice=1):
        self.engine = pyttsx3.init()
        
        self.language = language
        self.engine.setProperty('rate', rate) 

        """VOLUME"""
        volume = self.engine.getProperty('volume')
        self.engine.setProperty('volume', volume)

        """VOICE"""
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[voice].id)
        self.r = sr.Recognizer()

        self._commands = []
        self._loaded_modules = []
        self._threads = []

    def say(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def recognize(self, phrase_time_limit=None, timeout=None, snowboy_configuration=None):
        with sr.Microphone() as source:
            audio = self.r.listen(source, phrase_time_limit=phrase_time_limit, timeout=timeout, snowboy_configuration=snowboy_configuration)
        
        try:
            text = self.r.recognize_google(audio, language=self.language)
        except:
            text = None

        return text
    
    def recognize_command(self, text):
        text = text.lower()
        for data in self._commands:
            words = data["words"]
            function = data["func"]
            required_words = data["required_words"]
            or_required_words = data["or_required_words"]
            isrequired_words_in = []

            if data["is_capital_letters_matter"] == False:
                for rw in required_words:
                    if rw.lower() in text:
                        isrequired_words_in.append(True)
                    else:
                        isrequired_words_in.append(False)

                if isrequired_words_in.count(True) == len(required_words):
                    if or_required_words != []:
                        some_or_in = False
                        for or_word in or_required_words:
                            if or_word.lower() in text:
                                some_or_in = True
                                break
                        
                        if some_or_in == True:
                            for w in words:
                                if w.lower() in text:
                                    try:
                                        function(text)
                                    except TypeError:
                                        try:
                                            function()
                                        except Exception as e:
                                            raise e
                                    except Exception as e:
                                        raise e
                                    break
                    
                    else:

                        for w in words:
                            if w.lower() in text:
                                try:
                                    function(text)
                                except TypeError:
                                    try:
                                        function()
                                    except Exception as e:
                                        raise e
                                except Exception as e:
                                    raise e
                                break

            else:
                for rw in required_words:
                    if rw in text:
                        isrequired_words_in.append(True)
                    else:
                        isrequired_words_in.append(False)

                if isrequired_words_in.count(True) == len(required_words):
                    if or_required_words != []:
                        some_or_in = False
                        for or_word in or_required_words:
                            if or_word in text:
                                some_or_in = True
                                break
                        
                        if some_or_in == True:
                            for w in words:
                                if w in text:
                                    try:
                                        function(text)
                                    except TypeError:
                                        try:
                                            function()
                                        except Exception as e:
                                            raise e
                                    except Exception as e:
                                        raise e
                                    break
                    
                    else:

                        for w in words:
                            if w in text:
                                try:
                                    function(text)
                                except TypeError:
                                    try:
                                        function()
                                    except Exception as e:
                                        raise e
                                except Exception as e:
                                    raise e
                                break

    def add_command(self, is_capital_letters_matter:bool=False, words:list=[], or_required_words:list=[], required_words:list=[]):
        def decorator(func):
            for data in self._commands:
                if data["func"] == func:
                    return func
            self._commands.append({"words": words, "required_words": required_words, "or_required_words": or_required_words, "is_capital_letters_matter": is_capital_letters_matter, "func": func})
            return func

        return decorator
    
    def load_module(self, module):
        if module in self._loaded_modules:
            raise errors.ModuleAlreadyLoaded(module)

        spec = importlib.util.find_spec(module)
        if spec is None:
            raise errors.ModuleNotFound(module)
        
        self._load_from_module_spec(spec, module)
    
    @property
    def loaded_modules(self):
        return self._loaded_modules
    
    def stop_module(self, module):
        if module not in self._loaded_modules:
            raise errors.ModuleNotFound(module)

        mthread = self._threads[self._loaded_modules.index(module)]
        mthread.stop()

        self._threads.remove(mthread)
    
    def _load_from_module_spec(self, spec, key):

        lib = importlib.util.module_from_spec(spec)
        sys.modules[key] = lib

        try:
            spec.loader.exec_module(lib)
        except Exception as e:
            del sys.modules[key]
            raise errors.ModuleFailed(key, e)

        try:
            setup = getattr(lib, 'setup')
        except AttributeError as e:
            del sys.modules[key]
            raise e

        try:
            new_thread = utils.StoppableThread(target=setup, args=(self, ))
            new_thread.start()

            self._threads.append(new_thread)

        except Exception as e:
            del sys.modules[key]
            raise errors.ModuleFailed(key, e)
        
        self._loaded_modules.append(key)
    
    @property
    def get_commands(self):
        return self._commands