import pickle


def mailman_create_config():
    c = {
        'description': 'this is a clear description of the category',
        'subscribe_policy': 0,
        'private_roster': 0,
        'archive': 1,
        'archive_private': False,
        # 'default_member_moderation':
        'members': {
        },
        'moderator': [],
        'owner': [],
        'ban_list': [],
        'digest_members': {
        },
        'language': {
        },
        'delivery_status': {
        },
        'user_options': {
        },
        'usernames': {
        },
    }
    return c


def mailman_add(c, email, **kwargs):
    for k, v in (('members', True),
                 ('language', 'en'),
                 ('delivery_status', 0),
                 ('user_options', 0),
                 ('usernames', 'My Name')):
        c[k][email] = kwargs.get(k, v)

    for k, v in (('moderator', False),
                 ('owner', False)):
        if kwargs.get(k, v):
            c[k].append(email)


def mailman_write_config(p, c):
    pickle.dump(c, open(p, 'wb'))
