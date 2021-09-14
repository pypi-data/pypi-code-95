from unittest.mock import patch, Mock

from django.test import TestCase

from ..models import EveCharacter, EveCorporationInfo, EveAllianceInfo
from ..tasks import (
    update_alliance,
    update_corp,
    update_character,
    run_model_update
)


class TestTasks(TestCase):

    @patch('allianceauth.eveonline.tasks.EveCorporationInfo')
    def test_update_corp(self, mock_EveCorporationInfo):
        update_corp(42)
        self.assertEqual(
            mock_EveCorporationInfo.objects.update_corporation.call_count, 1
        )
        self.assertEqual(
            mock_EveCorporationInfo.objects.update_corporation.call_args[0][0], 42
        )

    @patch('allianceauth.eveonline.tasks.EveAllianceInfo')
    def test_update_alliance(self, mock_EveAllianceInfo):
        update_alliance(42)
        self.assertEqual(
            mock_EveAllianceInfo.objects.update_alliance.call_args[0][0], 42
        )
        self.assertEqual(
            mock_EveAllianceInfo.objects
            .update_alliance.return_value.populate_alliance.call_count, 1
        )

    @patch('allianceauth.eveonline.tasks.EveCharacter')
    def test_update_character(self, mock_EveCharacter):
        update_character(42)
        self.assertEqual(
            mock_EveCharacter.objects.update_character.call_count, 1
        )
        self.assertEqual(
            mock_EveCharacter.objects.update_character.call_args[0][0], 42
        )


