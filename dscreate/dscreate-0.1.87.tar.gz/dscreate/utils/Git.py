import sys
from git import Repo, GitCommandError

class GitModel(Repo):

    def __init__(self):
        Repo.__init__(self, '.')
        self.msg = self.get_commit_message()

    def get_commit_message(self):
        # get commit message from repo or custom flag
        sys_args = list(sys.argv)
        i = sys_args.index('-m') if '-m' in sys_args else None
        return sys_args[i + 1] if i else self.head.commit.message

    def add_and_commit(self, commit_msg=None):
        self.git.add(".")
        try:
            self.git.commit("-m", commit_msg if commit_msg else self.msg)
        except GitCommandError:
            print("nothing to commit, working tree clean")

    def merge_solution(self):
        self.git.checkout('solution')
        solution = self.active_branch
        master = self.branches['master']
        base = self.merge_base(solution, master)
        self.index.merge_tree(master, base=base)
        self.index.commit('Merge master into solution.', parent_commits=(solution.commit, master.commit))