""" First seat card play."""

import logging
log = logging.getLogger(__name__)

from typing import List, Dict, Union, Tuple
import random
from termcolor import colored

from bridgeobjects import SUITS, Card, Suit, SEATS, CARD_NAMES
from bfgsupport import Board

from .player import Player

class FirstSeat():

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

    def __init__(self, player: Player):
        self.player = player

    # def first_seat_card(board: Board) -> Card:
    #     """Return the card if the first seat."""
    #     print('fs first_seat_card')
    #     player = Player(board)
    #     suit = _select_lead_suit(player)
    #     selected_card = _select_card_from_suit(player, suit)
    #     # print(player.seat, selected_card)
    #     return selected_card

    # def _select_lead_suit(player: Player) -> Suit:
    #     """Return the suit for the lead."""
    #     if player.is_defender:
    #         return _select_lead_suit_for_defender(player)
    #     else:
    #         return _select_lead_suit_for_declarer(player)

    # def _select_lead_suit_for_declarer(player: Player) -> Suit:
    #     """Return the trick lead suit for the declarer."""
    #     if player.board.contract.is_nt:
    #         return FirstSeatDeclarer().select_lead_suit_for_suit_contract(player)  # TODO needs changing
    #     else:
    #         return FirstSeatDeclarer().select_lead_suit_for_suit_contract(player)

    # def _select_lead_suit_for_defender(player: Player) -> Suit:
    #     """Return the trick lead suit for the defender."""
    #     if player.board.contract.is_nt:
    #         return FirstSeatDefender().select_lead_suit_for_suit_contract(player)
    #     else:
    #         return FirstSeatDefender().select_lead_suit_for_suit_contract(player)


    # TODO does all pf this only apply to defenders?
    def _select_card_from_suit(self, suit):
        """Return the card to lead from the given suit."""
        player = self.player
        if player.is_declarer or player.is_dummy:
            return self.select_lead_card(suit)
        else:
            cards = player.suit_cards[suit.name]

            # Top of touching honours
            for index, card in enumerate(cards[:-1]):
                if card.is_honour and card.value == cards[index+1].value + 1:
                    return card

            # Top of doubleton
            if len(cards) == 2:
                return cards[0]

            # Return bottom card
            return cards[-1]

    def _deprecate_suits(self) -> List[Tuple[str, int]]:
        """Assign score to suits based on void."""
        suit_scores = {suit_name: 0 for suit_name, suit in SUITS.items()}
        for suit in SUITS:
            if not self.player.suit_cards[suit]:
                suit_scores[suit] -= self.VOID_SCORE
        return [(suit_name, score) for suit_name, score in suit_scores.items()]

    def _partners_suit(self) -> List[Tuple[str, int]]:
        """Assign score to suits based on it being suit partner led."""
        suit_scores = {suit_name: 0 for suit_name, suit in SUITS.items()}
        partners_suit = self._get_partners_suit()
        if partners_suit and not partners_suit == self.player.trump_suit:
            suit_scores[partners_suit.name] += self.PARTNERS_SUIT_SCORE
        return [(suit_name, score) for suit_name, score in suit_scores.items()]

    def _tenace_check(self) -> List[Tuple[str, int]]:
        """Assign score to suits based on tenaces in dummy."""
        suit_scores = {suit_name: 0 for suit_name, suit in SUITS.items()}
        dummy_tenaces = FirstSeat._identify_tenace(self)
        for suit in dummy_tenaces:
            if self.player.dummy_on_left:
                # Lead through tenaces
                suit_scores[suit] += self.TENACE_SCORE
            elif self.player.dummy_on_right:
                # Lead to tenaces
                suit_scores[suit] -= self.TENACE_SCORE
        return [(suit_name, score) for suit_name, score in suit_scores.items()]

    def _lead_through_strength(self) -> List[Tuple[str, int]]:
        """Assign score to suits where you lead through or to strength."""
        suit_scores = {suit_name: 0 for suit_name, suit in SUITS.items()}
        player = self.player
        if player.dummy_on_left:
            for suit, points in player.dummy_suit_strength.items():
                if points >= 5:
                    suit_scores[suit] += self.STRENGTH_SCORE
        elif player.dummy_on_right:
            for suit, points in player.dummy_suit_strength.items():
                if not player.trump_suit:
                    if points <= 2:
                        suit_scores[suit] += self.STRENGTH_SCORE
                else:
                    if suit != player.trump_suit.name:
                        if points <= 2:
                            suit_scores[suit] += self.STRENGTH_SCORE
        return [(suit_name, score) for suit_name, score in suit_scores.items()]

    def _frozen_suits(self) -> List[Tuple[str, int]]:
        """Assign score to suits based on frozen suits."""
        suit_scores = {suit_name: 0 for suit_name, suit in SUITS.items()}
        frozen_suits = []
        for suit, cards in self.player.dummys_suit_cards.items():
            dummy_honours = 0
            hand_honours = 0
            for card in cards:
                if card.is_honour:
                    dummy_honours += 1
            if dummy_honours == 1:
                suit_cards = self.player.suit_cards[suit]
                for card in suit_cards:
                    if card.is_honour:
                        hand_honours += 1
            if dummy_honours ==1 and hand_honours == 1:
                frozen_suits.append(suit)
        for suit in frozen_suits:
            suit_scores[suit] -= self.FROZEN_SUIT_SCORE
        return [(suit_name, score) for suit_name, score in suit_scores.items()]

    def _long_suits(self) -> List[Tuple[str, int]]:
        """Assign score to suits based on length (long)."""
        suit_scores = {suit_name: 0 for suit_name, suit in SUITS.items()}
        for suit in SUITS:
            number_cards = len(self.player.suit_cards[suit]) - 4
            if number_cards > 0:
                suit_scores[suit] = number_cards * self.LENGTH_SCORE
        return [(suit_name, score) for suit_name, score in suit_scores.items()]

    def _short_suits(self) -> List[Tuple[str, int]]:
        """Assign score to suits based on length (short)."""
        suit_scores = {suit_name: 0 for suit_name, suit in SUITS.items()}
        if len(self.player.trump_cards) > 0:
            for suit in SUITS:
                number_cards = len(self.player.suit_cards[suit])
                if 0 < number_cards < 3:
                    suit_scores[suit] = (2 - number_cards) * self.LENGTH_SCORE
        return [(suit_name, score) for suit_name, score in suit_scores.items()]

    def _ruff_and_discard(self) -> List[Tuple[str, int]]:
        """Assign score to suits based on potential for ruff and discard."""
        suit_scores = {suit_name: 0 for suit_name, suit in SUITS.items()}
        if len(self.player.dummys_suit_cards[self.player.trump_suit.name]) > 0:
            for suit in SUITS:
                if len(self.player.dummys_suit_cards[suit]) == 0:
                    suit_scores[suit] -= self.RUFF_AND_DISCARD_SCORE
        return [(suit_name, score) for suit_name, score in suit_scores.items()]

    def _get_partners_suit(self) -> Union[Suit, None]:
        """Return partner's suit if this is 3rd hand on first lead."""
        trick_one = self.player.board.tricks[0]
        if trick_one.leader == self.player.partner_seat:
            opening_lead = trick_one.cards[0]
            if opening_lead.suit != self.player.trump_suit:
                if opening_lead.value < 7 and self.player.suit_cards[opening_lead.suit]:
                    return opening_lead.suit
        return None

    def _identify_tenace(self) -> List[Suit]:
        """Return a list of suits with a tenace in dummy."""
        suits = []
        player = self.player
        for suit, tenace in player.dummy_suit_tenaces.items():
            if player.suit_cards[suit]:
                if tenace and (player.trump_suit and not suit == player.trump_suit.name):
                    tenace_index = CARD_NAMES.index(tenace.name)
                    next_card_name = CARD_NAMES[tenace_index+1]
                    if Card(next_card_name) not in player.cards:
                        suits.append(suit)
        return suits

    def _best_suit(self, score_reasons: Dict[str, int]) -> Suit:
        """Return the best suit based on score."""
        suit_scores = {suit_name: 0 for suit_name, suit in SUITS.items()}
        player = self.player
        for reason, suits in score_reasons.items():
            # print(colored(f'1st seat {reason[:8]:<8} {suits}', 'green'))
            for suit in suits:
                suit_scores[suit[0]] += suit[1]
        # print(colored(f'{player.seat=}{suit_scores=}', 'red'))

        max_score = 0
        for suit, score in suit_scores.items():
            if score > max_score:
                max_score = score
        candidate_suits = []
        for suit, score in suit_scores.items():
            if score == max_score:
                candidate_suits.append(suit)
        if not candidate_suits:
            return self._select_best_suit(player)
        return Suit(random.choice(candidate_suits))

    def _select_best_suit(self, player: Player) -> Suit:
        """Select suit for signal."""
        # TODO handle no points and equal suits
        cards = player.cards
        suit_points = player.get_suit_strength(cards)
        max_points = 0
        best_suit = None
        for suit in SUITS:
            hcp = suit_points[suit]
            if hcp > max_points:
                max_points = hcp
                best_suit = suit
        if not best_suit:
            return player.longest_suit
        return Suit(best_suit)
