from mailman2discourse import importer
from mailman2discourse import discourse
from mailman2discourse.discourse import Discourse
from mailman2discourse.mailman import Mailman
from mailman2discourse import retry
import pytest
from tests.helpers_mailman import (
    mailman_write_config,
    mailman_add)
import time


def test_main(test_options, mocker):
    m = mocker.patch('mailman2discourse.importer.Importer.importer',
                     return_value=(None, None))
    i = importer.Importer(test_options)
    assert i.main() == 0
    m.assert_called()


def test_group_moderators_settings(test_options):
    i = importer.Importer(test_options)
    i.mailman.info['private_roster'] = 2
    s = i.group_moderators_settings()
    assert s['group[members_visibility_level]'] == '3'
    assert s['group[full_name]'] == 'listname-mo'


def test_group_members_settings(test_options):
    m_everyone = Discourse.GROUP_MEMBERS_VISIBILITY_LEVEL_EVERYONE
    g_everyone = Discourse.GROUP_VISIBILITY_LEVEL_EVERYONE

    incoming = (Mailman.ROSTER_PUBLIC, Mailman.SUBSCRIBE_POLICY_OPEN)
    expected = {
         'group[full_name]': 'listname-me',
         'group[public_admission]': 'true',
         'group[allow_membership_requests]': 'false',
         'group[visibility_level]': g_everyone,
         'group[members_visibility_level]': m_everyone,
     }

    i = importer.Importer(test_options)
    (i.mailman.info['private_roster'], i.mailman.info['subscribe_policy']) = incoming
    assert i.group_members_settings() == expected


def test_users_add_invalid(test_options):
    i = importer.Importer(test_options)
    invalid_email = 'invalidmail@'
    valid_email = 'valid@example.com'
    try:
        i.mailman.user = {
            invalid_email: {},
            valid_email: {},
        }
        before, after = i.users_add()
        assert before == {valid_email: None}
        assert invalid_email not in after
        assert valid_email in after
        assert invalid_email not in i.mailman.user
    finally:
        i.discourse.user_delete(invalid_email)
        i.discourse.user_delete(valid_email)


@pytest.mark.parametrize("email,raw,cooked", [
    ('user0@example.com', 'Loïc Dachary', 'Loic_Dachary'),
    ('user1@example.com', '  - / my name _.', 'my_name'),
    ('user2@example.com', '__other name__', 'other_name'),
    ('user3@example.com', 'one__underscore', 'one_underscore'),
    ('user4@example.com', 'a hash is used if the name is too long', '7e65550957227bd38fe2'),
])
def test_users_add_normalize(test_options, email, raw, cooked):
    i = importer.Importer(test_options)
    try:
        i.mailman.user = {
            email: {
                'usernames': raw,
            },
        }
        before, after = i.users_add()
        assert after[email]['username'] == cooked
    finally:
        i.discourse.user_delete(email)


def test_users_add_preserve_existing_user_preference(test_options):
    i = importer.Importer(test_options)
    i.args.preserve_existing_user_preferences = True
    email = 'user@example.com'
    goodname = 'goodname'
    try:
        #
        # First time around, the user is created and the name is set
        #
        i.mailman.user = {
            email: {
                'usernames': goodname,
            },
        }
        before, after = i.users_add()
        assert before[email] is None
        assert after[email]['name'] == goodname

        #
        # Second time around, the user exists and the name is not overridden
        #
        i.mailman.user = {
            email: {
                'usernames': 'ignoredname',
            },
        }
        before, after = i.users_add()
        assert before[email]['name'] == goodname
        assert after[email]['name'] == goodname

    finally:
        i.discourse.user_delete(email)


def test_users_add_deactivated_preserve_existing_user_preference(test_options):
    i = importer.Importer(test_options)
    i.args.preserve_existing_user_preferences = True
    email = 'user@example.com'
    goodname = 'goodname'
    try:
        #
        # First time around, the user is created and the name is set
        #
        i.mailman.user = {
            email: {
                'usernames': goodname,
            },
        }
        before, after = i.users_add()
        assert before[email] is None
        assert after[email]['name'] == goodname

        #
        # The user is deactivated
        #
        assert after[email]['active'] == 'true'
        user_before, user_after = i.discourse.user_create(email, active='false')
        assert user_before['active'] == 'true'
        assert user_after['active'] == 'false'

        #
        # Second time around, the user exists but it is updated anyways
        # because it needs to be activated, and the name is overriden
        #
        newname = 'newname'
        i.mailman.user = {
            email: {
                'usernames': newname,
            },
        }
        before, after = i.users_add()
        assert before[email]['active'] == 'false'
        assert before[email]['name'] == goodname
        assert after[email]['active'] == 'true'
        assert after[email]['name'] == newname

    finally:
        i.discourse.user_delete(email)


