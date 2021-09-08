from blaugue import search, user, post, chat
from blaugue.base import BlaugueBase


class Blaugue(BlaugueBase):

    def __init__(self, **connexion):
        super().__init__(connexion['email'], connexion['password'])
        self.user = connexion['email']
        self.password = connexion['password']
        super().set_token()

    def search(self, query):
        return search.BlaugueResults(super().request(super().search_url.format(query)).json(), super())

    def get_user(self, email):
        return user.BlaugueUser(super().request(super().user_url.format(email)).json(), super())

    def get_post(self, post_id):
        return post.BlauguePost(super().request(super().post_url.format(post_id)).json(), super())

    def get_lasts_post(self):
        posts = []
        for _post in super().request(super().last_posts_url).json():
            posts.append(post.BlauguePost(_post, super()))
        return posts

    def all_users(self):
        all_users = []
        for infos in super().request(super().user_url.format('all')).json()['users']:
            all_users.append(user.BlaugueUser(infos, super()))
        return all_users

    def get_chats(self):
        return [self.get_chat(chat_name['name']) for chat_name in super().request(super().url + '/chats').json()]

    def get_chat(self, chat_name):
        return chat.BlaugueChat(super().request(super().chat_url.format(chat_name)).json(), super())

    def __str__(self):
        return self.user

    def __bool__(self):
        return super().isright()

    def __next__(self):
        return super().get_token()

    def __bytes__(self):
        return super().get_password()

    @property
    def connected(self):
        return self.get_user(self.user)
