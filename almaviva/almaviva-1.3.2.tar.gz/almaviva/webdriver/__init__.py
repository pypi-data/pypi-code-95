# coding: utf-8

#
# Dependences
# 
import sys, traceback
import time
from datetime import datetime
import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from almaviva.logging import Logging
# import os     # fassad, 2021-08-28: removido
# from selenium.webdriver.common.keys import Keys   # fassad, 2021-08-29: removido
# from _library.filetemp import TempFiles   # fassad, 2021-08-29: removido
# from _library.debug import Debug   # fassad, 2021-08-28: removido

#
# Manipulador webdriver selenium
# 
class WebDriverChrome():

    def __init__ (
        self
    ,   debug=None      # removido
    ,   profile_location=None
    ,   executable_path='chromedriver'
    ):
        
        self.log = Logging()
        self.set_debugging (
            activated=False
        )

        # self.debug = debug   # fassad, 2021-08-28: removido
        self.executable_path = executable_path      # Chromium Driver
        self.options = webdriver.ChromeOptions()    # Importação das configurações do navegador

        if profile_location:
            # self.debug.logSQL ('inicialização do webdriver usando perfil da pasta {' + str(profile_location) + '}', str(__name__))   # fassad, 2021-08-28: removido
            # print (
            #     '> [WebDriverChrome.__init__]: ' + \
            #     'inicialização do webdriver usando perfil da pasta {' + str(profile_location) + '}'
            # )     # removido
            self.log.info (
                description='Executando navegador Google Chrome usando perfil localizado na pasta ' + str (
                    profile_location
                )
            ,   step='WebDriverChrome.__init__'
            )
            self.set_options('user-data-dir=' + str(profile_location))
        else:
            # self.debug.logSQL ('inicialização do webdriver usando perfil temporário padrão', str(__name__))   # fassad, 2021-08-28: removido
            # print (
            #     '> [WebDriverChrome.__init__]: ' + \
            #     'inicialização do webdriver usando perfil temporário padrão'
            # )     # removido
            self.log.warn (
                description='Executando navegador Google Chrome usando perfil temporário'
            ,   step='WebDriverChrome.__init__'
            )

    # 
    # Set debug-in-code
    # 
    def set_debugging (
        self
    ,   activated=False
    ):
        if (activated==True):
            self.debug = True
        else:
            self.debug = False

        self.log.set_options (
            debug_in_terminal=self.debug
        )

        if (self.debug==True):
            self.log.info (
                description='Modo de depuração habilitado'
            ,   step='WebDriverChrome.set_debugging'
            )
        else:
            self.log.warn (
                description='Modo de depuração desabilitado'
            ,   step='WebDriverChrome.set_debugging'
            )
            
    def set_options (
        self
    ,   new_argument
    ):
        self.options.add_argument (
            str (
                new_argument
            )
        )
        self.log.info (
            description='Opção \'' + str (
                new_argument
            ) + '\' foi adicionada nas configuraões do navegador'
        ,   step='WebDriverChrome.set_options'
        )

    def add_experimental_option (
        self
    ,   prefs=None
    ,   excludeSwitches=None
    ):
        if prefs:
            self.options.add_experimental_option (
                "prefs"
            ,   prefs
            )
            self.log.info (
                description='Opçõ(es) ' + str (
                    prefs
                ) + ' adicionad(as) nas configuraões do navegador'
            ,   step='WebDriverChrome.add_experimental_option'
            )
        if excludeSwitches:
            self.options.add_experimental_option (
                'excludeSwitches'
            ,   excludeSwitches
            )   # fassad, 2021-08-28: remove hardware error detection
            self.log.info (
                description='Opção [' + str (
                    excludeSwitches
                ) + '] adicionada nas configuraões do navegador'
            ,   step='WebDriverChrome.add_experimental_option'
            )
    
    # fassad, 2020-06-09: removido
    # def set_url (
    #     self
    # ,   url
    # ):
    #     self.url = str (
    #         url
    #     )

    def set_browser (
        self
    ,   url=None
    ):
        
        if 'browser' in dir (
            self
        ):
            if (url):
                # self.debug.logSQL ('abrindo página web {' + url + '}', str(__name__))   # fassad, 2021-08-28: removido
                # print (
                #     '> [WebDriverChrome.set_browser]: ' + \
                #     'processando: ' + url
                # )     # removido
                self.log.info (
                    description='Processando URL ' + str (
                        url
                    )
                ,   step='WebDriverChrome.set_browser'
                )
                self.browser.get (
                    url
                )
            else:
                # self.debug.logSQL ('abrindo nova página', str(__name__))   # fassad, 2021-08-28: removido
                # print (
                #     '> [WebDriverChrome.set_browser]: ' + \
                #     'processando'
                # )     # removido
                self.log.warn (
                    description='Navegador está em execução sem nenhuma URL definida'
                ,   step='WebDriverChrome.set_browser'
                )
                self.browser = webdriver.Chrome (
                    executable_path=self.executable_path
                ,   chrome_options=self.options
                )
                

        else:
            if (url):
                # self.debug.logSQL ('inicialização do navegador e processamento da página {' + url + '}', str(__name__))   # fassad, 2021-08-28: removido
                # print (
                #     '> [WebDriverChrome.set_browser]: ' + \
                #     'processando: ' + url
                # )     # removido
                self.log.info (
                    description='Processando URL ' + str (
                        url
                    )
                ,   step='WebDriverChrome.set_browser'
                )
                self.browser = webdriver.Chrome (
                    executable_path=self.executable_path
                ,   chrome_options=self.options
                )
                self.browser.get (
                    url
                )
            else:
                # self.debug.logSQL ('inicialização do navegador', str(__name__))   # fassad, 2021-08-28: removido
                # print (
                #     '> [WebDriverChrome.set_browser]: ' + \
                #     'processando'
                # )     # removido
                self.log.warn (
                    description='Navegador está em execução sem nenhuma URL definida'
                ,   step='WebDriverChrome.set_browser'
                )
                self.browser = webdriver.Chrome (
                    executable_path=self.executable_path
                ,   chrome_options=self.options
                )
        
        return self.browser