def test_importer_moderation_no(test_options):
    i = importer.Importer(test_options)
    owner = 'owner@example.com'
    moderator = 'moderator@example.com'

    def cleanup():
        i.discourse.group_delete(i.group_moderators_name())
        i.discourse.category_delete(i.name_get())
        i.discourse.user_delete(moderator)
        i.discourse.user_delete(owner)
    cleanup()
    try:
        c = i.mailman.load_pickle()
        mailman_add(c, owner, owner=True)
        mailman_add(c, moderator, moderator=True)
        mailman_write_config(f'{test_options.mailman_config}', c)
        i.mailman.load()

        before0, after0 = i.importer()
        assert before0['category'] is None
        assert list(before0['group-moderators-list'].keys()) == [owner, moderator]
        assert all(v is None for v in before0['group-moderators-list'].values())
        assert 'group-members-list' not in before0
        assert before0['group-moderators'] is None
        assert list(before0['members'].keys()) == [owner, moderator]
        assert 'email_in' in before0['settings']

        assert after0['category']['name'] == test_options.list
        assert after0['settings']['email_in'] == 'true'
        assert after0['group-moderators']['group[name]'].startswith(test_options.list)
        assert owner in after0['group-moderators-list']
        assert moderator in after0['group-moderators-list']
        assert 'group-members' not in after0

        before1, after1 = i.importer()
        assert before1 == after0
        assert before1 == after1
    finally:
        cleanup()


def test_importer_ban_list(test_options):
    i = importer.Importer(test_options)

    banned = 'banned@example.com'

    def cleanup():
        i.discourse.group_delete(i.group_moderators_name())
        i.discourse.category_delete(i.name_get())
        i.discourse.emails_allow(banned)
    cleanup()
    try:
        c = i.mailman.load_pickle()
        c['ban_list'] = [banned]
        mailman_write_config(f'{test_options.mailman_config}', c)
        i.mailman.load()

        assert i.discourse.emails_screened() == []
        before0, after0 = i.importer()
        assert before0['banned'] == set()
        assert after0['banned'] == set([banned])
        assert i.discourse.emails_allow(banned) is True
        assert i.discourse.emails_allow(banned) is False
    finally:
        cleanup()


def test_importer_moderation_approval(test_options):
    i = importer.Importer(test_options)
    owner = 'owner@example.com'
    moderator = 'moderator@example.com'
    member = 'member@example.com'
    try:
        c = i.mailman.load_pickle()
        c['default_member_moderation'] = True
        c['member_moderation_action'] = Mailman.MODERATION_HOLD
        mailman_add(c, owner, owner=True)
        mailman_add(c, moderator, moderator=True)
        mailman_add(c, member)
        mailman_write_config(test_options.mailman_config, c)
        i.mailman.load()

        before0, after0 = i.importer()
        assert before0['category'] is None
        assert list(before0['group-moderators-list'].keys()) == [owner, moderator]
        assert all(v is None for v in before0['group-moderators-list'].values())
        assert list(before0['group-members-list'].keys()) == [owner, moderator, member]
        assert all(v is None for v in before0['group-members-list'].values())
        assert before0['group-moderators'] is None
        assert list(before0['members'].keys()) == [owner, moderator, member]
        assert 'email_in' in before0['settings']

        assert after0['category']['name'] == test_options.list
        assert after0['settings']['email_in'] == 'true'
        assert after0['group-moderators']['group[name]'].startswith(test_options.list)
        for who in (owner, member, moderator):
            assert who in after0['group-members-list']
        for who in (owner, moderator):
            assert who in after0['group-moderators-list']
        assert member not in after0['group-moderators-list']

        before1, after1 = i.importer()
        assert before1 == after0
        assert before1 == after1
    finally:
        i.discourse.group_delete(i.group_moderators_name())
        i.discourse.group_delete(i.group_members_name())
        i.discourse.category_delete(i.name_get())
        i.discourse.user_delete(moderator)
        i.discourse.user_delete(owner)
        i.discourse.user_delete(member)


