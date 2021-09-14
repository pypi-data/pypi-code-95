from unittest import mock

from django.contrib.auth.models import User, Group
from django.test import TestCase

from allianceauth.tests.auth_utils import AuthUtils
from allianceauth.eveonline.models import (
    EveCorporationInfo, EveAllianceInfo, EveCharacter
)

from ..models import GroupRequest, RequestLog


def create_testdata():    
    # clear DB
    User.objects.all().delete()
    Group.objects.all().delete()
    EveCharacter.objects.all().delete()
    EveCorporationInfo.objects.all().delete()
    EveAllianceInfo.objects.all().delete()

    # group 1
    group = Group.objects.create(name='Superheros')        
    group.authgroup.description = 'Default Group'
    group.authgroup.internal = False
    group.authgroup.hidden = False
    group.authgroup.save()
    
    # user 1        
    user_1 = AuthUtils.create_user('Bruce Wayne')
    AuthUtils.add_main_character_2(
        user_1,
        name='Bruce Wayne',
        character_id=1001,
        corp_id=2001,
        corp_name='Wayne Technologies'
    )        
    user_1.groups.add(group)
    group.authgroup.group_leaders.add(user_1)

    # user 2
    user_2 = AuthUtils.create_user('Clark Kent')
    AuthUtils.add_main_character_2(
        user_2,
        name='Clark Kent',
        character_id=1002,
        corp_id=2002,
        corp_name='Wayne Technologies'
    )            
    return group, user_1, user_2



class TestGroupRequest(TestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group, cls.user_1, _ = create_testdata()

    def test_main_char(self):
        group_request = GroupRequest.objects.create(
            status='Pending',
            user=self.user_1,
            group=self.group
        )
        expected = self.user_1.profile.main_character
        self.assertEqual(group_request.main_char, expected)

    def test_str(self):
        group_request = GroupRequest.objects.create(
            status='Pending',
            user=self.user_1,
            group=self.group
        )
        expected = 'Bruce Wayne:Superheros'
        self.assertEqual(str(group_request), expected)


class TestRequestLog(TestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group, cls.user_1, cls.user_2 = create_testdata()

    def test_requestor(self):
        request_log = RequestLog.objects.create(
            group=self.group,
            request_info='Clark Kent:Superheros',
            request_actor=self.user_1
        )
        expected = 'Clark Kent'
        self.assertEqual(request_log.requestor(), expected)

    def test_type_to_str_removed(self):
        request_log = RequestLog.objects.create(
            request_type=None,
            group=self.group,
            request_info='Clark Kent:Superheros',
            request_actor=self.user_1
        )
        expected = 'Removed'
        self.assertEqual(request_log.type_to_str(), expected)

    def test_type_to_str_leave(self):
        request_log = RequestLog.objects.create(
            request_type=True,
            group=self.group,
            request_info='Clark Kent:Superheros',
            request_actor=self.user_1
        )
        expected = 'Leave'
        self.assertEqual(request_log.type_to_str(), expected)

    def test_type_to_str_join(self):
        request_log = RequestLog.objects.create(
            request_type=False,
            group=self.group,
            request_info='Clark Kent:Superheros',
            request_actor=self.user_1
        )
        expected = 'Join'
        self.assertEqual(request_log.type_to_str(), expected)

    def test_action_to_str_accept(self):
        request_log = RequestLog.objects.create(            
            group=self.group,
            request_info='Clark Kent:Superheros',
            request_actor=self.user_1,
            action = True
        )
        expected = 'Accept'
        self.assertEqual(request_log.action_to_str(), expected)

    def test_action_to_str_reject(self):
        request_log = RequestLog.objects.create(            
            group=self.group,
            request_info='Clark Kent:Superheros',
            request_actor=self.user_1,
            action = False
        )
        expected = 'Reject'
        self.assertEqual(request_log.action_to_str(), expected)

    def test_req_char(self):
        request_log = RequestLog.objects.create(            
            group=self.group,
            request_info='Clark Kent:Superheros',
            request_actor=self.user_1,
            action = False
        )
        expected = self.user_2.profile.main_character
        self.assertEqual(request_log.req_char(), expected)


class TestAuthGroup(TestCase):

    def test_str(self):
        group = Group.objects.create(name='Superheros')        
        group.authgroup.description = 'Default Group'
        group.authgroup.internal = False
        group.authgroup.hidden = False
        group.authgroup.save()

        expected = 'Superheros'
        self.assertEqual(str(group.authgroup), expected)
