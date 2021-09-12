import copy
from deepdiff import DeepDiff
import hashlib
import logging
import os
from mailman2discourse.mailman import Mailman
from mailman2discourse.discourse import Discourse
import re
import unidecode

logger = logging.getLogger(__name__)


class Importer(object):

    def __init__(self, args):
        self.args = args
        self.discourse = Discourse(self.args)
        self.discourse.connect()
        self.mailman = Mailman(self.args)
        self.mailman.load()

    def name_get(self):
        return self.mailman.name

    def email_get(self):
        return f'{self.name_get()}@{self.args.domain}'

    def members_get(self):
        return self.mailman.user.values()

    def owners_get(self):
        return [u for u in self.mailman.user.values() if u.get('owner')]

    def moderators_get(self):
        return [u for u in self.mailman.user.values() if u.get('moderator')]

    @staticmethod
    def category2moderators_group(name):
        return f'{name}-mo'

    def group_moderators_name(self):
        return Discourse.enforce_group_name_length(self.category2moderators_group(self.name_get()))

    @staticmethod
    def category2members_group(name):
        return f'{name}-me'

    def group_members_name(self):
        return Discourse.enforce_group_name_length(self.category2members_group(self.name_get()))

    def user_create(self, email, name):
        username = None
        if name:
            candidate = re.sub(r'^[\W_]*(.*?)[\W_]*$', r'\1', unidecode.unidecode(name))
            candidate = re.sub(r'[\W_]+', r'_', candidate)
            too_short = len(candidate) < Discourse.USERNAME_MIN_LENGTH
            too_long = len(candidate) > Discourse.USERNAME_MAX_LENGTH
            if (not too_short and not too_long and not self.discourse.user_username_exists(
                    candidate)):
                username = candidate
        if not username:
            username = hashlib.md5(email.encode('utf-8')).hexdigest()[:20]
        password = hashlib.md5(os.urandom(16)).hexdigest()[:20]
        return self.discourse.user_create(email, **{
            'username': username,
            'password': password,
            'active': 'true',
            'trust_level': '1',
            'name': name})

    def users_add(self):
        before = {}
        after = {}
        for email in [e for e in self.mailman.user.keys()]:
            if self.args.preserve_existing_user_preferences:
                existing = self.discourse.user_get(email)
                if existing is not None and existing['active'] == 'true':
                    before[email], after[email] = existing, existing
                    continue
            user = self.mailman.user[email]
            name = user.get('usernames', '')
            try:
                before[email], after[email] = self.user_create(email, name)
            except Exception as e:
                logger.error(f'SKIP user {user} because {e}')
                del self.mailman.user[email]
        return before, after

    def users_ban(self):
        before = set([s["email"] for s in self.discourse.emails_screened()])
        after = copy.copy(before)
        for email in self.mailman.info.get('ban_list', []):
            if email in before:
                continue
            if self.discourse.emails_check(email) is False:
                continue
            self.user_create(email, '')
            self.discourse.user_delete(email, block_email=True)
            after.add(email)
        return before, after

    def users_preferences(self, existing_users):
        before = {}
        after = {}
        default_preferences = {}
        if self.mailman.info['private_roster'] != Mailman.ROSTER_PUBLIC:
            default_preferences['hide_profile_and_presence'] = 'true'
        for email, user in self.mailman.user.items():
            if (
                    self.args.preserve_existing_user_preferences and
                    existing_users[email] is not None
            ):
                existing_preferences = self.discourse.user_preferences_get(email)
                before[email], after[email] = existing_preferences, existing_preferences
            else:
                preferences = copy.deepcopy(default_preferences)
                language = user.get('language')
                if language:
                    preferences['locale'] = language
                if preferences != {}:
                    before[email], after[email] = self.discourse.user_preferences_set(
                        email, **preferences)
        return before, after

    def users_notifications(self):
        before = {}
        after = {}
        for email in [e for e in self.mailman.user.keys()]:
            (before[email], after[email]) = self.discourse.category_notifications(
                email, self.name_get(), self.notification_level_get(email))
        return before, after

    def group_members_add(self, group_name, members, owners):
        before = {}
        after = {}
        for users, owner in ((owners, True), (members, False)):
            for user in users:
                email = user['email']
                if email in after:  # owners take precendence over members
                    continue
                before[email], after[email] = self.discourse.group_member_create(
                    group_name, email, owner=owner)
        return before, after

    def notification_level_get(self, email):
        if self.mailman.user[email].get('delivery_status') in (0, '', None):
            return Discourse.CATEGORY_NOTIFICATION_LEVEL_WATCHING
        else:
            return Discourse.CATEGORY_NOTIFICATION_LEVEL_MUTED

    def moderation_get(self):
        return self.mailman.info['moderation']

    def archive_get(self):
        if self.args.force_private:
            return 'private'
        else:
            return self.mailman.info['archive']

    def category_settings(self):
        kwargs = {
            'email_in': self.email_get(),
        }

        create_reply_see = Discourse.GROUP_PERMISSIONS_CREATE_REPLY_SEE
        see = Discourse.GROUP_PERMISSIONS_SEE
        archive = self.archive_get()

        if self.moderation_get() == 'no' and archive == 'public':
            kwargs.update({
                'email_in_allow_strangers': 'true',
                'permissions[everyone]': create_reply_see,
            })
        elif self.moderation_get() == 'no' and archive == 'private':
            kwargs.update({
                'email_in_allow_strangers': 'true',
                f'permissions[{self.group_members_name()}]': create_reply_see,
            })
        elif self.moderation_get() == 'ignore' and archive == 'public':
            kwargs.update({
                'email_in_allow_strangers': 'false',
                f'permissions[{self.group_members_name()}]': create_reply_see,
                'permissions[everyone]': see,
            })
        elif self.moderation_get() == 'ignore' and archive == 'private':
            kwargs.update({
                'email_in_allow_strangers': 'false',
                f'permissions[{self.group_members_name()}]': create_reply_see,
            })
        elif self.moderation_get() == 'approval' and archive == 'public':
            kwargs.update({
                'email_in_allow_strangers': 'true',
                'custom_fields[require_topic_approval]': 'true',
                'custom_fields[require_reply_approval]': 'true',
                'reviewable_by_group_name': self.group_moderators_name(),
            })
        elif self.moderation_get() == 'approval' and archive == 'private':
            kwargs.update({
                'email_in_allow_strangers': 'true',
                f'permissions[{self.group_members_name()}]': create_reply_see,
                'custom_fields[require_topic_approval]': 'true',
                'custom_fields[require_reply_approval]': 'true',
                'reviewable_by_group_name': self.group_moderators_name(),
            })
        else:
            raise Exception(f'unexpected combination moderation={self.moderation_get()} ',
                            f'and archive=={archive}')
        logger.info(kwargs)
        return kwargs

    def group_moderators_settings(self):
        members_visibility_level = {
            Mailman.ROSTER_PUBLIC: Discourse.GROUP_MEMBERS_VISIBILITY_LEVEL_EVERYONE,
            Mailman.ROSTER_MEMBERS: Discourse.GROUP_MEMBERS_VISIBILITY_LEVEL_MEMBERS,
            Mailman.ROSTER_ADMINS: Discourse.GROUP_MEMBERS_VISIBILITY_LEVEL_GROUP_OWNERS_AND_STAFF,
        }[self.mailman.info['private_roster']]
        return {
            'group[full_name]': self.category2moderators_group(self.name_get()),
            'group[visibility_level]': '0',
            'group[members_visibility_level]': members_visibility_level,
            'group[public_admission]': 'false',
            'group[allow_membership_requests]': 'false',
        }

    def group_members_settings(self):
        private_roster = self.mailman.info['private_roster']
        subscribe_policy = self.mailman.info['subscribe_policy']
        if subscribe_policy in (Mailman.SUBSCRIBE_POLICY_OPEN,
                                Mailman.SUBSCRIBE_POLICY_CONFIRM):
            policy = 'public'
        elif subscribe_policy in (Mailman.SUBSCRIBE_POLICY_MODERATE,
                                  Mailman.SUBSCRIBE_POLICY_CONFIRM_THEN_MODERATE):
            policy = 'moderate'
        else:
            logger.error(f'subscribe_policy is unknown ({subscribe_policy} fallback to 2/moderate')
            policy = 'moderate'

        m_everyone = Discourse.GROUP_MEMBERS_VISIBILITY_LEVEL_EVERYONE
        m_members = Discourse.GROUP_MEMBERS_VISIBILITY_LEVEL_MEMBERS
        m_group_owners_and_staff = Discourse.GROUP_MEMBERS_VISIBILITY_LEVEL_GROUP_OWNERS_AND_STAFF
        g_everyone = Discourse.GROUP_VISIBILITY_LEVEL_EVERYONE
        g_owners_and_members = Discourse.GROUP_VISIBILITY_LEVEL_OWNERS_AND_MEMBERS
        converter = {
            (Mailman.ROSTER_PUBLIC, 'public'): {
                'group[public_admission]': 'true',
                'group[allow_membership_requests]': 'false',
                'group[visibility_level]': g_everyone,
                'group[members_visibility_level]': m_everyone,
            },
            (Mailman.ROSTER_MEMBERS, 'public'): {
                'group[public_admission]': 'true',
                'group[allow_membership_requests]': 'false',
                'group[visibility_level]': g_everyone,
                'group[members_visibility_level]': m_members,
            },
            (Mailman.ROSTER_ADMINS, 'public'): {
                'group[public_admission]': 'true',
                'group[allow_membership_requests]': 'false',
                'group[visibility_level]': g_owners_and_members,
                'group[members_visibility_level]': m_group_owners_and_staff,
            },
            (Mailman.ROSTER_PUBLIC, 'moderate'): {
                'group[public_admission]': 'false',
                'group[allow_membership_requests]': 'true',
                'group[visibility_level]': g_everyone,
                'group[members_visibility_level]': m_everyone,
            },
            (Mailman.ROSTER_MEMBERS, 'moderate'): {
                'group[public_admission]': 'false',
                'group[allow_membership_requests]': 'true',
                'group[visibility_level]': g_everyone,
                'group[members_visibility_level]': m_members,
            },
            (Mailman.ROSTER_ADMINS, 'moderate'): {
                'group[public_admission]': 'false',
                'group[allow_membership_requests]': 'false',
                'group[visibility_level]': g_owners_and_members,
                'group[members_visibility_level]': m_group_owners_and_staff,
            },
        }
        kwargs = converter[(private_roster, policy)]
        kwargs['group[full_name]'] = self.category2members_group(self.name_get())
        return kwargs

    def settings(self):
        kwargs = {
            'disallow_reply_by_email_after_days': '0',
            'block_auto_generated_emails': 'false',
            'automatically_download_gravatars': 'false',
            'body_min_entropy': '0',
            'title_min_entropy': '0',
            'allow_uppercase_posts': 'true',
            'title_prettify': 'false',
            'allow_user_locale': 'true',
            'email_in': 'true',
            'log_mail_processing_failures': 'true',
            'download_remote_images_to_local': 'true',
            'min_post_length': '1',
            'min_first_post_length': '1',
            'min_title_similar_length': '10240',
            'disable_system_edit_notifications': 'true',
            'hide_user_profiles_from_public': 'true',
            self.discourse.enable_category_group_moderation_setting(): 'true',
        }
        return self.discourse.settings_set(**kwargs)

    def importer(self):
        before = {
        }
        after = {
        }
        (before['settings'], after['settings']) = self.settings()
        (before['category'], _) = self.discourse.category_create(self.name_get())
        if len(self.mailman.info['description']) > 0:
            (before['category-info'], after['category-info']) = self.discourse.category_info_set(
                self.name_get(), self.mailman.info['description'])
        logger.info('Adding users')
        (before['members'], after['members']) = self.users_add()
        (before['banned'], after['banned']) = self.users_ban()
        logger.info('Populating the moderators group')
        (before['group-moderators'], _) = (
            self.discourse.group_create(self.group_moderators_name()))
        (before['group-moderators-list'], after['group-moderators-list']) = self.group_members_add(
            self.group_moderators_name(), self.moderators_get(), self.owners_get())
        #
        # The settings must be modified after members are added because some of them
        # can only be set if the group has at least one owner.
        #
        (_, after['group-moderators']) = self.discourse.group_create(
            self.group_moderators_name(), **self.group_moderators_settings())

        if self.moderation_get() != 'no' or self.archive_get() == 'private':
            logger.info('Populating the members group')
            (before['group-members'], _) = self.discourse.group_create(self.group_members_name())
            (before['group-members-list'],
             after['group-members-list']) = self.group_members_add(
                 self.group_members_name(), self.members_get(), self.owners_get())
            (_, after['group-members']) = self.discourse.group_create(
                self.group_members_name(), **self.group_members_settings())

        (_, after['category']) = self.discourse.category_set(
            self.name_get(), **self.category_settings())

        (before['preferences'], after['preferences']) = self.users_preferences(before['members'])
        (before['notifications'], after['notifications']) = self.users_notifications()

        return before, after

    def main(self):
        before, after = self.importer()
        print(DeepDiff(before, after).pretty())
        return 0