@patch('allianceauth.eveonline.tasks.update_character')
@patch('allianceauth.eveonline.tasks.update_alliance')
@patch('allianceauth.eveonline.tasks.update_corp')
@patch('allianceauth.eveonline.providers.provider')
@patch('allianceauth.eveonline.tasks.CHUNK_SIZE', 2)
class TestRunModelUpdate(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        EveCorporationInfo.objects.all().delete()
        EveAllianceInfo.objects.all().delete()
        EveCharacter.objects.all().delete()

        EveCorporationInfo.objects.create(
            corporation_id=2345,
            corporation_name='corp.name',
            corporation_ticker='c.c.t',
            member_count=10,
            alliance=None,
        )
        EveAllianceInfo.objects.create(
            alliance_id=3456,
            alliance_name='alliance.name',
            alliance_ticker='a.t',
            executor_corp_id=5,
        )
        EveCharacter.objects.create(
            character_id=1,
            character_name='character.name1',
            corporation_id=2345,
            corporation_name='character.corp.name',
            corporation_ticker='c.c.t',  # max 5 chars
            alliance_id=None
        )
        EveCharacter.objects.create(
            character_id=2,
            character_name='character.name2',
            corporation_id=9876,
            corporation_name='character.corp.name',
            corporation_ticker='c.c.t',  # max 5 chars
            alliance_id=3456,
            alliance_name='character.alliance.name',
        )
        EveCharacter.objects.create(
            character_id=3,
            character_name='character.name3',
            corporation_id=9876,
            corporation_name='character.corp.name',
            corporation_ticker='c.c.t',  # max 5 chars
            alliance_id=3456,
            alliance_name='character.alliance.name',
        )
        EveCharacter.objects.create(
            character_id=4,
            character_name='character.name4',
            corporation_id=9876,
            corporation_name='character.corp.name',
            corporation_ticker='c.c.t',  # max 5 chars
            alliance_id=3456,
            alliance_name='character.alliance.name',
        )
        """
        EveCharacter.objects.create(
            character_id=5,
            character_name='character.name5',
            corporation_id=9876,
            corporation_name='character.corp.name',
            corporation_ticker='c.c.t',  # max 5 chars
            alliance_id=3456,
            alliance_name='character.alliance.name',
        )
        """

    def setUp(self):
        self.affiliations = [
            {'character_id': 1, 'corporation_id': 5},
            {'character_id': 2, 'corporation_id': 9876, 'alliance_id': 3456},
            {'character_id': 3, 'corporation_id': 9876, 'alliance_id': 7456},
            {'character_id': 4, 'corporation_id': 9876, 'alliance_id': 3456}
        ]
        self.names = [
            {'id': 1, 'name': 'character.name1'},
            {'id': 2, 'name': 'character.name2'},
            {'id': 3, 'name': 'character.name3'},
            {'id': 4, 'name': 'character.name4_new'}
        ]

    def test_normal_run(
        self,
        mock_provider,
        mock_update_corp,
        mock_update_alliance,
        mock_update_character,
    ):
        def get_affiliations(characters: list):
            response = [x for x in self.affiliations if x['character_id'] in characters]
            mock_operator = Mock(**{'result.return_value': response})
            return mock_operator

        def get_names(ids: list):
            response = [x for x in self.names if x['id'] in ids]
            mock_operator = Mock(**{'result.return_value': response})
            return mock_operator

        mock_provider.client.Character.post_characters_affiliation.side_effect \
            = get_affiliations

        mock_provider.client.Universe.post_universe_names.side_effect = get_names

        run_model_update()

        self.assertEqual(
            mock_provider.client.Character.post_characters_affiliation.call_count, 2
        )
        self.assertEqual(
            mock_provider.client.Universe.post_universe_names.call_count, 2
        )

        # character 1 has changed corp
        # character 2 no change
        # character 3 has changed alliance
        # character 4 has changed name
        self.assertEqual(mock_update_corp.apply_async.call_count, 1)
        self.assertEqual(
            int(mock_update_corp.apply_async.call_args[1]['args'][0]), 2345
        )
        self.assertEqual(mock_update_alliance.apply_async.call_count, 1)
        self.assertEqual(
            int(mock_update_alliance.apply_async.call_args[1]['args'][0]), 3456
        )
        characters_updated = {
            x[1]['args'][0] for x in mock_update_character.apply_async.call_args_list
        }
        excepted = {1, 3, 4}
        self.assertSetEqual(characters_updated, excepted)

    def test_ignore_character_not_in_affiliations(
        self,
        mock_provider,
        mock_update_corp,
        mock_update_alliance,
        mock_update_character,
    ):
        def get_affiliations(characters: list):
            response = [x for x in self.affiliations if x['character_id'] in characters]
            mock_operator = Mock(**{'result.return_value': response})
            return mock_operator

        def get_names(ids: list):
            response = [x for x in self.names if x['id'] in ids]
            mock_operator = Mock(**{'result.return_value': response})
            return mock_operator

        del self.affiliations[0]

        mock_provider.client.Character.post_characters_affiliation.side_effect \
            = get_affiliations

        mock_provider.client.Universe.post_universe_names.side_effect = get_names

        run_model_update()
        characters_updated = {
            x[1]['args'][0] for x in mock_update_character.apply_async.call_args_list
        }
        excepted = {3, 4}
        self.assertSetEqual(characters_updated, excepted)

    def test_ignore_character_not_in_names(
        self,
        mock_provider,
        mock_update_corp,
        mock_update_alliance,
        mock_update_character,
    ):
        def get_affiliations(characters: list):
            response = [x for x in self.affiliations if x['character_id'] in characters]
            mock_operator = Mock(**{'result.return_value': response})
            return mock_operator

        def get_names(ids: list):
            response = [x for x in self.names if x['id'] in ids]
            mock_operator = Mock(**{'result.return_value': response})
            return mock_operator

        del self.names[3]

        mock_provider.client.Character.post_characters_affiliation.side_effect \
            = get_affiliations

        mock_provider.client.Universe.post_universe_names.side_effect = get_names

        run_model_update()
        characters_updated = {
            x[1]['args'][0] for x in mock_update_character.apply_async.call_args_list
        }
        excepted = {1, 3}
        self.assertSetEqual(characters_updated, excepted)
