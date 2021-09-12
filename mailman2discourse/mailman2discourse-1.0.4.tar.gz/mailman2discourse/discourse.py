import copy
import hashlib
import logging
import os
from packaging import version
import requests
from requests.exceptions import HTTPError
from mailman2discourse.retry import retry

logger = logging.getLogger(__name__)


class DiscourseError(HTTPError):
    pass


class DiscourseClientError(DiscourseError):
    pass


class DiscourseClientNotFound(DiscourseError):
    pass


class DiscourseClientForbidden(DiscourseError):
    pass


DELETE = "DELETE"
GET = "GET"
POST = "POST"
PUT = "PUT"


class DiscourseClient(object):

    def __init__(self, host, api_username, api_key):
        self.host = host
        self.api_username = api_username
        self.api_key = api_key

    def _get(self, path, **kwargs):
        return self._request(GET, path, params=kwargs)

    def _put(self, path, **kwargs):
        return self._request(PUT, path, data=kwargs)

    def _post(self, path, files=None, **kwargs):
        return self._request(POST, path, files=files, params=kwargs)

    def _delete(self, path, **kwargs):
        return self._request(DELETE, path, params=kwargs)

    def _request(
        self, verb, path, params=None, files=None, data=None
    ):
        url = self.host + path

        headers = {
            "Accept": "application/json; charset=utf-8",
            "Api-Key": self.api_key,
            "Api-Username": self.api_username,
            "Discourse-Present": "true",
        }

        request_kwargs = dict(
            allow_redirects=False,
            params=params,
            files=files,
            data=data,
            headers=headers,
        )

        request_message = f"request {verb} {url} params={params} data={data}"
        logger.debug(request_message)
        response = requests.request(verb, url, **request_kwargs)
        logger.debug(f"response {response.status_code}: {repr(response.text[:400])}")

        if response.status_code == 404:
            raise DiscourseClientNotFound(request_message)
        elif response.status_code == 403:
            raise DiscourseClientForbidden(request_message)
        response.raise_for_status()

        if not response.content.strip():
            return None

        json_content = "application/json; charset=utf-8"
        content_type = response.headers["content-type"]
        if content_type != json_content:
            raise DiscourseError(
                'Invalid Response, expecting "{0}" got "{1}"'.format(
                    json_content, content_type
                ),
                response=response,
            )

        try:
            decoded = response.json()
        except ValueError:
            raise DiscourseError("failed to decode response", response=response)

        if isinstance(decoded, dict) and "errors" in decoded:
            message = decoded.get("message")
            if not message:
                message = u",".join(decoded["errors"])
            raise DiscourseClientError(message, response=response)

        return decoded


class DiscourseErrorManyMembers(Exception):
    pass


class DiscourseErrorManyGroupMembers(Exception):
    pass


class DiscourseErrorMinVersion(Exception):
    pass


class DiscourseErrorCategoryFieldType(Exception):
    pass


class DiscourseErrorCategoryNotification(Exception):
    pass


class DiscourseErrorUserCreate(Exception):
    pass


class DiscourseErrorUserActive(Exception):
    pass


class DiscourseErrorUserTrustLevel(Exception):
    pass


class DiscourseErrorUserPreferences(Exception):
    pass


class DiscourseErrorGroupCreate(Exception):
    pass


class DiscourseErrorUserNotFound(Exception):
    pass


