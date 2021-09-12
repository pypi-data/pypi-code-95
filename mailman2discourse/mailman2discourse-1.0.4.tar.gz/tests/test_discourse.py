import pytest
import time
from mailman2discourse import discourse


class DiscourseTest(discourse.Discourse):

    def connect(self):
        r = super().connect()
        kwargs = {
            'max_topics_in_first_day': '1000000',
            'max_replies_in_first_day': '1000000',
        }
        self.settings_set(**kwargs)
        return r


def test_connect(test_options):
    d = DiscourseTest(test_options).connect()
    assert 'version' in d.about


def test_enforce_group_name_length():
    good = 'goodname'
    assert good == discourse.Discourse.enforce_group_name_length(good)
    too_long = 'a' * (discourse.Discourse.GROUP_NAME_LENGTH_MAX * 2)
    shorter = discourse.Discourse.enforce_group_name_length(too_long)
    assert len(shorter) == discourse.Discourse.GROUP_NAME_LENGTH_MAX
    assert shorter[0] == 'g'


def test_enable_category_group_moderation_setting(test_options):
    d = DiscourseTest(test_options)
    d.about = {'version': '2.5.5'}
    assert 'group_review' in d.enable_category_group_moderation_setting()
    d.about = {'version': '2.6.0'}
    assert 'group_moderation' in d.enable_category_group_moderation_setting()


def test_version_check(test_options):
    d = DiscourseTest(test_options)
    d.about = {'version': '2.5.5'}
    assert d.version_check() is True
    d.about = {'version': '1.0.0'}
    with pytest.raises(discourse.DiscourseErrorMinVersion):
        d.version_check()


@pytest.mark.parametrize("name", [
    'simpleone',
    'with_underscore',  # _ is converted into -
    'with.dot',  # . is converted into -
])
def test_category_create(test_options, name):
    d = DiscourseTest(test_options).connect()
    try:
        d.args.dry_run = True
        before0, after0 = d.category_create(name)
        assert before0 is None
        assert after0['name'] == name

        d.args.dry_run = False
        before0, after0 = d.category_create(name)
        assert before0 is None
        assert after0['name'] == name
        assert after0['custom_fields[import_id]'] == name

        before1, after1 = d.category_create(name)
        assert after0 == before1
        assert before1 == after1

        d.args.dry_run = True
        assert d.category_delete(name)['id'] == after1['id']
        d.args.dry_run = False
        assert d.category_delete(name)['id'] == after1['id']
        assert d.category_delete(name) is None
    finally:
        d.category_delete(name)


def test_category_set_action(test_options):
    d = DiscourseTest(test_options).connect()
    name = 'CATEGORYNAME'
    group = 'CATEGORYNAME-me'
    try:
        _, category = d.category_create(name)
        assert category['name'] == name
        color = '112233'
        before, after = d.category_set(name, color=color)
        assert after['color'] == color

        d.group_create(group)
        permission_group = f'permissions[{group}]'
        permission_one = '1'
        approval = 'custom_fields[require_topic_approval]'
        approval_value = 'true'
        before, after = d.category_set(name, **{
            permission_group: permission_one,
            approval: approval_value,

        })
        assert after[permission_group] == permission_one
        assert after[approval] == approval_value
        assert 'permissions[everyone]' in before
        assert 'permissions[everyone]' not in after

        #
        # permissions[everyone] superseeds permissions[group_name]
        #
        permission_everyone = 'permissions[everyone]'
        before, after = d.category_set(name, **{permission_everyone: permission_one})
        assert after[permission_everyone] == permission_one
        assert permission_group in before
        assert permission_group not in after

    finally:
        d.category_delete(name)
        d.group_delete(group)


def test_category_set_dry_run(test_options):
    d = DiscourseTest(test_options).connect()
    name = 'CATEGORYNAME'
    try:
        _, category = d.category_create(name)
        assert category['name'] == name
        color = '112233'

        d.args.dry_run = True
        before, after = d.category_set(name, color=color)
        assert before['color'] != color
        assert after['color'] == color

        d.args.dry_run = False
        before, after = d.category_set(name, color=color)
        assert before['color'] != color
        assert after['color'] == color

        before, after = d.category_set(name, color=color)
        assert before == after

    finally:
        d.category_delete(name)


def test_group_create(test_options):
    name = 'GROUPNAME'
    try:
        d = DiscourseTest(test_options).connect()

        d.args.dry_run = True
        before0, after0 = d.group_create(name)
        assert before0 is None
        assert after0['group[name]'] == name

        d.args.dry_run = False
        before0, after0 = d.group_create(name, **{'group[public_exit]': 'true'})
        assert before0 is None
        assert after0['group[name]'] == name
        assert after0['group[public_exit]'] == 'true'

        before1, after1 = d.group_create(name, **{'group[public_exit]': 'false'})
        assert after1['group[public_exit]'] == 'false'

        before2, after2 = d.group_create(name)
        assert after1 == before2
        assert before2 == after2

        assert d.group_delete(name)['group[id]'] == after1['group[id]']
        assert d.group_delete(name) is None
    finally:
        d.group_delete(name)