def test_importer_members_settings(test_options):
    i = importer.Importer(test_options)
    owner = 'owner@example.com'
    moderator = 'moderator@example.com'
    member = 'member@example.com'
    try:
        c = i.mailman.load_pickle()
        c['default_member_moderation'] = True
        c['member_moderation_action'] = Mailman.MODERATION_HOLD
        c['private_roster'] = Mailman.ROSTER_ADMINS
        c['subscribe_policy'] = Mailman.SUBSCRIBE_POLICY_MODERATE
        mailman_add(c, owner, owner=True)
        mailman_add(c, moderator, moderator=True)
        mailman_add(c, member)
        mailman_write_config(test_options.mailman_config, c)
        i.mailman.load()

        before0, after0 = i.importer()
        assert before0['group-members'] is None
        assert (after0['group-members']['group[visibility_level]'] ==
                Discourse.GROUP_VISIBILITY_LEVEL_OWNERS_AND_MEMBERS)
        assert (after0['group-members']['group[members_visibility_level]'] ==
                Discourse.GROUP_MEMBERS_VISIBILITY_LEVEL_GROUP_OWNERS_AND_STAFF)

        before1, after1 = i.importer()
        assert before1 == after0
        assert before1 == after1
    finally:
        i.discourse.group_delete(i.group_moderators_name())
        i.discourse.group_delete(i.group_members_name())
        i.discourse.category_delete(i.name_get())
        i.discourse.user_delete(moderator)
        i.discourse.user_delete(owner)
        i.discourse.user_delete(member)


def email_stranger(d, email):
    subject = f'MESSAGE {time.time()}'
    message = f"""From user@example.com  Mon Nov  9 21:54:11 1999
Message-ID: <msg@{time.time()}>
From: "Some One" <stranger@example.com>
To: <{email}>
Date: Fri,  6 Apr 2007 15:43:55 -0700 (PDT)
Subject: {subject}

First content
    """
    assert 'email has been received' in d.message_load(message, None).text
    return subject


def email_stranger_ok(i, email):
    subject = email_stranger(i.discourse, email)
    topic_id = i.discourse.topic_wait(i.name_get(), subject)['id']
    return subject, topic_id


def email_stranger_ignored(i, email):
    subject = email_stranger(i.discourse, email)
    with pytest.raises(retry.RetryException):
        i.discourse.topic_wait(i.name_get(), subject)


def email_stranger_and_approve(i, email):
    subject = email_stranger(i.discourse, email)
    i.discourse.review_wait(subject)
    return subject, i.discourse.review_approve(subject)


def topic_post(i, email):
    title = f'a perfectly fine msg from {email} {time.time()}'
    message = f'thanks {email} for a nice and interesting message {time.time()}'
    user = i.discourse.user_get(email)
    api_username = i.discourse.d.api_username
    try:
        i.discourse.d.api_username = user['username']
        return title, i.discourse.topic_post(i.name_get(), title, message)
    finally:
        i.discourse.d.api_username = api_username


def topic_post_ok(i, email):
    title, r = topic_post(i, email)
    return title, r['topic_id']


def topic_post_forbidden(i, email):
    with pytest.raises(discourse.DiscourseClientForbidden):
        topic_post(i, email)


def topic_post_and_approve(i, email):
    title, r = topic_post(i, email)
    assert r is None
    return title, i.discourse.review_approve(title)


def user_can_see_topic(i, email, subject):
    user = i.discourse.user_get(email)
    api_username = i.discourse.d.api_username
    try:
        i.discourse.d.api_username = user['username']
        return i.discourse.topic_wait(i.name_get(), subject)['id']
    finally:
        i.discourse.d.api_username = api_username


def user_cannot_see_category(i, email):
    user = i.discourse.user_get(email)
    api_username = i.discourse.d.api_username
    try:
        i.discourse.d.api_username = user['username']
        with pytest.raises(discourse.DiscourseClientForbidden):
            i.discourse.d._get(f'/c/{i.name_get()}/show.json')
    finally:
        i.discourse.d.api_username = api_username
    return True


