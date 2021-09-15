# coding: utf-8

# 
# Dependences
# 
import time
from almaviva.ihm import HUNames

# 
# Manipulador para registro do log
# 
class Logging():
    
    def __init__ (
        self
    ):
        
        self.set_options (
            logging_in_file=True
        ,   debug_in_terminal=False
        ,   logging_in_server=False
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
    ,   logging_in_file=True
    ,   debug_in_terminal=False
    ,   logging_in_server=False
    ):
        
        # 
        # Regitra a atividade do servidor em arquivos de log separados por dia
        # 
        if (
            logging_in_file==True
        ):
            self.logging_in_file = True
        else:
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
        # Regitra a atividade do servidor no banco de dados do Noc Central
        # 
        if (
            logging_in_server==True
        ):
            self.logging_in_server = True
        else:
            self.logging_in_server = None

    # 
    # Log do nível de segurança 'INFO' c/s registro em banco de dados
    # 
    def info (
        self
    ,   description
    ,   step=None
    ,   complete=True
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
        Tratamento do campo
        """
        switcher = {
            True:   'OK'
        ,   False:  'WAIT/PROCESS'
        }

        try:
            if (
                complete!=True
            ):
                complete=False
        
        except:
            complete=False
            pass

        """
        contexto do log para exibição no terminal.
        contém os campos: dhLocal, level, step, status, description
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
        +   switcher.get (
                complete
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
        +   switcher.get (
                complete
            ) \
        +   ':' \
        +   str (
                description
            ).replace (
                ':'
            ,   '.'
            )
        
        """
        Mostrar registro de log resumido no terminal, caso a opção __debug_in_terminal__ esteja habilitada
        """
        if (
            self.debug_in_terminal==True
        ):
            print (
                '> ' \
            +   log_in_terminal
            )

        """
        Verificar se a opção do registro do log em arquivo no sistema local foi habilitada
        """
        if (
            self.logging_in_file==True
        ):
            _try=1
            _try_counts=10
            while True:

                try:

                    """
                    Tentar registrar o log em arquivo no sistema local
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

                except FileNotFoundError:
                    _try+=1
                    if (
                        _try > _try_counts
                    ):
                        break
                
                except PermissionError:
                    _try+=1
                    if (
                        _try > _try_counts
                    ):
                        break
                    
                    time.sleep (1)
                    continue

                else:
                    break

        """
        Verificar se a opção do registro do log no servidor está habilitada
        """
        if (
            self.logging_in_server==True
        ):
            _try=1
            _try_counts=10
            while True:

                try:

                    """
                    Tentar enviar o registro do log para o servidor de LOGS
                    """
                    if self.server=='MG00BI02':
                        logfileurl='E:\\logfiles\\buffer.log'
                    else:
                        logfileurl='\\\\portalnoc\\logfiles$\\buffer.log'
                    with open (
                        file=logfileurl
                    ,   mode='a'
                    ,   encoding='utf8'
                    ) as fh:
                        readme = fh.write (
                            log_in_file + '\n'
                        )
                        fh.close()

                except FileNotFoundError:
                    _try+=1
                    if (
                        _try > _try_counts
                    ):
                        break
                
                except PermissionError:
                    _try+=1
                    if (
                        _try > _try_counts
                    ):
                        break
                    
                    time.sleep (1)
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
    ,   complete=True
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
        Tratamento do campo
        """
        switcher = {
            True:   'OK'
        ,   False:  'WAIT/PROCESS'
        }

        try:
            if (
                complete!=True
            ):
                complete=False
        
        except:
            complete=False
            pass

        """
        contexto do log para exibição no terminal.
        contém os campos: dhLocal, level, step, status, description
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
        +   switcher.get (
                complete
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
        +   switcher.get (
                complete
            ) \
        +   ':' \
        +   str (
                description
            ).replace (
                ':'
            ,   '.'
            )
        
        """
        Mostrar registro de log resumido no terminal, caso a opção __debug_in_terminal__ esteja habilitada
        """
        if (
            self.debug_in_terminal==True
        ):
            print (
                '> ' \
            +   log_in_terminal
            )

        """
        Verificar se a opção do registro do log em arquivo no sistema local foi habilitada
        """
        if (
            self.logging_in_file==True
        ):
            _try=1
            _try_counts=10
            while True:

                try:

                    """
                    Tentar registrar o log em arquivo no sistema local
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

                except FileNotFoundError:
                    _try+=1
                    if (
                        _try > _try_counts
                    ):
                        break
                
                except PermissionError:
                    _try+=1
                    if (
                        _try > _try_counts
                    ):
                        break
                    
                    time.sleep (1)
                    continue

                else:
                    break

        """
        Verificar se a opção do registro do log no servidor está habilitada
        """
        if (
            self.logging_in_server==True
        ):
            _try=1
            _try_counts=10
            while True:

                try:

                    """
                    Tentar enviar o registro do log para o servidor de LOGS
                    """
                    if self.server=='MG00BI02':
                        logfileurl='E:\\logfiles\\buffer.log'
                    else:
                        logfileurl='\\\\portalnoc\\logfiles$\\buffer.log'
                    with open (
                        file=logfileurl
                    ,   mode='a'
                    ,   encoding='utf8'
                    ) as fh:
                        readme = fh.write (
                            log_in_file + '\n'
                        )
                        fh.close()

                except FileNotFoundError:
                    _try+=1
                    if (
                        _try > _try_counts
                    ):
                        break
                
                except PermissionError:
                    _try+=1
                    if (
                        _try > _try_counts
                    ):
                        break
                    
                    time.sleep (1)
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
        Tratamento do campo
        """
        switcher = {
            True:   'OK'
        ,   False:  'WAIT/PROCESS'
        }
        complete=True       # Sempre CONCLUÍDO, porém com sinalização de erro
        
        """
        contexto do log para exibição no terminal.
        contém os campos: dhLocal, level, step, status, description
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
        +   switcher.get (
                complete
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
        +   switcher.get (
                complete
            ) \
        +   ':' \
        +   str (
                description
            ).replace (
                ':'
            ,   '.'
            )
        
        """
        Mostrar registro de log resumido no terminal, caso a opção __debug_in_terminal__ esteja habilitada
        """
        if (
            self.debug_in_terminal==True
        ):
            print (
                '> ' \
            +   log_in_terminal
            )

        """
        Verificar se a opção do registro do log em arquivo no sistema local foi habilitada
        """
        if (
            self.logging_in_file==True
        ):
            _try=1
            _try_counts=10
            while True:

                try:

                    """
                    Tentar registrar o log em arquivo no sistema local
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

                except FileNotFoundError:
                    _try+=1
                    if (
                        _try > _try_counts
                    ):
                        break
                
                except PermissionError:
                    _try+=1
                    if (
                        _try > _try_counts
                    ):
                        break
                    
                    time.sleep (1)
                    continue

                else:
                    break

        """
        Verificar se a opção do registro do log no servidor está habilitada
        """
        if (
            self.logging_in_server==True
        ):
            _try=1
            _try_counts=10
            while True:

                try:

                    """
                    Tentar enviar o registro do log para o servidor de LOGS
                    """
                    if self.server=='MG00BI02':
                        logfileurl='E:\\logfiles\\buffer.log'
                    else:
                        logfileurl='\\\\portalnoc\\logfiles$\\buffer.log'
                    with open (
                        file=logfileurl
                    ,   mode='a'
                    ,   encoding='utf8'
                    ) as fh:
                        readme = fh.write (
                            log_in_file + '\n'
                        )
                        fh.close()

                except FileNotFoundError:
                    _try+=1
                    if (
                        _try > _try_counts
                    ):
                        break
                
                except PermissionError:
                    _try+=1
                    if (
                        _try > _try_counts
                    ):
                        break
                    
                    time.sleep (1)
                    continue

                else:
                    break