@pytest.mark.parametrize("email", [
    'user@example.com',
    'UPPERCASE@example.com',  # mails are converted to all lowercase
    'some+else@test.com',  # + must be quoted otherwise it fails
])
def test_user_create(test_options, email):
    d = DiscourseTest(test_options).connect()
    try:
        password = 'dashkeedfakojfiesMob'
        username = 'MYUSERNAME'
        kwargs = {
            'username': username,
            'password': password,
        }
        d.args.dry_run = True
        before0, after0 = d.user_create(email, **kwargs)
        assert before0 is None
        assert after0['email'] == email
        assert after0['username'] == username

        d.args.dry_run = False
        before0, after0 = d.user_create(email, **kwargs)
        assert before0 is None
        assert after0['email'] == email.lower()
        assert after0['username'] == username

        before1, after1 = d.user_create(email, **kwargs)
        assert after0 == before1
        assert before1 == after1

        d.args.dry_run = True
        assert d.user_delete(email)['id'] == after1['id']
        d.args.dry_run = False
        assert d.user_delete(email)['id'] == after1['id']
        assert d.user_delete(email) is None
    finally:
        d.user_delete(email)


def test_user_create_active(test_options):
    email = 'user@example.com'
    d = DiscourseTest(test_options).connect()
    try:
        password = 'dashkeedfakojfiesMob'
        username = 'MYUSERNAME'
        kwargs = {
            'username': username,
            'password': password,
            'active': 'false',
        }

        before0, after0 = d.user_create(email, **kwargs)
        assert before0 is None
        assert after0['active'] == 'false'

        kwargs['active'] = 'true'
        before1, after1 = d.user_create(email, **kwargs)
        assert before1['active'] == 'false'
        assert after1['active'] == 'true'

        kwargs['active'] = 'false'
        before2, after2 = d.user_create(email, **kwargs)
        assert before2['active'] == 'true'
        assert after2['active'] == 'false'

    finally:
        d.user_delete(email)


def test_user_active(test_options):
    email = 'user@example.com'
    d = DiscourseTest(test_options).connect()
    try:
        password = 'dashkeedfakojfiesMob'
        username = 'MYUSERNAME'
        kwargs = {
            'username': username,
            'password': password,
            'active': 'true',
        }
        _, _ = d.user_create(email, **kwargs)

        d.args.dry_run = True
        before0, after0 = d.user_active(email, 'false')
        assert before0['active'] == 'true'
        assert after0['active'] == 'false'

        d.args.dry_run = False
        before0, after0 = d.user_active(email, 'false')
        assert before0['active'] == 'true'
        assert after0['active'] == 'false'

        before1, after1 = d.user_active(email, 'true')
        assert before1['active'] == 'false'
        assert after1['active'] == 'true'

        before2, after2 = d.user_active(email, 'true')
        assert after1 == before2
        assert before2 == after2
    finally:
        d.user_delete(email)


def test_user_trust_level(test_options):
    email = 'user@example.com'
    d = DiscourseTest(test_options).connect()
    try:
        password = 'dashkeedfakojfiesMob'
        username = 'MYUSERNAME'
        kwargs = {
            'username': username,
            'password': password,
            'active': 'true',
        }
        _, _ = d.user_create(email, **kwargs)

        d.args.dry_run = True
        before0, after0 = d.user_trust_level(email, '1')
        assert before0['trust_level'] == '0'
        assert after0['trust_level'] == '1'

        d.args.dry_run = False
        before0, after0 = d.user_trust_level(email, '1')
        assert before0['trust_level'] == '0'
        assert after0['trust_level'] == '1'

        before1, after1 = d.user_trust_level(email, '1')
        assert after0 == before1
        assert before1 == after1

        with pytest.raises(discourse.DiscourseErrorUserTrustLevel):
            d.user_trust_level(email, 'invalid')
    finally:
        d.user_delete(email)


def test_user_create_trust_level_0(test_options):
    email = 'user@example.com'
    d = DiscourseTest(test_options).connect()
    try:
        password = 'dashkeedfakojfiesMob'
        username = 'MYUSERNAME'
        kwargs = {
            'username': username,
            'password': password,
        }
        before, after = d.user_create(email, **kwargs)
        assert before is None
        assert after['trust_level'] == '0'
    finally:
        d.user_delete(email)