# 
# Manupulador para rescrita das funções find_element* selenium adicionando método em loop para otimizar run time
# 
class Browser (
    webdriver.Chrome
):

    def __init__ (
        self
    ,   debug=None  # # fassad, 2021-08-28: removido
    ,   browser=WebDriverChrome.set_browser
    ,   timeout=30
    ,   poll_frequency=1
    ):

        self.log = Logging()
        self.set_debugging (
            activated=False
        )

        # self.debug = debug   # fassad, 2021-08-28: removido
        self._browser = browser
        self._timeout = timeout
        self._poll = poll_frequency
    
    # 
    # Set debug-in-code
    # 
    def set_debugging (
        self
    ,   activated=False
    ):
        if (activated==True):
            self.debug = True
        else:
            self.debug = False

        self.log.set_options (
            debug_in_terminal=self.debug
        )

        if (self.debug==True):
            self.log.info (
                description='Modo de depuração habilitado'
            ,   step='Browser.set_debugging'
            )
        else:
            self.log.warn (
                description='Modo de depuração desabilitado'
            ,   step='Browser.set_debugging'
            )
    
    def quit (
        self
    ):
        self._browser.quit()
        # print (
        #     '> [Browser.quit]: ' + \
        #     'Ok'
        # )     # removido
        self.log.info (
            description='A aplicação web foi finalizada'
        ,   step='Browser.quit'
        )


    def refresh (
        self
    ):
        self._browser.refresh()
        # print (
        #     '> [Browser.refresh]: ' + \
        #     'Ok'
        # )     # removido
        self.log.info (
            description='A página web foi atualizada'
        ,   step='Browser.refresh'
        )

    def current_url (
        self
    ):
        self._browser.refresh()
        # print (
        #     '> [Browser.current_url]: ' + \
        #     self._browser.current_url
        # )     # removido
        self.log.info (
            description=str (
                self._browser.current_url
            )
        ,   step='Browser.current_url'
        )
        return self._browser.current_url

    def switchTo (
        self
    ,   tab=0
    ):
        # print (
        #     '> [Browser.switchTo]: ' + \
        #     self._browser.window_handles[tab]
        # )     # removido
        self.log.info (
            description='Alternando para guia nro. ' + str (
                tab
            ) + ' do navegador'
        ,   step='Browser.switchTo'
        )
        self._browser.switch_to.window (
            self._browser.window_handles [
                tab
            ]
        )

    def closeTab (
        self
    ,   tab=0
    ):
        self.switchTo (
            tab=tab
        )
        # print (
        #     '> [Browser.closeTab]: ' + \
        #     self._browser.window_handles [
        #         tab
        #     ]
        # )     # removido
        self.log.info (
            description='A guia nro. ' + str (
                tab
            ) + ' do navegador foi encerrado'
        ,   step='Browser.closeTab'
        )
        self._browser.close()

    # 
    # Esta função está desatualizada, em breve será removida. Utilize a função 'find_element()'
    # 
    def find_element_by_xpath (
        self
    ,   value
    ,   timeout=None
    ):

        
        try:
            
            # self.debug.logSQL ('localizar elemento da página usando { locate=xpath; value=' + str(value) + ' }', str(__name__))   # fassad, 2021-08-28: removido
            # print (
            #     '> [Browser.find_element_by_xpath]: ' + \
            #     'aguardando elemento web -> ' + str(value)
            # )     # remvido
            self.log.info (
                description='localizando XPATH > ' + str (
                    value
                )
            ,   step='Browser.find_element_by_xpath'
            )

            if (timeout):
                return WebDriverWait (
                    driver=value
                ,   timeout=timeout
                ,   poll_frequency=self._poll
                ).until (
                    method=self._browser.find_element_by_xpath
                )
            else:
                return WebDriverWait (
                    driver=value
                ,   timeout=self._timeout
                ,   poll_frequency=self._poll
                ).until (
                    method=self._browser.find_element_by_xpath
                )
            
        except Exception as ecp:
            # self.debug.logSQL ( \
            #     '! ' + str(sys.exc_info()[0]).replace('\'', '') + ' o processo para localizar o elemento da página usando { locate=xpath; value=' + str(value) + ' } falhou. o robo retornou ao processo anterior para evitar a interrupção do programa', \
            #     str(__name__) \
            # )   # fassad, 2021-08-28: removido
            # print (
            #     '> [Browser.find_element_by_xpath]: ' + \
            #     'Falhou -> ' + str(value)
            # )     # removido
            self.log.error (
                description='Falha ao localizar XPATH > ' + str (
                    value
                )
            ,   step='Browser.find_element_by_xpath'
            )
            print (
                sys.exc_info()
            )
            print (
                traceback.print_exc (
                    file=sys.stdout
                )
            )
            raise ecp

    def find_element (
        self
    ,   by=By
    ,   values=list
    ,   timeout=None
    ):

        # BY_CHOISES = {
        #     By.ID = "id"
        #     By.XPATH = "xpath"
        #     By.LINK_TEXT = "link text"
        #     By.PARTIAL_LINK_TEXT = "partial link text"
        #     By.NAME = "name"
        #     By.TAG_NAME = "tag name"
        #     By.CLASS_NAME = "class name"
        #     By.CSS_SELECTOR = "css selector"
        # }

        # self.debug.logSQL ('localizar elemento da página usando { locate=' + str(by) + '; values=' + str(values) + ' }', str(__name__))   # fassad, 2021-08-28: removido
        # print (
        #     '> [Browser.find_element]: ' + \
        #     'aguardando elemento web -> ' + str (
        #         values
        #     )
        # )     # removido
        self.log.info (
            description='Localizando ' + str (
                by
            ) + ' > ' + str (
                values
            )
        ,   step='Browser.find_element'
        )

        init_time = int (
            datetime.now().strftime (
                "%S"
            )
        )
        if timeout:
            end_time = init_time + timeout
        else:
            end_time = init_time + self._timeout
        poll_time = init_time
        
        while True:
            try:
                
                find = False
                for value in values:
                    try:
                        find = self._browser.find_element (
                            by=by
                        ,   value=value
                        ).is_displayed()
                    
                    except selenium.common.exceptions.NoSuchElementException:
                        continue
                    
                    except:
                        # print (
                        #     sys.exc_info()
                        # )
                        # print (
                        #     traceback.print_exc (
                        #         file=sys.stdout
                        #     )
                        # )     # removido
                        break
                    
                    else:
                        break
                
                if not find:
                    raise selenium.common.exceptions.NoSuchElementException
            
            except selenium.common.exceptions.NoSuchElementException:
                
                if poll_time < end_time:
                    poll_time = poll_time + self._poll
                    time.sleep (
                        self._poll
                    )
                    continue

                else:
                    # print (
                    #     '> [Browser.find_element]: ' + \
                    #     'Não encontrado -> ' + str (
                    #         values
                    #     )
                    # )     # removido
                    self.log.error (
                        description='Falhou ao localizar ' + str (
                            by
                        ) + ' > ' + str (
                            values
                        )
                    ,   step='Browser.find_element'
                    )
                    raise selenium.common.exceptions.TimeoutException
            
            except Exception as ecp:
                # self.debug.logSQL ( \
                #     '! ' + str(sys.exc_info()[0]).replace('\'', '') + ' o processo para localizar o elemento da página usando { locate=' + str(by) + '; value=' + str(value) + ' } falhou. o robo retornou ao processo anterior para evitar a interrupção do programa', \
                #     str(__name__) \
                # )   # fassad, 2021-08-28: removido
                # print (
                #     '> [Browser.find_element]: ' + \
                #     'Falhou -> ' + str (
                #         values
                #     )
                # )     # removido
                self.log.error (
                    description='Falhou ao localizar ' + str (
                        by
                    ) + ' > ' + str (
                        values
                    )
                ,   step='Browser.find_element'
                )
                print (
                    sys.exc_info()
                )
                print (
                    traceback.print_exc (
                        file=sys.stdout
                    )
                )
                raise ecp

            else:
                break
        
        self.log.info (
            description='Localizado ' + str (
                by
            ) + ' > ' + str (
                values
            )
        ,   step='Browser.find_element'
        )
        return self._browser.find_element (
            by=by
        ,   value=value
        )