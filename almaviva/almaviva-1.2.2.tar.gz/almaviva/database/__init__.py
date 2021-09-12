# coding: utf-8

# 
# Dependences
# 
import os, sys, traceback
import pyodbc
from almaviva.logging import Logging

# 
# Manipulador para conexão ao banco de dados
# 
class Database():
    
    def __init__ (
        self
    ,   server
    ,   database
    ,   username=None
    ,   password=None
    ,   driver=None
    ):

        self.log = Logging()
        self.set_debugging (
            activated=False
        )

        # set default DRIVER={ODBC Driver 13 for SQL Server} or private DRIVER={self.driver}
        if driver:
            self.set_driver (driver=driver)
        else:
            self.set_driver (driver='ODBC Driver 13 for SQL Server')

        self.set_server (server=server)
        self.set_database (database=database)
        self.set_username (username=username)
        self.set_password (password=password)

        # cursor init set
        self.cursor = list()

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
            ,   step='Database.set_debugging'
            )
        else:
            self.log.warn (
                description='Modo de depuração desabilitado'
            ,   step='Database.set_debugging'
            )

    # 
    # Set other driver
    # 
    def set_driver (
        self
    ,   driver
    ):
        self.driver = driver
        self.log.info (
            description='Driver configurado: ' + str (
                driver
            )
        ,   step='Database.set_driver'
        )

    # 
    # Set other server name
    # 
    def set_server (
        self
    ,   server
    ):
        self.server = server
        self.log.info (
            description='Servidor configurado: ' + str (
                server
            )
        ,   step='Database.set_server'
        )

    # 
    # Set other database name
    # 
    def set_database (
        self
    ,   database
    ):
        self.database = database
        self.log.info (
            description='Banco de dados configurado: ' + str (
                database
            )
        ,   step='Database.set_database'
        )

    # 
    # Set username name
    # 
    def set_username (
        self
    ,   username
    ):
        self.username = username
        self.log.info (
            description='Autenticação via username configurado'
        ,   step='Database.set_username'
        )

    # 
    # Set password name
    # 
    def set_password (
        self
    ,   password
    ):
        self.password = password
    
    #
    # Função para iniciar a conexão com banco de dados usando as informações da biblioteca 
    # 
    def connect (
        self
    ):
        
        try:
            if (self.username):
                self.log.info (
                    description='Iniciando conexão usando DRIVER=' + str(self.driver) + ';SERVER=' + str(self.server) + ';DATABASE=' + str(self.database) + ';Trusted_Connection=no'
                ,   step='Database.connect'
                )
                cnxn = pyodbc.connect ( \
                    'DRIVER={' + str(self.driver) + '};' \
                +   'SERVER=' + str(self.server) + ';' \
                +   'DATABASE=' + str(self.database) + ';' \
                +   'UID=' + str(self.username) + ';' \
                +   'PWD=' + str(self.password)
                )
            else:
                self.log.info (
                    description='Iniciando conexão usando DRIVER=' + str(self.driver) + ';SERVER=' + str(self.server) + ';DATABASE=' + str(self.database) + ';Trusted_Connection=yes'
                ,   step='Database.connect'
                )
                cnxn = pyodbc.connect ( \
                    'DRIVER={' + str(self.driver) + '};' \
                +   'SERVER=' + str(self.server) + ';' \
                +   'DATABASE=' + str(self.database) + ';' \
                +   'Trusted_Connection=yes'
                )   # add Trusted Connection

            self.cursor = cnxn.cursor()     # set cursor
            cnxn.autocommit = True
            self.log.info (
                description='Conectado'
            ,   step='Database.connect'
            )

            return True
        
        except Exception as ecp:
            self.log.error (
                description='Falhou'
            ,   step='Database.connect'
            )
            # return sys.exc_info()[0]      # alterado para permitir tratamento de falhas no código pai
            print (sys.exc_info())
            print (traceback.print_exc(file=sys.stdout))
            raise ecp
    
    #
    # SELECT
    # 
    def select (
        self
    ,   query
    ):
        
        try:
            self.cursor.execute(query)
            self.log.info (
                description='Ok > ' + str (
                    query
                )
            ,   step='Database.select'
            )
            return self.cursor.fetchall()

        except Exception as ecp:
            self.log.error (
                description='Falhou > ' + str (
                    query
                )
            ,   step='Database.select'
            )
            # return sys.exc_info()[0]      # alterado para permitir tratamento de falhas no código pai
            print (sys.exc_info())
            print (traceback.print_exc(file=sys.stdout))
            raise ecp

    #
    # INSERT
    # 
    def insert (
        self
    ,   query
    ):
        
        try:
            self.cursor.execute(query)
            self.log.info (
                description='Ok > ' + str (
                    query
                )
            ,   step='Database.insert'
            )
            return True

        except Exception as ecp:
            self.log.error (
                description='Falhou > ' + str (
                    query
                )
            ,   step='Database.insert'
            )
            # return sys.exc_info()[0]      # alterado para permitir tratamento de falhas no código pai
            print (sys.exc_info())
            print (traceback.print_exc(file=sys.stdout))
            raise ecp

    #
    # DELETE
    # 
    def delete (
        self
    ,   query
    ):
        
        try:
            self.cursor.execute(query)
            self.log.info (
                description='Ok > ' + str (
                    query
                )
            ,   step='Database.delete'
            )
            return True

        except Exception as ecp:
            self.log.error (
                description='Falhou > ' + str (
                    query
                )
            ,   step='Database.delete'
            )
            # return sys.exc_info()[0]      # alterado para permitir tratamento de falhas no código pai
            print (sys.exc_info())
            print (traceback.print_exc(file=sys.stdout))
            raise ecp

    #
    # UPDATE
    # 
    def update (
        self
    ,   query
    ):
        
        try:
            self.cursor.execute(query)
            self.log.info (
                description='Ok > ' + str (
                    query
                )
            ,   step='Database.update'
            )
            return True

        except Exception as ecp:
            self.log.error (
                description='Falhou > ' + str (
                    query
                )
            ,   step='Database.update'
            )
            # return sys.exc_info()[0]      # alterado para permitir tratamento de falhas no código pai
            print (sys.exc_info())
            print (traceback.print_exc(file=sys.stdout))
            raise ecp

    # 
    # STORED PROCEDURE
    # 
    def execute_sp (
        self
    ,   stored_procedure
    ,   param=None
    ):
        
        try:
            
            if (param):
                
                if not (type(param) == tuple):
                    
                    if (type(param) == str):
                        _param = '(\'' + str(param) + '\')'
                    
                    else:
                        _param = '(' + str(param) + ')'

                else:
                    _param = param      # fix issue
            
            else:

                # if (type(param) == int or type(param) == float):
                #     _param = '(' + str(param) + ')'
                # else:
                #     if (type(param) == str):
                #         _param = '(\'\')'
                #     else:
                #         _param = '()'
                _param = ''    # fix issue
            
            _query = '{call ' + str(stored_procedure) + str(_param) + '}'
            self.cursor.execute(_query)
            self.log.info (
                description='Ok > ' + str (
                    _query
                )
            ,   step='Database.execute_sp'
            )
        
        except Exception as ecp:
            self.log.error (
                description='Falhou > ' + str (
                    _query
                )
            ,   step='Database.execute_sp'
            )
            print (sys.exc_info())
            print (traceback.print_exc(file=sys.stdout))
            raise ecp