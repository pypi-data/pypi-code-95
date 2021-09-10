import os
import typing
import pickle
import requests
from datetime import date
from dataclasses import dataclass, field
from gitlab_kaban_report.constants import (
    API_URL,
    HERE,
)
from gitlab_kaban_report.encrypt import EncryptRSA


@dataclass
class APIInterface:
    project_id: str
    project_boards_url: str = "/projects/[id]/boards/"
    token: str = field(init=False, repr=False, default="")
    boards_dict: dict = field(init=False, repr=False, default_factory=dict)
    encrypter = EncryptRSA()

    def __post_init__(self):
        self.project_boards_url = self.project_boards_url.replace(
            "[id]",
            self.project_id
        )

    def get_token(self, token="") -> None:
        files = os.listdir(HERE)
        if "TOKEN" not in files:
            self.token=token
            token_encrypt = self.encrypter.encrypt(self.token)

            with open(os.path.join(HERE, "TOKEN"), "wb") as f:
                pickle.dump(token_encrypt, f)

        else:
            with open(os.path.join(HERE, "TOKEN"), "rb") as f:
                encrypt_token = pickle.load(f)
            self.token = self.encrypter.decrypt(encrypt_token)

    def format_header(self) -> typing.Mapping[str, str]:
        header = {
            "PRIVATE-TOKEN": self.token
        }
        return header

    def get_project_boards(self, token) -> list:
        self.get_token(token)
        url = API_URL + self.project_boards_url
        headers = self.format_header()
        response = requests.get(url=url, headers=headers)
        if response.status_code == 200:
            return response.json()
        raise Exception("Não foi possível pegar os boards\n{}".format(
            response.text))

    def list_projects_boards(self, token="") -> None:
        boards = self.get_project_boards(token)
        print("-------------------------------------------------------")
        print("- Escolha o projeto que quer fazer o relatório        -")
        for index, board in enumerate(boards):
            self.boards_dict[index] = {
                "id": board["id"],
                "name": board["name"]
            }
            print("- {}: {}-".format(index, board["name"]))
        print("-------------------------------------------------------")

    def get_board_by_id(self, opt) -> list:
        headers = self.format_header()
        url = API_URL + self.project_boards_url + "{}/lists".format(
            self.boards_dict[int(opt)]["id"]
        )
        response = requests.get(url=url, headers=headers)
        if response.status_code == 200:
            self.boards_labels = []
            for board in response.json():
                self.boards_labels.append(board['label']['name'])
            return response.json()
        raise Exception("Erro ao requisitar board {}".format(
            self.boards_dict[int(opt)]["name"]
        )
        )

    def get_issues_of_project(self) -> list:
        url = API_URL + "/projects/{}/issues".format(self.project_id)
        headers = self.format_header()
        response = requests.get(url=url, headers=headers)
        if response.status_code == 200:
            return response.json()
        raise Exception("Erro ao requisitar issues")

    def list_all_users(self):
        issues = self.get_issues_of_project()
        self.people = {}
        for issue in issues:
            for person in issue["assignees"]:
                self.people[person["name"]] = {
                    "id": person["id"],
                    "name": person["name"],
                    "username": person["username"]

                }
        self.choose = {}
        print("- Escolha que pessoa quer filtrar: -")
        for index, key in enumerate(self.people.keys()):
            self.choose[index] = {"id": self.people[
                key]["id"], "name": self.people[key]["name"],
                "username": self.people[key]["username"]}
            print("- OPT: {} Name: {} -".format(index, key))
        print("-------------------------------------------------------")

    def get_issues_of_a_user(self, opt):
        url = API_URL + "/projects/{}/issues/?assignee_id={}".format(
            self.project_id,
            self.choose[int(opt)]["id"]
        )
        headers = self.format_header()
        response = requests.get(url=url, headers=headers)
        if response.status_code == 200:
            return response.json()
        raise Exception("Erro ao requisitar issues  do usuário")

    def separe_issues_of_user(self, opt, date_in, date_of):
        issues = self.get_issues_of_a_user(opt)
        date_in = date.fromisoformat(date_in)
        date_of = date.fromisoformat(date_of)
        self.user = {k: [] for k in self.boards_labels}
        self.user["CLOSE"] = []
        for issue in issues:
            issue_update = date.fromisoformat(issue["updated_at"].split("T")[0])
            if issue_update < date_in or issue_update > date_of:
                continue
            for label in self.boards_labels:
                if label in issue['labels']:
                    self.user[label].append(issue)
            if issue["state"] == "closed":
                self.user["CLOSE"].append(issue)

    def format_markdow(self, opt, path, date_in, date_of):
        self.separe_issues_of_user(opt, date_in, date_of)
        now_date = date.today()
        markdown = ""
        format_now = "# Relatório dia {}/{}/{}   \n".format(now_date.day, now_date.month, now_date.year)
        markdown += format_now
        markdown += "## Usuário: {}   \n".format(self.choose[int(opt)]["name"])
        for key in self.user.keys():
            markdown += "### {}   \n".format(key)
            for issue in self.user[key]:
                if issue["closed_at"] != None:
                    closed = date.fromisoformat(issue["closed_at"].split("T")[0])
                    create = date.fromisoformat(issue["created_at"].split("T")[0])
                    timestamp = now_date - create
                    markdown += "* titulo: {} duração: {}   \n".format(
                                issue["title"],
                                timestamp.days
                            )
                else:
                    closed = date.fromisoformat(issue["updated_at"].split("T")[0])
                    create = date.fromisoformat(issue["created_at"].split("T")[0])
                    timestamp = now_date - create
                    markdown += "* titulo: {} duração: {}   \n".format(
                                issue["title"],
                                timestamp.days
                            )
        with open(os.path.join(path, "{}_{}_{}_{}.md".format(
                    self.choose[int(opt)]["username"],
                    now_date.day,
                    now_date.month,
                    now_date.year)
                ),
                "w"
                ) as f:
            f.write(markdown)
        print("Done")
