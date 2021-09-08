from blaugue.user import BlaugueUser
from blaugue.post import BlauguePost
from blaugue.tag import BlaugueTag


class BlaugueResults:

    def __init__(self, results: dict, base: object):
        results['tags'] = [BlaugueTag(tag, base) for tag in results['tags']]
        results['users'] = [BlaugueUser(user, base) for user in results['users']]
        results['posts'] = [BlauguePost(post, base) for post in results['posts']]
        self._results = results

    @property
    def results(self):
        """
        :return: List of all results
        """
        return self._results['users'] + self._results['posts'] + self._results['tags']

    @property
    def json_results(self):
        """
        :return: List of all results
        """
        return self._results

    @property
    def users_results(self):
        """
        :return: List of BlaugueUser() object
        """
        return self._results['users']

    @property
    def posts_results(self):
        """
        :return: List of BlauguePost() object
        """
        return self._results['posts']

    @property
    def tags_results(self):
        """
        :return: List of BlaugueTag() object
        """
        return self._results['tags']
