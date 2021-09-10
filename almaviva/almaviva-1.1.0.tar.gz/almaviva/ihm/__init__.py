# coding: utf-8

# 
# Dependences
# 
import wmi, socket

# 
# Manipulador para obter nome da máquina e usuário logado
# 
class HUNames():

    def __init__ (
        self
    ):
        self.set_hostname()
        self.set_username()
    
    # 
    # Métodos para obter nome da máquina
    # 
    def set_hostname (
        self
    ):
        self.hostname = socket.gethostname()

    def get_hostname (
        self
    ):
        return self.hostname

    # 
    # Métodos para obter nome do usuário windows atualmente conectado
    # 
    def set_username (
        self
    ):
        user = list()
        wmi_object = wmi.WMI (
            self.get_hostname()
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

    def get_username (
        self
    ):
        return self.username