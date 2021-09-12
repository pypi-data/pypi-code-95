from github import Github


class GithubUtility:
    def __init__(self):
        AUTH_TOKEN = input('Input your github token: ')
        self.github = Github(AUTH_TOKEN)
        self.user = self.github.get_user()

    def get_repo(self, name):
        return self.user.get_repo(name)

    def create_repo(self, name, private=False, gitignore=""):
        return self.user.create_repo(name, private=private, gitignore_template=gitignore, auto_init=True)

    def delete_repo(self, name):
        self.get_repo(name).delete()