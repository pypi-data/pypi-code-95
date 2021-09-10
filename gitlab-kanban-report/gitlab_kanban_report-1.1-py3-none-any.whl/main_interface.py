import os
import PySimpleGUI as sg
from gitlab_kaban_report.api_interface import APIInterface
from gitlab_kaban_report.constants import HERE


class GitLabKabanUi:
    def __init__(self):
        sg.theme('DarkAmber')
        layout = [
            [sg.Text('Id do projeto: '), sg.Input(key="project_id")],
            [sg.Text('Gitlab Token: '), sg.Input(key="token")],
            [sg.Button('Pesquisar projeto')],
            [sg.Output(size=(60,10))],
            [sg.Text('Escolha o projeto que quer fazer o relatório: ', visible=False, key="1"), sg.Input(key='board_id', visible=False)],
            [sg.Text('Escolha que pessoa quer filtrar: ', visible=False, key="2"), sg.Input(key='person_id', visible=False)],
            [sg.Text('Data com o formato YYYY-MM-DD', visible=False, key="3")],
            [sg.Text('Data de inicio: ', visible=False, key="4"), sg.Input(key='date_ini', visible=False)],
            [sg.Text('Data de final: ', visible=False, key="5"), sg.Input(key='date_end', visible=False)],
            [sg.Text("Path para salvar relatório: ", visible=False, key="6"), sg.FolderBrowse(key="path")],
            [sg.Button('Criar')]
        ]
        if os.path.isfile(os.path.join(HERE, "TOKEN")):
            layout = [
                [sg.Text('Id do projeto: '), sg.Input(key="project_id")],
                [sg.Text('Gitlab Token: ', visible=False), sg.Input(key="token", visible=False)],
                [sg.Button('Pesquisar projeto')],
                [sg.Output(size=(60,10))],
                [sg.Text('Escolha o projeto que quer fazer o relatório: ', visible=False, key="1"), sg.Input(key='board_id', visible=False)],
                [sg.Text('Escolha que pessoa quer filtrar: ', visible=False, key="2"), sg.Input(key='person_id', visible=False)],
                [sg.Text('Data com o formato YYYY-MM-DD', visible=False, key="3")],
                [sg.Text('Data de inicio: ', visible=False, key="4"), sg.Input(key='date_ini', visible=False)],
                [sg.Text('Data de final: ', visible=False, key="5"), sg.Input(key='date_end', visible=False)],
                [sg.Text("Path para salvar relatório: ", visible=False, key="6"), sg.FolderBrowse(key="path")],
                [sg.Button('Criar')]
            ]
        self.api = None
        self.window = sg.Window(
                "GitLab Report",
                icon=os.path.join(HERE, 'logo.py')
        ).layout(layout)


    def run(self):
        while True:
            event, values = self.window.read()
            if event == "Exit" or event == sg.WIN_CLOSED:
                break
            if event == "Pesquisar projeto":
                self.api = APIInterface(values["project_id"])
                if values["token"] != "":
                    self.api.list_projects_boards(values["token"])
                self.api.list_projects_boards("")
                self.api.list_all_users()
                for each in range(1,7,1):
                    self.window[str(each)].update(visible=True)
                self.window["board_id"].update(visible=True)
                self.window["person_id"].update(visible=True)
                self.window["date_ini"].update(visible=True)
                self.window["date_end"].update(visible=True)
            if event == "Criar":
                self.api.get_board_by_id(values["board_id"])
                self.api.format_markdow(values["person_id"], values["path"], values["date_ini"], values["date_end"])


def main():
    Window = GitLabKabanUi()
    Window.run()