class Discourse(object):

    USERNAME_MIN_LENGTH = 3
    USERNAME_MAX_LENGTH = 20

    GROUP_PERMISSIONS_CREATE_REPLY_SEE = 1
    GROUP_PERMISSIONS_SEE = 3

    GROUP_MEMBERS_VISIBILITY_LEVEL_EVERYONE = '0'
    GROUP_MEMBERS_VISIBILITY_LEVEL_MEMBERS = '2'
    GROUP_MEMBERS_VISIBILITY_LEVEL_GROUP_OWNERS_AND_STAFF = '3'

    GROUP_VISIBILITY_LEVEL_EVERYONE = '0'
    GROUP_VISIBILITY_LEVEL_OWNERS_AND_MEMBERS = '2'

    CATEGORY_NOTIFICATION_LEVEL_WATCHING = '3'
    CATEGORY_NOTIFICATION_LEVEL_MUTED = '0'

    GROUP_NAME_LENGTH_MAX = 20

    MIN_VERSION = '2.5.5'

    def __init__(self, args):
        self.args = args

    def connect(self):
        self.d = DiscourseClient(
            self.args.url,
            api_username=self.args.api_user,
            api_key=f'{self.args.api_key}')
        self.about = self.d._get('/about.json')['about']
        logger.info(f'{self.args.url} discourse version {self.about["version"]}')
        return self

    def version_check(self):
        if version.parse(self.about["version"]) < version.parse(Discourse.MIN_VERSION):
            raise DiscourseErrorMinVersion(
                f'discourse is running {self.about["version"]} '
                f'but the minimum required version is {Discourse.MIN_VERSION}')
        return True

    def enable_category_group_moderation_setting(self):
        if version.parse(self.about["version"]) >= version.parse("2.5.9"):
            return 'enable_category_group_moderation'
        else:
            return 'enable_category_group_review'

    @staticmethod
    def value2str(v):
        if v is None:
            return ''
        elif v is True:
            return 'true'
        elif v is False:
            return 'false'
        elif isinstance(v, int):
            return str(v)
        else:
            return v

    @staticmethod
    def category_dict2params(d):
        p = {}
        for k, v in d.items():
            if k not in Discourse.category_fields():
                continue
            if isinstance(v, list):
                if k == 'group_permissions':
                    for v1 in v:
                        p[f'permissions[{v1["group_name"]}]'] = Discourse.value2str(
                            v1["permission_type"])
                else:
                    raise DiscourseErrorCategoryFieldType(
                        f'{k} is not expected to be an array in {d}')
            elif isinstance(v, dict):
                if k == 'custom_fields':
                    for k1, v1 in v.items():
                        p[f'{k}[{k1}]'] = Discourse.value2str(v1)
                else:
                    raise DiscourseErrorCategoryFieldType(
                        f'{k} is not expected to be a dict in {d}')
            else:
                p[k] = Discourse.value2str(v)
        return p

    @staticmethod
    def enforce_group_name_length(name):
        if len(name) > Discourse.GROUP_NAME_LENGTH_MAX:
            md5 = hashlib.md5(name.encode('utf-8')).hexdigest()
            name = 'g' + md5[:Discourse.GROUP_NAME_LENGTH_MAX - 1]
        return name

    @staticmethod
    def category_fields():
        return (
            'name',
            'id',
            'color',
            'text_color',
            'email_in_allow_strangers',
            'email_in',
            'group_permissions',
            'custom_fields',
            'reviewable_by_group_name',
            'notification_level',
            'topic_url',
            'post_count',
            'topic_count',
        )

    def category_slug(self, name):
        for category in self.d._get('/categories.json')['category_list']['categories']:
            if category['name'] == name:
                return category['slug']
        return None

    def category_get(self, name):
        slug = self.category_slug(name)
        if not slug:
            return None
        try:
            category = self.d._get(f'/c/{slug}/show.json')['category']
            return self.category_dict2params(category)
        except DiscourseClientNotFound:
            return None

    def category_create(self, name):
        category = self.category_get(name)
        if category:
            return category, category
        else:
            if self.args.dry_run:
                return None, {'name': name}
            else:
                kwargs = {
                    'name': name,
                    'color': 'BF1E2E',
                    'text_color': 'FFFFFF',
                    'allow_badges': 'false',
                    # see https://meta.discourse.org/t/79773/157
                    'custom_fields[import_id]': name,
                }
                category = self.d._post('/categories.json', **kwargs)['category']
                return None, self.category_dict2params(category)

    def category_delete(self, name):
        category = self.category_get(name)
        if category and not self.args.dry_run:
            self.d._delete(f'/categories/{category["id"]}')
        return category

    def category_info_get(self, name, post_id=None):
        if not post_id:
            category = self.category_get(name)
            topic_id = os.path.basename(category['topic_url'])
            topic = self.d._get(f'/t/{topic_id}.json')
            post_id = topic['post_stream']['posts'][0]['id']
        post = self.d._get(f'/posts/{post_id}.json')
        return post['raw'], post_id

    def category_info_set(self, name, target):
        before, post_id = self.category_info_get(name)
        if self.args.dry_run:
            return before, target
        self.d._put(f'/posts/{post_id}.json', **{'post[raw]': target})
        return before, self.category_info_get(name, post_id)[0]

    def category_set(self, name, **kwargs):
        before = self.category_get(name)
        target = copy.deepcopy(before)
        #
        # permissions[] obey a precedence algorithm that is non trivial.
        # If the category_set caller specifies permissions[], the existing permissions[*]
        # are discarded. Here is an example why:
        #
        # * the category is set with permissions[everyone] = 1
        # * the caller sets permissions[mygroup] = 1
        # * the CORRECT call is to put
        #
        #   permissions[mygroup] = 1
        #
        #   because it will implicitly discard permissions[everyone]
        #
        # * the INCORRECT call is to put
        #
        #   permissions[mygroup] = 1 and
        #   permissions[everyone] = 1
        #
        #   because permissions[everyone] has precedence and permissions[mygroup] will
        #   be discarded.
        #
        set_permissions = False
        for k in kwargs.keys():
            if k.startswith('permissions['):
                set_permissions = True
        if set_permissions:
            for k in [v for v in target.keys()]:
                if k.startswith('permissions['):
                    del target[k]
        target.update(kwargs)
        if self.args.dry_run:
            return before, target
        else:
            self.d._put(f'/categories/{before["id"]}', **target)
            return before, self.category_get(name)

    def category_notifications(self, email, name, level):
        user = self.user_get(email)
        api_username = self.d.api_username
        try:
            self.d.api_username = user['username'].lower()
            category = self.category_get(name)
            if self.args.dry_run:
                return category['notification_level'], level
            r = self.d._post(f'/category/{category["id"]}/notifications', notification_level=level)
            if not r['success']:
                raise DiscourseErrorCategoryNotification(
                    f'setting notification_level={level} '
                    f'for user {user["username"]} failed: {r["message"]}')
            return category['notification_level'], self.category_get(name)['notification_level']
        finally:
            self.d.api_username = api_username

    def settings_dict2params(self, settings):
        fields = self.settings_fields()
        return {
            s['setting']: s['value'] for s in settings
            if s['setting'] in fields
        }

    def settings_fields(self):
        return ('email_in',
                'log_mail_processing_failures',
                'download_remote_images_to_local',
                'min_post_length'
                'min_first_post_length',
                'min_title_similar_length',
                'disable_system_edit_notifications',
                'disable_emails',
                self.enable_category_group_moderation_setting())

    def settings_set(self, **kwargs):
        before = self.settings_get()
        if self.args.dry_run:
            target = copy.deepcopy(before)
            target.update(kwargs)
            return before, target
        for k, v in kwargs.items():
            self.d._put(f'/admin/site_settings/{k}', **{k: v})
        return before, self.settings_get()

    def settings_get(self):
        return self.settings_dict2params(self.d._get('/admin/site_settings')['site_settings'])

    @staticmethod
    def group_dict2params(group):
        params = {}
        fields = Discourse.group_fields()
        for k, v in group['group'].items():
            if k not in fields:
                continue
            params[f'group[{k}]'] = Discourse.value2str(v)
        return params

    @staticmethod
    def group_fields():
        return ('name',
                'full_name',
                'id',
                'public_exit',
                'members_visibility_level',
                'visibility_level',
                'allow_membership_requests',
                'public_admission')

    def group_get(self, name):
        try:
            group = self.d._get(f'/groups/{name}.json')
            return self.group_dict2params(group)
        except DiscourseClientNotFound:
            return None

    def group_create(self, name, **kwargs):
        before = self.group_get(name)
        if before:
            target = copy.deepcopy(before)
        else:
            target = {
                'group[name]': name,
            }
        target.update(kwargs)
        if self.args.dry_run or before == target:
            return before, target
        elif before is None:
            after = self.d._post('/admin/groups', **target)
            after['group'] = after.pop('basic_group')
            return before, self.group_dict2params(after)
        else:
            r = self.d._put(f'/groups/{before["group[id]"]}', **target)
            if not r['success']:
                raise DiscourseErrorGroupCreate(f'{target} failed {r["message"]}')
            return before, self.group_get(name)

    def group_delete(self, name):
        group = self.group_get(name)
        if group and not self.args.dry_run:
            self.d._delete(f'/admin/groups/{group["group[id]"]}')
        return group

    def group_member_fields(self):
        return ('id', 'username', 'owner')

    def group_member_get(self, name, email):
        members = self.d._get(f'/groups/{name}/members.json', filter=email)
        if len(members['members']) == 0:
            return None
        if len(members['members']) > 1:
            raise DiscourseErrorManyGroupMembers(
                f'expected only one member with {email} in group {name} and got {members}')
        if len(members['owners']) > 0:
            member = members['owners'][0]
            member['owner'] = True
        else:
            member = members['members'][0]
            member['owner'] = False
        member['email'] = email
        return {k: member[k] for k in self.group_member_fields()}

    def group_member_create(self, name, email, owner):
        before = self.group_member_get(name, email)

        if not before or self.args.dry_run:
            user = self.user_get(email)
            if not user:
                raise DiscourseErrorUserNotFound(f'{email} is not a know user')

        if self.args.dry_run:
            target = {'email': email, 'username': user['username'], 'owner': owner}
            if before:
                return before, target
            else:
                return None, target

        if not before:
            group_id = self.group_get(name)['group[id]']
            if owner:
                endpoint = f'/admin/groups/{group_id}/owners.json'
                kwargs = {'group[usernames]': user['username']}
            else:
                endpoint = f'/groups/{group_id}/members.json'
                kwargs = {'usernames': user['username']}
            self.d._put(endpoint, **kwargs)
            return None, self.group_member_get(name, email)
        if before['owner'] != owner:
            group_id = self.group_get(name)['group[id]']
            endpoint = f'/admin/groups/{group_id}/owners.json'
            if owner:
                kwargs = {
                    'group[usernames]': before['username'],
                }
                self.d._put(endpoint, **kwargs)
            else:
                self.d._delete(endpoint, user_id=before['id'])
            after = copy.deepcopy(before)
            after['owner'] = owner
            return before, after
        return before, before

    def group_member_delete(self, name, email):
        member = self.group_member_get(name, email)
        if member and not self.args.dry_run:
            group = self.group_get(name)
            self.d._delete(f'/groups/{group["group[id]"]}/members.json', user_id=member['id'])
        return member

    @staticmethod
    def user_dict2params(user):
        return {k: Discourse.value2str(v) for k, v in user.items() if k in Discourse.user_fields()}

    @staticmethod
    def user_fields():
        return ('username', 'name', 'id', 'email', 'active', 'trust_level')

    def user_username_exists(self, username):
        try:
            user = self.d._get(f'/users/{username}.json')
            return self.user_dict2params(user['user'])
        except DiscourseClientNotFound:
            return None

    def user_get(self, email):
        email = email.lower()
        users = self.d._get('/admin/users/list/active.json', filter=email, show_emails='true')
        for user in users:
            if user['email'] == email:
                return self.user_dict2params(user)
        return None

    def user_create(self, email, **kwargs):
        before = self.user_get(email)
        if before:
            target = copy.deepcopy(before)
        else:
            target = {'email': email}
        target.update(kwargs)
        if self.args.dry_run or before == target:
            return before, target
        elif before is None:
            r = self.d._post('/users', **target)
            if r['success']:
                after = self.user_get(email)
            else:
                raise DiscourseErrorUserCreate(f'{target} failed {r["message"]}')
        else:
            self.d._put(f'/u/{before["username"]}', **target)
            after = self.user_get(email)
            if after['active'] != target['active']:
                _, after = self.user_active(email, target['active'])
        if 'trust_level' in target and after['trust_level'] != target['trust_level']:
            _, after = self.user_trust_level(email, target['trust_level'])
        return before, after

    def user_active(self, email, active):
        before = self.user_get(email)
        if before['active'] == active:
            return before, before
        if self.args.dry_run:
            after = copy.deepcopy(before)
            after['active'] = active
            return before, after
        if active == 'true':
            action = 'activate'
        elif active == 'false':
            action = 'deactivate'
        else:
            raise DiscourseErrorUserActive(
                f'active={active} invalid, it must be "true" or "false"')
        r = self.d._put(f'/admin/users/{before["id"]}/{action}')
        if r['success']:
            return before, self.user_get(email)
        else:
            raise DiscourseErrorUserActive(f'active={active} failed {r["message"]}')

    def user_trust_level(self, email, trust_level):
        before = self.user_get(email)
        if before['trust_level'] == trust_level:
            return before, before
        if self.args.dry_run:
            after = copy.deepcopy(before)
            after['trust_level'] = trust_level
            return before, after
        self.d._put(f'/admin/users/{before["id"]}/trust_level', level=trust_level)
        after = self.user_get(email)
        if after['trust_level'] != trust_level:
            raise DiscourseErrorUserTrustLevel(
                f'failed to change trust_level from {before["trust_level"]} to {trust_level}: '
                f'it is now {after["trust_level"]}')
        return before, after

    def user_delete(self, email, **data):
        user = self.user_get(email)
        if user and not self.args.dry_run:
            self.d._delete(f'/admin/users/{user["id"]}', delete_posts=True, **data)
        return user

    @staticmethod
    def user_preferences_dict2params(user):
        params = {}
        for k, v in user.items():
            if k == 'user_option':
                params.update(Discourse.user_preferences_dict2params(v))
            elif k in Discourse.user_preferences_fields():
                params[k] = Discourse.value2str(v)
        return params

    @staticmethod
    def user_preferences_fields():
        return ('username', 'hide_profile_and_presence', 'locale')

    def user_preferences_get(self, email):
        user = self.user_get(email)
        preferences = self.d._get(f'/u/{user["username"]}.json')
        return self.user_preferences_dict2params(preferences['user'])

    def user_preferences_set(self, email, **kwargs):
        before = self.user_preferences_get(email)
        target = copy.deepcopy(before)
        target.update(kwargs)
        if self.args.dry_run:
            return before, target
        else:
            r = self.d._put(f'/u/{before["username"]}.json', **target)
            if r['success']:
                return before, self.user_preferences_get(email)
            else:
                raise DiscourseErrorUserPreferences(f'{target} failed {r["message"]}')

    def topic_post(self, name, title, message):
        category = self.category_get(name)
        kwargs = {
            'category': str(category['id']),
            'title': title,
            'raw': message,
            'unlist_topic': "false",
            'archetype': "regular",
        }
        return self.d._post('/posts', **kwargs)

    def topic_delete(self, id):
        self.d._delete(f'/t/{id}')

    def message_load(self, raw, msg):
        #
        # There is no convenient way to reverse engineer the /admin/email/handle_mail endpoint
        #
        # https://github.com/discourse/discourse/blob/427d54b2b00fa94474c0522eaed750452c4e7f43/app/controllers/admin/email_controller.rb#L145-L159
        # Which is run by app/jobs/regular/process_email.rb calling Email::Processor.process!
        # Which calls lib/email/processor.rb Email::Receiver.new
        # Which calls lib/email/receiver.rb
        #
        # Errors when processing the queue are found in http://forum.example.com/logs/
        #
        data = {
            'email': raw,
            'api_key': self.d.api_key,
            'api_username': self.d.api_username,
        }
        r = requests.post(f'{self.d.host}/admin/email/handle_mail',
                          allow_redirects=False,
                          data=data)
        logger.debug(r.text)
        r.raise_for_status()
        return r

    def category_topics_delete(self, category_name):
        category = self.category_get(category_name)
        topics = self.d._get(f'/c/{category_name}/{category["id"]}.json')['topic_list']['topics']
        about_id = os.path.basename(category['topic_url'])
        for topic in topics:
            if str(topic['id']) == about_id:
                continue
            self.topic_delete(topic['id'])

    @retry(AssertionError, tries=5)
    def topic_wait(self, category_name, subject):
        topic = self.topic_get(category_name, subject)
        assert topic, f'no topics {subject} in category {category_name}'
        return topic

    def topic_get(self, category_name, subject):
        category = self.category_get(category_name)
        if category is None:
            return None
        kwargs = {
            'term': subject,
            'search_context[type]': 'category',
            'search_context[id]': category["id"],
        }
        r = self.d._get('/search/query', **kwargs)
        if 'topics' not in r:
            return None
        for topic in r['topics']:
            if topic['title'].lower() == subject.lower():
                return topic
        return None

    @retry(AssertionError, tries=5)
    def review_wait(self, subject):
        reviewable = self.reviewable_get(subject)
        assert reviewable, f'{subject} not found in /review'

    def reviewable_get(self, subject):
        reviewables = self.d._get('/review.json')['reviewables']
        for reviewable in reviewables:
            if reviewable['payload']['title'] == subject:
                return reviewable
        return None

    def review_approve(self, title):
        reviewable = self.reviewable_get(title)
        r = self.d._put(f'/review/{reviewable["id"]}/perform/approve_post', version=0)
        r = r['reviewable_perform_result']
        assert r['success']
        return r['created_post_topic_id']

    def disconnect(self):
        del self.d

    def emails_screened(self):
        return self.d._get('/admin/logs/screened_emails.json')

    def emails_allow(self, email):
        for e in self.emails_screened():
            if e["email"] == email:
                self.d._delete(f'/admin/logs/screened_emails/{e["id"]}')
                return True
        return False

    def emails_check(self, email):
        try:
            self.d._get('/u/check_email', email=email)
            return True
        except DiscourseClientError:
            return False
