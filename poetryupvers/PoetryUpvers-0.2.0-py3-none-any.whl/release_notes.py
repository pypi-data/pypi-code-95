"""PyProjectUpVers

Copyright (c) 2021 - GitLab
"""

from os import getenv
from gitlab_ps_utils.api import GitLabApi
import poetryupvers.git as git

class GitLabReleaseNoteGenerator():
    """
        Generates release notes for a software release based on commit messages and MRs

        Outputs a file with a format like:

        ## Release Notes/Included MRs:

        - [Merge request title](!merge request ID)
        - ...
    """
    def __init__(self):
        self.api = GitLabApi()
        self.project_id = getenv('CI_PROJECT_ID')
        self.token = getenv('ACCESS_TOKEN')
        self.release_notes = "## Release Notes/Included MRs:\n\n"
        self.mr_dict = {}
        
    def generate_mr_map(self):
        """
            Iterates over all hashes between HEAD and the latest numeric tag

            Iterates over all related MRs related to the commit hashes

            Appends the related MR title and ID to the mr_dict dictionary
        """
        for commit in git.get_all_hashes_from_tag(git.get_latest_tag()):
            for related_mr in self.get_related_mrs(commit):
                self.append_to_mr_map(related_mr["title"], related_mr["iid"])
                
    def generate_release_notes(self):
        """
            Creates the final, formatted release notes text
        """
        for mr_num, mr_name in self.mr_dict.items():
            self.append_to_release_notes(
                self.format_note_line(mr_num, mr_name))
        print(self.release_notes)
    
    def save_release_notes(self, path=None):
        if not path:
            path = "./release_notes.md"
        print(f"Writing release notes to {path}")
        with open(path, "w") as f:
            f.write(self.release_notes)

    def get_related_mrs(self, commit):
        """
            Returns a generator function iterating over the

            projects/{id}/repository/commits/{commit}/merge_requests endpoint
        """
        base_url = getenv('CI_SERVER_URL')
        return self.api.list_all(base_url, self.token, 
            f"projects/{self.project_id}/repository/commits/{commit}/merge_requests")

    def append_to_mr_map(self, mr_name, mr_num):
        self.mr_dict[mr_num] = mr_name

    def append_to_release_notes(self, line):
        self.release_notes += line

    def format_note_line(self, mr_num, mr_name):
        return f"- [{mr_name}](!{mr_num})\n"


    