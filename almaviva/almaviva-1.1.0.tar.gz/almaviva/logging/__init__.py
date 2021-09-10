# coding: utf-8

# 
# Dependences
# 
import time

# 
# Manipulador para registro do log
# 
class Logging():
    
    def __init__ (
        self
    ):
        self.set_options (
            logging_in_db=None
        ,   debug_in_terminal=False
        )

    #
    # Opções avançadas
    #
    def set_options (
        self
    ,   logging_in_db=None
    ,   debug_in_terminal=False
    ):
        
        # 
        # Regitra a atividade do servidor no banco de dados
        # 
        if (
            logging_in_db   # informar a instância do objeto Database
        ):
            self.logging_in_db = logging_in_db
        else:
            self.logging_in_db = None
        
        #
        # Caso esteja habilitado, mostrará todos os registros no terminal a partir do nível de segurança 'INFO' até 'ERROR'
        # Case esteja desabilitado, exibirá apenas os registros a partir do nível 'WARNING' até 'ERROR', no terminal.
        # Esta opção não altera o modo de gravação dos registros no banco de dados
        #
        if (
            debug_in_terminal==True
        ):
            self.debug_in_terminal = True
        else:
            self.debug_in_terminal = None

    # 
    # Log do nível de segurança 'INFO' c/s registro em banco de dados
    # 
    def info (
        self
    ,   description
    ,   step=None
    ):
        now = time.time()
        mlsec = repr(now).split('.')[1][:3]
        timestamp = time.strftime (
            '%Y%m%d%H%M%S{}'.format(mlsec)
        ,   time.localtime(now)
        )

        if (self.logging_in_db):
            if (step):
                if (self.debug_in_terminal==True):
                    print ( \
                        '> '
                    +   str(step) \
                    +   ':' \
                    +   'INFO' \
                    +   ':' \
                    +   str(timestamp) \
                    +   ':' + \
                        str(description) \
                    )
                params = str(step), 'INFO', str(description)
                procedure = '[NocCentral].[dbo].[sp_ServersLogging]'
                param_tuple = (params)
                self.logging_in_db.execute_sp (
                    stored_procedure=procedure
                ,   param=param_tuple
                )
            else:
                if (self.debug_in_terminal==True):
                    print ( \
                        '> '
                    +   'INFO' \
                    +   ':' \
                    +   str(timestamp) \
                    +   ':' + \
                        str(description) \
                    )
                params = '', 'INFO', str(description)
                procedure = '[NocCentral].[dbo].[sp_ServersLogging]'
                param_tuple = (params)
                self.logging_in_db.execute_sp (
                    stored_procedure=procedure
                ,   param=param_tuple
                )
        else:
            if (step):
                if (self.debug_in_terminal==True):
                    print ( \
                        '> '
                    +   str(step) \
                    +   ':' \
                    +   'INFO' \
                    +   ':' \
                    +   str(timestamp) \
                    +   ':' + \
                        str(description) \
                    )
            else:
                if (self.debug_in_terminal==True):
                    print ( \
                        '> '
                    +   'INFO' \
                    +   ':' \
                    +   str(timestamp) \
                    +   ':' + \
                        str(description) \
                    )

    # 
    # Log do nível de segurança 'WARNING' c/s registro em banco de dados
    # 
    def warn (
        self
    ,   description
    ,   step=None
    ):
        now = time.time()
        mlsec = repr(now).split('.')[1][:3]
        timestamp = time.strftime (
            '%Y%m%d%H%M%S{}'.format(mlsec)
        ,   time.localtime(now)
        )

        if (self.logging_in_db):
            if (step):
                print ( \
                    '> '
                +   str(step) \
                +   ':' \
                +   'WARN' \
                +   ':' \
                +   str(timestamp) \
                +   ':' + \
                    str(description) \
                )
                params = str(step), 'WARN', str(description)
                procedure = '[NocCentral].[dbo].[sp_ServersLogging]'
                param_tuple = (params)
                self.logging_in_db.execute_sp (
                    stored_procedure=procedure
                ,   param=param_tuple
                )
            else:
                print ( \
                    '> '
                +   'WARN' \
                +   ':' \
                +   str(timestamp) \
                +   ':' + \
                    str(description) \
                )
                params = '', 'WARN', str(description)
                procedure = '[NocCentral].[dbo].[sp_ServersLogging]'
                param_tuple = (params)
                self.logging_in_db.execute_sp (
                    stored_procedure=procedure
                ,   param=param_tuple
                )
        else:
            if (step):
                print ( \
                    '> '
                +   str(step) \
                +   ':' \
                +   'WARN' \
                +   ':' \
                +   str(timestamp) \
                +   ':' + \
                    str(description) \
                )
            else:
                print ( \
                    '> '
                +   'WARN' \
                +   ':' \
                +   str(timestamp) \
                +   ':' + \
                    str(description) \
                )

    # 
    # Log do nível de segurança 'ERROR' c/s registro em banco de dados
    # 
    def error (
        self
    ,   description
    ,   step=None
    ):
        now = time.time()
        mlsec = repr(now).split('.')[1][:3]
        timestamp = time.strftime (
            '%Y%m%d%H%M%S{}'.format(mlsec)
        ,   time.localtime(now)
        )

        if (self.logging_in_db):
            if (step):
                print ( \
                    '> '
                +   str(step) \
                +   ':' \
                +   'ERROR' \
                +   ':' \
                +   str(timestamp) \
                +   ':' + \
                    str(description) \
                )
                params = str(step), 'ERROR', str(description)
                procedure = '[NocCentral].[dbo].[sp_ServersLogging]'
                param_tuple = (params)
                self.logging_in_db.execute_sp (
                    stored_procedure=procedure
                ,   param=param_tuple
                )
            else:
                print ( \
                    '> '
                +   'ERROR' \
                +   ':' \
                +   str(timestamp) \
                +   ':' + \
                    str(description) \
                )
                params = '', 'ERROR', str(description)
                procedure = '[NocCentral].[dbo].[sp_ServersLogging]'
                param_tuple = (params)
                self.logging_in_db.execute_sp (
                    stored_procedure=procedure
                ,   param=param_tuple
                )
        else:
            if (step):
                print ( \
                    '> '
                +   str(step) \
                +   ':' \
                +   'ERROR' \
                +   ':' \
                +   str(timestamp) \
                +   ':' + \
                    str(description) \
                )
            else:
                print ( \
                    '> '
                +   'ERROR' \
                +   ':' \
                +   str(timestamp) \
                +   ':' + \
                    str(description) \
                )