def verify_moderation_is_no_archive_is_public(i, nonmember, member, moderator):
    subject, topic_id = email_stranger_ok(i, i.email_get())
    assert topic_id == user_can_see_topic(i, nonmember, subject)


def verify_moderation_is_no_archive_is_private(i, nonmember, member, moderator):
    subject, topic_id = email_stranger_ok(i, i.email_get())
    assert user_cannot_see_category(i, nonmember)
    assert topic_id == user_can_see_topic(i, member, subject)


def verify_moderation_is_ignore_archive_is_public(i, nonmember, member, moderator):
    topic_post_forbidden(i, nonmember)
    title, topic_id = topic_post_ok(i, member)
    email_stranger_ignored(i, i.email_get())
    assert topic_id == user_can_see_topic(i, nonmember, title)


def verify_moderation_is_ignore_archive_is_private(i, nonmember, member, moderator):
    assert user_cannot_see_category(i, nonmember)
    title, topic_id = topic_post_ok(i, member)
    assert topic_id == user_can_see_topic(i, member, title)
    email_stranger_ignored(i, i.email_get())


def verify_moderation_is_approval_archive_is_public(i, nonmember, member, moderator):
    title, topic_id = email_stranger_and_approve(i, i.email_get())
    assert topic_id == user_can_see_topic(i, nonmember, title)
    title, topic_id = topic_post_and_approve(i, member)
    assert topic_id == user_can_see_topic(i, nonmember, title)


def verify_moderation_is_approval_archive_is_private(i, nonmember, member, moderator):
    assert user_cannot_see_category(i, nonmember)
    title, topic_id = email_stranger_and_approve(i, i.email_get())
    assert topic_id == user_can_see_topic(i, member, title)
    title, topic_id = topic_post_and_approve(i, member)
    assert topic_id == user_can_see_topic(i, member, title)


@pytest.mark.parametrize("info,verify", [
    ({'moderation': 'no', 'archive': 'public'},
     verify_moderation_is_no_archive_is_public),
    ({'moderation': 'no', 'archive': 'private'},
     verify_moderation_is_no_archive_is_private),
    ({'moderation': 'ignore', 'archive': 'public'},
     verify_moderation_is_ignore_archive_is_public),
    ({'moderation': 'ignore', 'archive': 'private'},
     verify_moderation_is_ignore_archive_is_private),
    ({'moderation': 'approval', 'archive': 'public'},
     verify_moderation_is_approval_archive_is_public),
    ({'moderation': 'approval', 'archive': 'private'},
     verify_moderation_is_approval_archive_is_private),
])
def test_importer_category_settings(test_options, info, verify):
    i = importer.Importer(test_options)
    owner = 'owner@example.com'
    moderator = 'moderator@example.com'
    member = 'member@example.com'
    nonmember = 'nonmember@example.com'
    try:
        c = i.mailman.load_pickle()
        mailman_add(c, owner, owner=True)
        mailman_add(c, moderator, moderator=True)
        mailman_add(c, member)
        mailman_write_config(test_options.mailman_config, c)
        i.mailman.load()
        i.mailman.info.update(info)

        password = 'dashkeedfakojfiesMob'
        username = 'NONMEMBERNAME'
        _, _ = i.discourse.user_create(nonmember, **{
            'active': 'true', 'username': username, 'password': password})

        _, _ = i.importer()

        verify(i, nonmember, member, moderator)

    finally:
        i.discourse.category_topics_delete(i.name_get())
        i.discourse.category_delete(i.name_get())
        i.discourse.group_delete(i.group_moderators_name())
        i.discourse.group_delete(i.group_members_name())
        i.discourse.user_delete(moderator)
        i.discourse.user_delete(owner)
        i.discourse.user_delete(member)
        i.discourse.user_delete(nonmember)


