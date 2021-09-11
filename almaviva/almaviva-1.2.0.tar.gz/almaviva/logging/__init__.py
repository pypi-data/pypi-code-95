# coding: utf-8

# 
# Dependences
# 
import time
from almaviva.ihm import HUNames    # fassad, 2021-09-11: adicionado na versão 1.2.0

# 
# Manipulador para registro do log
# 
class Logging():
    
    def __init__ (
        self
    ):
        
        self.set_options (
            # logging_in_db=None    # substituído na versão 1.2.0
            logging_in_file=True
        ,   debug_in_terminal=False
        )

        huname = HUNames()
        self.server = huname.get_hostname()
        self.user = huname.get_username()
        self.app = huname.get_app()

    #
    # Opções avançadas
    #
    def set_options (
        self
    # ,   logging_in_db=None    # substituído na versão 1.2.0
    ,   logging_in_file=True
    ,   debug_in_terminal=False
    ):
        
        # 
        # Regitra a atividade do servidor no banco de dados
        # 
        if (
            # logging_in_db   # informar a instância do objeto Database
            logging_in_file==True     # substituído na versão 1.2.0
        ):
            # self.logging_in_db = logging_in_db    # substituído na versão 1.2.0
            self.logging_in_file = True
        else:
            # self.logging_in_db = None     # substituído na versão 1.2.0
            self.logging_in_file = None
        
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
        mlsec = repr (
            now
        ).split (
            '.'
        )[1][:3]
        dateLocal = time.strftime (
            '%Y-%m-%d'
        ,   time.localtime (
                now
            )
        )
        dateUtc = time.strftime (
            '%Y-%m-%d'
        ,   time.gmtime()
        )
        timeLocal = time.strftime (
            '%H:%M:%S.{}'.format (
                mlsec
            )
        ,   time.localtime (
                now
            )
        )
        timeUtc = time.strftime (
            '%H:%M:%S.{}'.format (
                mlsec
            )
        ,   time.gmtime()
        )

        """
        contexto do log para exibição no terminal.
        contém os campos: dhLocal, level, step, description
        """
        log_in_terminal = \
            dateLocal \
        +   ' ' \
        +   timeLocal \
        +   ':' \
        +   'INFO' \
        +   ':' \
        +   str (
                step
            ).replace (
                ':'
            ,   '.'
            ) \
        +   ':' \
        +   str (
                description
            ).replace (
                ':'
            ,   '.'
            )

        """
        contexto do log para registro no arquivo.
        contém os campos: dhUtc, dhLocal, server, user, app, level, step, description
        """
        log_in_file = \
            dateUtc \
        +   ' ' \
        +   timeUtc \
        +   ':' \
        +   dateLocal \
        +   ' ' \
        +   timeLocal \
        +   ':' \
        +   str (
                self.server
            ).replace (
                ':'
            ,   '.'
            ) \
        +   ':' \
        +   str (
                self.user
            ).replace (
                ':'
            ,   '.'
            ) \
        +   ':' \
        +   str (
                self.app
            ).replace (
                ':'
            ,   '.'
            ) \
        +   ':' \
        +   'INFO' \
        +   ':' \
        +   str (
                step
            ).replace (
                ':'
            ,   '.'
            ) \
        +   ':' \
        +   str (
                description
            ).replace (
                ':'
            ,   '.'
            )

        """
        Verificar se a opção do registro do log em arquivo no sistema local foi habilitada
        """
        # if (self.logging_in_db):      # fassad, 2021-09-11: substituído na versão 1.2.0
        if (self.logging_in_file):
            
            """
            Mostrar registro de log resumido no terminal, caso a opção __debug_in_terminal__ esteja habilitada
            """
            if (self.debug_in_terminal==True):
                print ( \
                    '> '
                +   log_in_terminal \
                )

            _try=1
            _try_counts=10
            while True:

                try:

                    """
                    Registrar o log em arquivo no sistema local
                    """
                    with open (
                        file= \
                            dateLocal \
                        +   '.log'
                    ,   mode='a'
                    ,   encoding='utf8'
                    ) as fh:
                        readme = fh.write (
                            log_in_file + '\n'
                        )
                        fh.close()
                    
                    """
                    Tentar enviar o registro do log para o servidor de LOGS
                    """
                    # params = str(step), 'INFO', str(description)
                    # procedure = '[NocCentral].[dbo].[sp_ServersLogging]'
                    # param_tuple = (params)
                    # self.logging_in_db.execute_sp (
                    #     stored_procedure=procedure
                    # ,   param=param_tuple
                    # )     # fassad, 2021-09-11: substituído na versão 1.2.0
                    with open (
                        file='\\\\portalnoc\\logfiles$\\buffer.log'
                    ,   mode='a'
                    ,   encoding='utf8'
                    ) as fh:
                        readme = fh.write (
                            log_in_file + '\n'
                        )
                        fh.close()

                except FileNotFoundError as ecp:
                    # print (
                    #     sys.exc_info()
                    # )
                    # print (
                    #     traceback.print_exc (
                    #         file=sys.stdout
                    #     )
                    # )
                    break
                
                except PermissionError as ecp:
                    _try+=1
                    if (
                        _try > _try_counts
                    ):
                        raise ecp
                    
                    time.sleep (5)
                    continue

                else:
                    break

        # Desconsiderar o registro do log em arquivo no sistema local
        else:
            
            """
            Mostrar registro de log resumido no terminal, caso a opção __debug_in_terminal__ esteja habilitada
            """
            if (self.debug_in_terminal==True):
                print ( \
                    '> '
                +   log_in_terminal \
                )

            _try=1
            _try_counts=10
            while True:

                try:

                    """
                    Tentar enviar o registro do log para o servidor de LOGS
                    """
                    # params = str(step), 'INFO', str(description)
                    # procedure = '[NocCentral].[dbo].[sp_ServersLogging]'
                    # param_tuple = (params)
                    # self.logging_in_db.execute_sp (
                    #     stored_procedure=procedure
                    # ,   param=param_tuple
                    # )     # fassad, 2021-09-11: substituído na versão 1.2.0
                    with open (
                        file='\\\\portalnoc\\logfiles$\\buffer.log'
                    ,   mode='a'
                    ,   encoding='utf8'
                    ) as fh:
                        readme = fh.write (
                            log_in_file + '\n'
                        )
                        fh.close()

                except FileNotFoundError as ecp:
                    # print (
                    #     sys.exc_info()
                    # )
                    # print (
                    #     traceback.print_exc (
                    #         file=sys.stdout
                    #     )
                    # )
                    break
                
                except PermissionError as ecp:
                    _try+=1
                    if (
                        _try > _try_counts
                    ):
                        raise ecp
                    
                    time.sleep (5)
                    continue

                else:
                    break

    # 
    # Log do nível de segurança 'WARNING' c/s registro em banco de dados
    # 
    def warn (
        self
    ,   description
    ,   step=None
    ):
        now = time.time()
        mlsec = repr (
            now
        ).split (
            '.'
        )[1][:3]
        dateLocal = time.strftime (
            '%Y-%m-%d'
        ,   time.localtime (
                now
            )
        )
        dateUtc = time.strftime (
            '%Y-%m-%d'
        ,   time.gmtime()
        )
        timeLocal = time.strftime (
            '%H:%M:%S.{}'.format (
                mlsec
            )
        ,   time.localtime (
                now
            )
        )
        timeUtc = time.strftime (
            '%H:%M:%S.{}'.format (
                mlsec
            )
        ,   time.gmtime()
        )

        """
        contexto do log para exibição no terminal.
        contém os campos: dhLocal, level, step, description
        """
        log_in_terminal = \
            dateLocal \
        +   ' ' \
        +   timeLocal \
        +   ':' \
        +   'WARN' \
        +   ':' \
        +   str (
                step
            ).replace (
                ':'
            ,   '.'
            ) \
        +   ':' \
        +   str (
                description
            ).replace (
                ':'
            ,   '.'
            )

        """
        contexto do log para registro no arquivo.
        contém os campos: dhUtc, dhLocal, server, user, app, level, step, description
        """
        log_in_file = \
            dateUtc \
        +   ' ' \
        +   timeUtc \
        +   ':' \
        +   dateLocal \
        +   ' ' \
        +   timeLocal \
        +   ':' \
        +   str (
                self.server
            ).replace (
                ':'
            ,   '.'
            ) \
        +   ':' \
        +   str (
                self.user
            ).replace (
                ':'
            ,   '.'
            ) \
        +   ':' \
        +   str (
                self.app
            ).replace (
                ':'
            ,   '.'
            ) \
        +   ':' \
        +   'WARN' \
        +   ':' \
        +   str (
                step
            ).replace (
                ':'
            ,   '.'
            ) \
        +   ':' \
        +   str (
                description
            ).replace (
                ':'
            ,   '.'
            )

        """
        Verificar se a opção do registro do log em arquivo no sistema local foi habilitada
        """
        # if (self.logging_in_db):      # fassad, 2021-09-11: substituído na versão 1.2.0
        if (self.logging_in_file):
            
            """
            Mostrar registro de log resumido no terminal, caso a opção __debug_in_terminal__ esteja habilitada
            """
            if (self.debug_in_terminal==True):
                print ( \
                    '> '
                +   log_in_terminal \
                )

            _try=1
            _try_counts=10
            while True:

                try:

                    """
                    Registrar o log em arquivo no sistema local
                    """
                    with open (
                        file= \
                            dateLocal \
                        +   '.log'
                    ,   mode='a'
                    ,   encoding='utf8'
                    ) as fh:
                        readme = fh.write (
                            log_in_file + '\n'
                        )
                        fh.close()
                    
                    """
                    Tentar enviar o registro do log para o servidor de LOGS
                    """
                    # params = str(step), 'WARN', str(description)
                    # procedure = '[NocCentral].[dbo].[sp_ServersLogging]'
                    # param_tuple = (params)
                    # self.logging_in_db.execute_sp (
                    #     stored_procedure=procedure
                    # ,   param=param_tuple
                    # )     # fassad, 2021-09-11: substituído na versão 1.2.0
                    with open (
                        file='\\\\portalnoc\\logfiles$\\buffer.log'
                    ,   mode='a'
                    ,   encoding='utf8'
                    ) as fh:
                        readme = fh.write (
                            log_in_file + '\n'
                        )
                        fh.close()

                except FileNotFoundError as ecp:
                    # print (
                    #     sys.exc_info()
                    # )
                    # print (
                    #     traceback.print_exc (
                    #         file=sys.stdout
                    #     )
                    # )
                    break
                
                except PermissionError as ecp:
                    _try+=1
                    if (
                        _try > _try_counts
                    ):
                        raise ecp
                    
                    time.sleep (5)
                    continue

                else:
                    break

        # Desconsiderar o registro do log em arquivo no sistema local
        else:
            
            """
            Mostrar registro de log resumido no terminal, caso a opção __debug_in_terminal__ esteja habilitada
            """
            if (self.debug_in_terminal==True):
                print ( \
                    '> '
                +   log_in_terminal \
                )

            _try=1
            _try_counts=10
            while True:

                try:

                    """
                    Tentar enviar o registro do log para o servidor de LOGS
                    """
                    # params = str(step), 'WARN', str(description)
                    # procedure = '[NocCentral].[dbo].[sp_ServersLogging]'
                    # param_tuple = (params)
                    # self.logging_in_db.execute_sp (
                    #     stored_procedure=procedure
                    # ,   param=param_tuple
                    # )     # fassad, 2021-09-11: substituído na versão 1.2.0
                    with open (
                        file='\\\\portalnoc\\logfiles$\\buffer.log'
                    ,   mode='a'
                    ,   encoding='utf8'
                    ) as fh:
                        readme = fh.write (
                            log_in_file + '\n'
                        )
                        fh.close()

                except FileNotFoundError as ecp:
                    # print (
                    #     sys.exc_info()
                    # )
                    # print (
                    #     traceback.print_exc (
                    #         file=sys.stdout
                    #     )
                    # )
                    break
                
                except PermissionError as ecp:
                    _try+=1
                    if (
                        _try > _try_counts
                    ):
                        raise ecp
                    
                    time.sleep (5)
                    continue

                else:
                    break
    

    # 
    # Log do nível de segurança 'ERROR' c/s registro em banco de dados
    # 
    def error (
        self
    ,   description
    ,   step=None
    ):
        now = time.time()
        mlsec = repr (
            now
        ).split (
            '.'
        )[1][:3]
        dateLocal = time.strftime (
            '%Y-%m-%d'
        ,   time.localtime (
                now
            )
        )
        dateUtc = time.strftime (
            '%Y-%m-%d'
        ,   time.gmtime()
        )
        timeLocal = time.strftime (
            '%H:%M:%S.{}'.format (
                mlsec
            )
        ,   time.localtime (
                now
            )
        )
        timeUtc = time.strftime (
            '%H:%M:%S.{}'.format (
                mlsec
            )
        ,   time.gmtime()
        )

        """
        contexto do log para exibição no terminal.
        contém os campos: dhLocal, level, step, description
        """
        log_in_terminal = \
            dateLocal \
        +   ' ' \
        +   timeLocal \
        +   ':' \
        +   'ERROR' \
        +   ':' \
        +   str (
                step
            ).replace (
                ':'
            ,   '.'
            ) \
        +   ':' \
        +   str (
                description
            ).replace (
                ':'
            ,   '.'
            )

        """
        contexto do log para registro no arquivo.
        contém os campos: dhUtc, dhLocal, server, user, app, level, step, description
        """
        log_in_file = \
            dateUtc \
        +   ' ' \
        +   timeUtc \
        +   ':' \
        +   dateLocal \
        +   ' ' \
        +   timeLocal \
        +   ':' \
        +   str (
                self.server
            ).replace (
                ':'
            ,   '.'
            ) \
        +   ':' \
        +   str (
                self.user
            ).replace (
                ':'
            ,   '.'
            ) \
        +   ':' \
        +   str (
                self.app
            ).replace (
                ':'
            ,   '.'
            ) \
        +   ':' \
        +   'ERROR' \
        +   ':' \
        +   str (
                step
            ).replace (
                ':'
            ,   '.'
            ) \
        +   ':' \
        +   str (
                description
            ).replace (
                ':'
            ,   '.'
            )

        """
        Verificar se a opção do registro do log em arquivo no sistema local foi habilitada
        """
        # if (self.logging_in_db):      # fassad, 2021-09-11: substituído na versão 1.2.0
        if (self.logging_in_file):
            
            """
            Mostrar registro de log resumido no terminal, caso a opção __debug_in_terminal__ esteja habilitada
            """
            if (self.debug_in_terminal==True):
                print ( \
                    '> '
                +   log_in_terminal \
                )

            _try=1
            _try_counts=10
            while True:

                try:

                    """
                    Registrar o log em arquivo no sistema local
                    """
                    with open (
                        file= \
                            dateLocal \
                        +   '.log'
                    ,   mode='a'
                    ,   encoding='utf8'
                    ) as fh:
                        readme = fh.write (
                            log_in_file + '\n'
                        )
                        fh.close()
                    
                    """
                    Tentar enviar o registro do log para o servidor de LOGS
                    """
                    # params = str(step), 'ERROR', str(description)
                    # procedure = '[NocCentral].[dbo].[sp_ServersLogging]'
                    # param_tuple = (params)
                    # self.logging_in_db.execute_sp (
                    #     stored_procedure=procedure
                    # ,   param=param_tuple
                    # )     # fassad, 2021-09-11: substituído na versão 1.2.0
                    with open (
                        file='\\\\portalnoc\\logfiles$\\buffer.log'
                    ,   mode='a'
                    ,   encoding='utf8'
                    ) as fh:
                        readme = fh.write (
                            log_in_file + '\n'
                        )
                        fh.close()

                except FileNotFoundError as ecp:
                    # print (
                    #     sys.exc_info()
                    # )
                    # print (
                    #     traceback.print_exc (
                    #         file=sys.stdout
                    #     )
                    # )
                    break
                
                except PermissionError as ecp:
                    _try+=1
                    if (
                        _try > _try_counts
                    ):
                        raise ecp
                    
                    time.sleep (5)
                    continue

                else:
                    break

        # Desconsiderar o registro do log em arquivo no sistema local
        else:
            
            """
            Mostrar registro de log resumido no terminal, caso a opção __debug_in_terminal__ esteja habilitada
            """
            if (self.debug_in_terminal==True):
                print ( \
                    '> '
                +   log_in_terminal \
                )

            _try=1
            _try_counts=10
            while True:

                try:

                    """
                    Tentar enviar o registro do log para o servidor de LOGS
                    """
                    # params = str(step), 'ERROR', str(description)
                    # procedure = '[NocCentral].[dbo].[sp_ServersLogging]'
                    # param_tuple = (params)
                    # self.logging_in_db.execute_sp (
                    #     stored_procedure=procedure
                    # ,   param=param_tuple
                    # )     # fassad, 2021-09-11: substituído na versão 1.2.0
                    with open (
                        file='\\\\portalnoc\\logfiles$\\buffer.log'
                    ,   mode='a'
                    ,   encoding='utf8'
                    ) as fh:
                        readme = fh.write (
                            log_in_file + '\n'
                        )
                        fh.close()

                except FileNotFoundError as ecp:
                    # print (
                    #     sys.exc_info()
                    # )
                    # print (
                    #     traceback.print_exc (
                    #         file=sys.stdout
                    #     )
                    # )
                    break
                
                except PermissionError as ecp:
                    _try+=1
                    if (
                        _try > _try_counts
                    ):
                        raise ecp
                    
                    time.sleep (5)
                    continue

                else:
                    break