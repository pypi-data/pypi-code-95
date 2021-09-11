# coding: utf-8

# 
# Dependences
# 
import wmi, socket, sys

# 
# Manipulador para obter nome da máquina e usuário logado
# 
class HUNames():

    def __init__ (
        self
    ):
        self.set_hostname()
        self.set_username()
        self.set_app()
    
    # 
    # obter nome da máquina
    # 
    def set_hostname (
        self
    ):
        try:
            
            try:
                self.hostname = socket.gethostname()
            
            except:
                self.hostname = socket.gethostbyname (
                    socket.gethostname()
                )
                pass
        
        except:
            self.hostname = 'N/D'
            pass

    def get_hostname (
        self
    ):
        return self.hostname

    # 
    # obter nome do usuário windows atualmente conectado
    # 
    def set_username (
        self
    ):
        try:
            user = list()
            wmi_object = wmi.WMI (
                self.hostname
            )
            user = wmi_object.Win32_LogonSession()[0].references (
                'Win32_LoggedOnUser'
            )
            if str (
                user[0].Antecedent.Name
            ) == 'SISTEMA':
                self.username = 'Administrador'
            else:
                self.username = str (
                    user[0].Antecedent.Name
                )
        
        except:
            self.username = 'N/D'
            pass

    def get_username (
        self
    ):
        return self.username

    # 
    # Obter a versão do Python instalado no sistema
    # 
    def set_app (
        self
    ):
        try:
            self.app_version = \
            'Python {}.{}'.format (
                sys.version_info.major
            ,   sys.version_info.minor
            )

        except:
            self.app_version = 'N/D'

    def get_app (
        self
    ):
        return self.app_version