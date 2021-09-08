""" Common classes for card play."""
import random

from typing import List, Dict, Union, Tuple

from bridgeobjects import SUITS, Card, Suit, SEATS, CARD_NAMES
from bfgsupport import Board
from .cardplayer import Player

DEFAULT_SCORE = 1
PARTNERS_SUIT_SCORE = 5
TENACE_SCORE = 3
STRENGTH_SCORE = 2
TRUMP_SCORE = 2
FROZEN_SUIT_SCORE = 5
LENGTH_SCORE = 1
RUFF_AND_DISCARD_SCORE = 5
VOID_SCORE = 1000
DRAW_TRUMPS_SCORE = 20

class FirstSeat():
    """General routines for First Seat."""


    def __init__(self):
        pass

    @staticmethod
    def _deprecate_suits(player: Player) -> List[Tuple[str, int]]:
        """Assign score to suits based on void."""
        suit_scores = {suit_name: 0 for suit_name, suit in SUITS.items()}
        for suit in SUITS:
            if not player.suit_cards[suit]:
                suit_scores[suit] -= VOID_SCORE
        return [(suit_name, score) for suit_name, score in suit_scores.items()]

    @staticmethod
    def _partners_suit(player: Player) -> List[Tuple[str, int]]:
        """Assign score to suits based on it being suit partner led."""
        suit_scores = {suit_name: 0 for suit_name, suit in SUITS.items()}
        partners_suit = FirstSeat._get_partners_suit(player)
        if partners_suit and not partners_suit == player.trump_suit:
            suit_scores[partners_suit.name] += PARTNERS_SUIT_SCORE
        return [(suit_name, score) for suit_name, score in suit_scores.items()]

    @staticmethod
    def _tenace_check(player: Player) -> List[Tuple[str, int]]:
        """Assign score to suits based on tenaces in dummy."""
        suit_scores = {suit_name: 0 for suit_name, suit in SUITS.items()}
        dummy_tenaces = FirstSeat._identify_tenace(player)
        for suit in dummy_tenaces:
            if player.dummy_on_left:
                # Lead through tenaces
                suit_scores[suit] += TENACE_SCORE
            elif player.dummy_on_right:
                # Lead to tenaces
                suit_scores[suit] -= TENACE_SCORE
        return [(suit_name, score) for suit_name, score in suit_scores.items()]

    @staticmethod
    def _lead_through_strength(player: Player) -> List[Tuple[str, int]]:
        """Assign score to suits where you lead through or to strength."""
        suit_scores = {suit_name: 0 for suit_name, suit in SUITS.items()}
        if player.dummy_on_left:
            for suit, points in player.dummy_suit_strength.items():
                if points >= 5:
                    suit_scores[suit] += STRENGTH_SCORE
        elif player.dummy_on_right:
            for suit, points in player.dummy_suit_strength.items():
                if not player.trump_suit:
                    if points <= 2:
                        suit_scores[suit] += STRENGTH_SCORE
                else:
                    if suit != player.trump_suit.name:
                        if points <= 2:
                            suit_scores[suit] += STRENGTH_SCORE
        return [(suit_name, score) for suit_name, score in suit_scores.items()]

    @staticmethod
    def _frozen_suits(player: Player) -> List[Tuple[str, int]]:
        """Assign score to suits based on frozen suits."""
        suit_scores = {suit_name: 0 for suit_name, suit in SUITS.items()}
        frozen_suits = []
        for suit, cards in player.dummy_suit_cards.items():
            dummy_honours = 0
            hand_honours = 0
            for card in cards:
                if card.is_honour:
                    dummy_honours += 1
            if dummy_honours == 1:
                suit_cards = player.suit_cards[suit]
                for card in suit_cards:
                    if card.is_honour:
                        hand_honours += 1
            if dummy_honours ==1 and hand_honours == 1:
                frozen_suits.append(suit)
        for suit in frozen_suits:
            suit_scores[suit] -= FROZEN_SUIT_SCORE
        return [(suit_name, score) for suit_name, score in suit_scores.items()]

    @staticmethod
    def _long_suits(player: Player) -> List[Tuple[str, int]]:
        """Assign score to suits based on length (long)."""
        suit_scores = {suit_name: 0 for suit_name, suit in SUITS.items()}
        for suit in SUITS:
            number_cards = len(player.suit_cards[suit]) - 4
            if number_cards > 0:
                suit_scores[suit] = number_cards * LENGTH_SCORE
        return [(suit_name, score) for suit_name, score in suit_scores.items()]

    @staticmethod
    def _short_suits(player: Player) -> List[Tuple[str, int]]:
        """Assign score to suits based on length (short)."""
        suit_scores = {suit_name: 0 for suit_name, suit in SUITS.items()}
        if len(player.trump_cards) > 0:
            for suit in SUITS:
                number_cards = len(player.suit_cards[suit])
                if 0 < number_cards < 3:
                    suit_scores[suit] = (2 - number_cards) * LENGTH_SCORE
        return [(suit_name, score) for suit_name, score in suit_scores.items()]

    @staticmethod
    def _ruff_and_discard(player: Player) -> List[Tuple[str, int]]:
        """Assign score to suits based on potential for ruff and discard."""
        suit_scores = {suit_name: 0 for suit_name, suit in SUITS.items()}
        if len(player.dummy_suit_cards[player.trump_suit.name]) > 0:
            for suit in SUITS:
                if len(player.dummy_suit_cards[suit]) == 0:
                    suit_scores[suit] -= RUFF_AND_DISCARD_SCORE
        return [(suit_name, score) for suit_name, score in suit_scores.items()]

    @staticmethod
    def _get_partners_suit(player: Player) -> Union[Suit, None]:
        """Return partner's suit if this is 3rd hand on first lead."""
        trick_one = player.board.tricks[0]
        if trick_one.leader == player.partner_seat:
            opening_lead = trick_one.cards[0]
            if opening_lead.suit != player.trump_suit:
                if opening_lead.value < 7 and player.suit_cards[opening_lead.suit]:
                    return opening_lead.suit
        return None

    @staticmethod
    def _identify_tenace(player: Player) -> List[Suit]:
        """Return a list of suits with a tenace in dummy."""
        suits = []
        for suit, tenace in player.dummy_suit_tenaces.items():
            if player.suit_cards[suit]:
                if tenace and (player.trump_suit and not suit == player.trump_suit.name):
                    tenace_index = CARD_NAMES.index(tenace.name)
                    next_card_name = CARD_NAMES[tenace_index+1]
                    if Card(next_card_name) not in player.cards:
                        suits.append(suit)
        return suits

    @staticmethod
    def _best_suit(player: Player, score_reasons: Dict[str, int]) -> Suit:
        """Return the best suit based on score."""
        suit_scores = {suit_name: 0 for suit_name, suit in SUITS.items()}
        for reason, suits in score_reasons.items():
            # print(f'1st seat {reason[:8]:<8}', suits)
            for suit in suits:
                suit_scores[suit[0]] += suit[1]
        # print(f'{player.seat=}{suit_scores=}')

        max_score = 0
        for suit, score in suit_scores.items():
            if score > max_score:
                max_score = score
        candidate_suits = []
        for suit, score in suit_scores.items():
            if score == max_score:
                candidate_suits.append(suit)
        if not candidate_suits:
            return player.best_suit
        return Suit(random.choice(candidate_suits))
