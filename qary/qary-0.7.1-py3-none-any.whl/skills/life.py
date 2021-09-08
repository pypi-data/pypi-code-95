""" Rule-based chatbot (FSM) for administering adaptive quizzes """
import logging
import os

from qary.constants import DATA_DIR
from qary.skills.base import ContextBaseSkill
from qary.etl.dialog import TurnsPreparation, compose_statement, load_dialog_turns
from qary.etl.intents import Intents
from qary.conversation.understanders import check_match
from qary.etl.dialog import get_nxt_cndn_match_mthd_dict

# FIXME: make this a config option and dont default to a test file
DEFAULT_QUIZ = os.path.join(DATA_DIR, 'life_coach/burns-cognitive-distortion-emotion-journal.v2.dialog.yml')
DIALOG_TREE_END_STATE_NAMES = (None, False, 0, '', ''.encode(), '0', 'none', 'None')
DIALOG_TREE_END_BOT_STATEMENTS = (None, 'none', )

WELCOME_STATE_NAME = '__WELCOME__'
FINISH_STATE_NAME = '__FINISH__'
DEFAULT_STATE_NAME = '__default__'
DEFAULT_BOT_USERNAME = 'bot'
EXIT_STATE_NAME = None
EXIT_BOT_STATEMENTS = ['Session is already over! Type "quit" to exit or press "Enter" for a new session']
EXIT_STATE_TURN_DICT = {'state': EXIT_STATE_NAME, DEFAULT_BOT_USERNAME: EXIT_BOT_STATEMENTS}


log = logging.getLogger(__name__)


class Skill(ContextBaseSkill):
    r"""Skill for Quiz"""

    def __init__(self, datafile=DEFAULT_QUIZ, turns_list=None, use_nlp=False):
        """ If datafile is not given, the turns list of dicts can directly be passed to seed the data
        """
        super().__init__()
        self.fuzzy_intents = Intents()
        self.datafile = datafile
        self.turns = {}
        self.use_nlp = use_nlp
        # if turns is passed, then you should not set the datafile
        if turns_list:
            self.turns_input = turns_list
        else:
            self.turns_input = load_dialog_turns(datafile)
        if self.turns_input:
            # Do more complex operations using the helper '_TurnsPreparation' class
            turns_preparation = TurnsPreparation(turns_list=self.turns_input, use_nlp=self.use_nlp)
            self.turns = turns_preparation.prepare_turns()
        else:  # some sort of error
            log.error('An empty turns_list and/or datafile was passed to quiz.Skill.__init__()')
        self.state = ''  # State names must be strings
        self.current_turn = {}  # None or empty dict used to indicate start of quiz that bot says something first?
        return

    def reply(self, statement, context=None):
        r"""Except for the welcome state, all other states are mere recordings of the quiz responses
        """
        responses = super().reply(statement, context=context)
        statement = str(statement)
        if statement in DIALOG_TREE_END_BOT_STATEMENTS:
            statement = None

        # First check to see if we are in the time before the welcome state
        if self.state in DIALOG_TREE_END_STATE_NAMES:
            # First figure out the welcome state name using a magical special WELCOME_STATE_NAME string
            # as the key. This will allow you to access the actual welcome turn
            self.state = self.turns[WELCOME_STATE_NAME]
            # print(self.state)
            self.current_turn = self.state
            response_text = compose_statement(self.current_turn['bot'])
        else:
            nxt_cndn = self.current_turn['next_condition']
            context
            nxt_cndn_match_mthd_dict = get_nxt_cndn_match_mthd_dict(nxt_cndn)
            # for match_method_keyword in ['EXACT', '']
            match_found = False
            for next_state_option in nxt_cndn_match_mthd_dict['EXACT']:
                match_found = check_match(statement, next_state_option, 'EXACT')
                if match_found:
                    break
            if not match_found:
                for next_state_option in nxt_cndn_match_mthd_dict['LOWER']:
                    match_found = check_match(statement, next_state_option, 'LOWER')
                    if match_found:
                        break
            if not match_found:
                for next_state_option in nxt_cndn_match_mthd_dict['CASE_SENSITIVE_KEYWORD']:
                    match_found = check_match(
                        statement, next_state_option, 'CASE_SENSITIVE_KEYWORD'
                    )
                    if match_found:
                        break
            if not match_found:
                for next_state_option in nxt_cndn_match_mthd_dict['KEYWORD']:
                    match_found = check_match(statement, next_state_option, 'KEYWORD')
                    if match_found:
                        break
            if not match_found:
                for next_state_option in nxt_cndn_match_mthd_dict['NORMALIZE']:
                    match_found = check_match(statement, next_state_option, 'NORMALIZE')
                    if match_found:
                        break
            if not match_found:
                for next_state_option in nxt_cndn_match_mthd_dict['FUZZY_KEYWORD']:
                    match_found = check_match(statement, next_state_option, 'FUZZY_KEYWORD')
                    if match_found:
                        break
            if not match_found:
                self.state = nxt_cndn_match_mthd_dict[None][0][1]
            self.current_turn = self.turns.get(self.state, EXIT_STATE_TURN_DICT)
            response_text = compose_statement(self.current_turn.get(DEFAULT_BOT_USERNAME, EXIT_BOT_STATEMENTS))

        return responses + [(1.0, response_text)]
