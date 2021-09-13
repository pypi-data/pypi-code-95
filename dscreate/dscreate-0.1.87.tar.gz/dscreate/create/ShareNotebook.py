import pyperclip
import argparse

class ShareNotebook:

    def get_file_path(self, url):
        """
        Pull out the organization, repository name, branch, and file path
        from a github url.
        """
        org, repo = url.split('github.com/')[1].split('/')[:2]
        paths = url.split('blob/')[1].split('/')
        branch = paths[0]
        file_path = '/'.join(paths[1:])
        return org, repo, branch, file_path

    def get_assignment_url(self, org, repo, branch, file_path):
        """
        org - The name of a github organization.
        repo - The name of a github repository.
        branch - The name of a github repository branch.
        file_path - The path pointing to a jupyter notebook in a github repository.

        Returns: An illumidesk link that will clone the notebook onto your personal
                server and open the notebook.
        """
        template = """https://flatiron.illumidesk.com/user/x/git-pull?repo=https%3A%2F%2Fgithub.com%2F{}%2F{}&branch={}&subpath={}"""
        return template.format(org, repo, branch, file_path)

    def main(self, url):
        """
        Main function for creating the illumidesk link.
        The link is added to your clipboard.
        """
        org, repo, branch, file_path = self.get_file_path(url)
        link = self.get_assignment_url(org, repo, branch, file_path)
        pyperclip.copy(link)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create an illumidesk link for a github hosted notebook.')
    parser.add_argument('url', action="store")
    args = parser.parse_args()
    url = args.url
    share = ShareNotebook()
    share.main(url)
    print()
    print('Url has been copied to your clipboard!')
    print()