def test_user_create_trust_level_1(test_options):
    email = 'user@example.com'
    d = DiscourseTest(test_options).connect()
    try:
        password = 'dashkeedfakojfiesMob'
        username = 'MYUSERNAME'
        trust_level = '1'
        kwargs = {
            'username': username,
            'password': password,
            'trust_level': trust_level,
        }
        before, after = d.user_create(email, **kwargs)
        assert before is None
        assert after['trust_level'] == trust_level

    finally:
        d.user_delete(email)


def test_user_delete_and_block(test_options):
    d = DiscourseTest(test_options).connect()
    email = 'banned0@example.com'
    password = 'dashkeedfakojfiesMob'
    username = 'MYUSERNAME'
    kwargs = {
        'username': username,
        'password': password,
    }
    d.emails_allow(email)
    assert d.emails_check(email) is True
    before0, after0 = d.user_create(email, **kwargs)
    assert before0 is None
    assert after0['email'] == email
    assert after0['username'] == username

    email_similar = 'banned1@example.com'
    assert d.emails_check(email_similar) is True
    assert d.user_delete(email, block_email=True)['id'] == after0['id']
    assert any([e["email"] == email for e in d.emails_screened()]) is True
    assert d.emails_check(email) is False
    assert d.emails_check(email_similar) is False
    assert d.emails_allow(email) is True


def test_user_duplicate(test_options):
    d = DiscourseTest(test_options).connect()
    first_email = 'someuser@some.com'
    second_email = 'user@some.com'
    try:
        password = 'dashkeedfakojfiesMob'
        _, first = d.user_create(first_email, **{
            'active': 'true',
            'username': 'FIRST',
            'password': password,
        })
        _, second = d.user_create(second_email, **{
            'active': 'true',
            'username': 'SECOND',
            'password': password,
        })
        assert first['id'] != second['id']
    finally:
        assert d.user_delete(first_email) is not None
        assert d.user_delete(second_email) is not None


def test_user_name_invalid(test_options):
    d = DiscourseTest(test_options).connect()
    email = 'someuser@some.com'
    with pytest.raises(discourse.DiscourseErrorUserCreate) as e:
        password = 'dashkeedfakojfiesMob'
        invalid_username = 'USERNAME'
        kwargs = {
            'username': invalid_username,
            'password': password,
        }
        _, _ = d.user_create(email, **kwargs)
    assert 'That username is not allowed' in str(e)


def test_user_preferences_set(test_options):
    d = DiscourseTest(test_options).connect()
    email = 'me@example.com'
    try:
        kwargs = {
            'active': 'true',
            'username': 'myusername',
            'password': 'dashkeedfakojfiesMob',
        }
        _, _ = d.user_create(email, **kwargs)
        _, _ = d.user_preferences_set(email, locale='fr', hide_profile_and_presence='true')

        #
        # hide_profile_and_presence is in user['user_option']
        # locale is in user
        #
        d.args.dry_run = True
        before0, after0 = d.user_preferences_set(
            email, locale='en', hide_profile_and_presence='false')
        assert before0['locale'] == 'fr'
        assert before0['hide_profile_and_presence'] == 'true'

        d.args.dry_run = False
        before1, after1 = d.user_preferences_set(
            email, locale='en', hide_profile_and_presence='false')
        assert before0['locale'] == 'fr'
        assert before0['hide_profile_and_presence'] == 'true'
        assert after1['locale'] == 'en'
        assert after1['hide_profile_and_presence'] == 'false'

        before2, after2 = d.user_preferences_set(
            email, locale='en', hide_profile_and_presence='false')
        assert before2 == after2

    finally:
        d.user_delete(email)


def test_group_member(test_options):
    d = DiscourseTest(test_options).connect()
    email = 'user@example.com'
    group_name = 'GROUPNAME'
    try:
        password = 'dashkeedfakojfiesMob'
        username = 'MYUSERNAME'
        _, user = d.user_create(email, **{
            'active': 'true', 'username': username, 'password': password})
        _, group = d.group_create(group_name)

        #
        # Verify idempotence with owner=False
        #
        d.args.dry_run = True
        with pytest.raises(discourse.DiscourseErrorUserNotFound):
            d.group_member_create(group_name, 'unknown@example.com', owner=False)
        before0, after0 = d.group_member_create(group_name, email, owner=False)
        assert before0 is None
        assert after0['username'] == username

        d.args.dry_run = False
        with pytest.raises(discourse.DiscourseErrorUserNotFound):
            d.group_member_create(group_name, 'unknown@example.com', owner=False)
        before0, after0 = d.group_member_create(group_name, email, owner=False)
        assert before0 is None
        assert after0['username'] == username

        before1, after1 = d.group_member_create(group_name, email, owner=False)
        assert after0 == before1
        assert before1 == after1

        #
        # Modify owner to True
        #
        before2, after2 = d.group_member_create(group_name, email, owner=True)
        assert before2['id'] == after2['id']
        assert before2['owner'] is False
        assert after2['owner'] is True
        #
        # Modify owner to False
        #
        before3, after3 = d.group_member_create(group_name, email, owner=False)
        assert before3['id'] == after3['id']
        assert before3['owner'] is True
        assert after3['owner'] is False

        #
        # Delete
        #
        d.args.dry_run = True
        assert d.group_member_delete(group_name, email)['id'] == after1['id']
        d.args.dry_run = False
        assert d.group_member_delete(group_name, email)['id'] == after1['id']
        assert d.group_member_delete(group_name, email) is None

        #
        # Added with owner=True
        #
        before0, after0 = d.group_member_create(group_name, email, owner=True)
        assert before0 is None
        assert after0['username'] == username

    finally:
        d.group_delete(group_name)
        d.user_delete(email)