def test_importer_category_settings_force_private(test_options):
    i = importer.Importer(test_options)
    i.args.force_private = True
    member = 'member@example.com'
    nonmember = 'nonmember@example.com'
    try:
        c = i.mailman.load_pickle()
        mailman_add(c, member)
        mailman_write_config(test_options.mailman_config, c)
        i.mailman.load()
        i.mailman.info.update({'archive': 'public'})

        password = 'dashkeedfakojfiesMob'
        username = 'NONMEMBERNAME'
        _, _ = i.discourse.user_create(nonmember, **{
            'active': 'true', 'username': username, 'password': password})

        _, _ = i.importer()

        assert user_cannot_see_category(i, nonmember)
        title, topic_id = topic_post_ok(i, member)
        assert topic_id == user_can_see_topic(i, member, title)

    finally:
        i.discourse.category_topics_delete(i.name_get())
        i.discourse.category_delete(i.name_get())
        i.discourse.group_delete(i.group_moderators_name())
        i.discourse.group_delete(i.group_members_name())
        i.discourse.user_delete(member)
        i.discourse.user_delete(nonmember)


def test_importer_notifications_level(test_options):
    i = importer.Importer(test_options)
    member = 'member@example.com'
    member_no_mail = 'membernomail@example.com'
    try:
        c = i.mailman.load_pickle()
        mailman_add(c, member, delivery_status=0)
        mailman_add(c, member_no_mail, delivery_status=1)
        mailman_write_config(test_options.mailman_config, c)
        i.mailman.load()

        before0, after0 = i.importer()
        assert before0['category'] is None

        assert (after0['notifications'][member] ==
                Discourse.CATEGORY_NOTIFICATION_LEVEL_WATCHING)
        assert (after0['notifications'][member_no_mail] ==
                Discourse.CATEGORY_NOTIFICATION_LEVEL_MUTED)

        before1, after1 = i.importer()
        assert before1 == after0
        assert before1 == after1
    finally:
        i.discourse.group_delete(i.group_moderators_name())
        i.discourse.category_delete(i.name_get())
        i.discourse.user_delete(member)
        i.discourse.user_delete(member_no_mail)


@pytest.mark.parametrize("private_roster", [
    Mailman.ROSTER_PUBLIC,
    Mailman.ROSTER_MEMBERS,
])
def test_importer_user_preferences(test_options, private_roster):
    i = importer.Importer(test_options)
    fr_language = 'fr@example.com'
    no_language = 'none@example.com'
    try:
        c = i.mailman.load_pickle()
        c['private_roster'] = private_roster
        mailman_add(c, fr_language, language='fr')
        mailman_add(c, no_language)
        del c['language'][no_language]
        mailman_write_config(test_options.mailman_config, c)
        i.mailman.load()

        before0, after0 = i.importer()

        assert after0['preferences'][fr_language]['locale'] == 'fr'
        if private_roster == Mailman.ROSTER_MEMBERS:
            assert after0['preferences'][no_language]['locale'] == ''
        else:
            assert no_language not in after0['preferences']

        before1, after1 = i.importer()
        assert before1 == after0
        assert before1 == after1
    finally:
        i.discourse.group_delete(i.group_moderators_name())
        i.discourse.category_delete(i.name_get())
        i.discourse.user_delete(fr_language)
        i.discourse.user_delete(no_language)


def test_importer_user_preferences_preserve_existing_user_preferences(test_options):
    i = importer.Importer(test_options)
    i.args.preserve_existing_user_preferences = True
    email = 'user@example.com'
    try:
        c = i.mailman.load_pickle()
        mailman_add(c, email, language='fr')
        mailman_write_config(test_options.mailman_config, c)
        i.mailman.load()

        #
        # language is set to 'fr' when the preferences are set for the first time
        #
        before0, after0 = i.importer()
        assert before0['members'][email] is None
        assert after0['preferences'][email]['locale'] == 'fr'

        #
        # language is not changed to 'de' because the user already existed
        # prior to the import
        #
        c['language'][email] = 'de'
        before1, after1 = i.importer()
        assert before1 == after0
        assert before1 == after1
        assert after1['preferences'][email]['locale'] == 'fr'
    finally:
        i.discourse.group_delete(i.group_moderators_name())
        i.discourse.category_delete(i.name_get())
        i.discourse.user_delete(email)


def test_importer_category_info(test_options):
    i = importer.Importer(test_options)
    try:
        long_description = 'This is a description'
        c = i.mailman.load_pickle()
        c['description'] = long_description
        mailman_write_config(test_options.mailman_config, c)
        i.mailman.load()

        before0, after0 = i.importer()
        assert after0['category-info'] == long_description
    finally:
        i.discourse.category_delete(i.name_get())