def test_settings(test_options):
    d = DiscourseTest(test_options).connect()
    saved = d.settings_get()
    try:
        initial_values = {
            'email_in': "true",
            'download_remote_images_to_local': "true",
        }
        d.settings_set(**initial_values)

        kwargs = {
            'email_in': "false",
            'download_remote_images_to_local': "false",
        }
        d.args.dry_run = True
        before0, after0 = d.settings_set(**kwargs)
        assert after0['email_in'] == "false"
        assert after0['download_remote_images_to_local'] == "false"

        d.args.dry_run = False
        before0, after0 = d.settings_set(**kwargs)
        assert after0['email_in'] == "false"
        assert after0['download_remote_images_to_local'] == "false"

        before1, after1 = d.settings_set(**kwargs)
        assert before1 == after0
        assert before1 == after1
    finally:
        d.settings_set(**saved)


def test_category_notifications(test_options):
    email = 'user@example.com'
    category_name = 'CATNAME'
    try:
        d = DiscourseTest(test_options).connect()
        password = 'dashkeedfakojfiesMob'
        username = 'MYUSERNAME'
        _, user = d.user_create(email, **{
            'active': 'true', 'username': username, 'password': password})
        _, category = d.category_create(category_name)

        level0 = '2'
        _, after0 = d.category_notifications(email, category_name, level0)
        assert after0 == level0

        level1 = '1'
        d.args.dry_run = True
        before1, after1 = d.category_notifications(email, category_name, level1)
        assert before1 == after0
        assert after1 == level1

        d.args.dry_run = False
        before1, after1 = d.category_notifications(email, category_name, level1)
        assert before1 == after0
        assert after1 == level1

        before2, after2 = d.category_notifications(email, category_name, level1)
        assert before2 == after1
        assert before2 == after2
    finally:
        d.user_delete(email)
        d.category_delete(category_name)


def test_category_info(test_options):
    d = DiscourseTest(test_options).connect()
    name = 'ABCD'
    try:
        _, _ = d.category_create(name)
        original = 'This is the original content to look for'
        _, _ = d.category_info_set(name, original)

        d.args.dry_run = True
        modified = 'Something different is said about the category'
        before0, after0 = d.category_info_set(name, modified)
        assert before0 == original
        assert after0 == modified

        d.args.dry_run = False
        before0, after0 = d.category_info_set(name, modified)
        assert before0 == original
        assert after0 == modified

        before1, after1 = d.category_info_set(name, modified)
        assert after0 == before1
        assert before1 == after1

    finally:
        d.category_delete(name)


def test_message_load(test_options):
    topic = None
    email = 'user@example.com'
    category_name = 'CATNAME'
    try:
        d = DiscourseTest(test_options).connect()
        password = 'dashkeedfakojfiesMob'
        username = 'MYUSERNAME'
        _, user = d.user_create(email, **{
            'active': 'true', 'username': username, 'password': password})
        _, category = d.category_create(category_name)
        d.settings_set(email_in='true',
                       log_mail_processing_failures='true',
                       email_in_min_trust='0',
                       min_post_length='5',
                       min_first_post_length='5',
                       min_title_similar_length='10240')
        email_in = 'list@example.com'
        d.category_set(category_name,
                       email_in=email_in,
                       email_in_allow_strangers='true')
        subject = f'MESSAGE ONE {time.time()}'
        message = f"""From user@example.com  Mon Nov  9 21:54:11 1999
Message-ID: <msg@{time.time()}>
From: "Some One" <user@example.com>
To: <list@example.com>
Date: Fri,  6 Apr 2007 15:43:55 -0700 (PDT)
Subject: {subject}

First content
        """
        assert 'email has been received' in d.message_load(message, None).text
        topic = d.topic_wait(category_name, subject)
    finally:
        if topic:
            d.topic_delete(topic['id'])
        d.user_delete(email)
        d.category_delete(category_name)
        d.settings_set(email_in='false')
