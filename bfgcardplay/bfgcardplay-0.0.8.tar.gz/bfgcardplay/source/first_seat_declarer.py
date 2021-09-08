""" First seat card play for declarer."""

import logging
log = logging.getLogger(__name__)

from typing import List, Dict, Union, Tuple
import random

from bridgeobjects import SUITS, Card, Suit, SEATS, CARD_NAMES
from bfgsupport import Board
from .cardplayer import Player
from .common import FirstSeat, DRAW_TRUMPS_SCORE, LENGTH_SCORE, FROZEN_SUIT_SCORE

ALL_WINNERS = 5

class FirstSeatDeclarer(FirstSeat):
    def __init__(self):
        super().__init__()
        self.declarer_cards = []
        self.declarer_suit_cards = {}

    def select_lead_suit_for_suit_contract(self, player: Player) -> Suit:
        """Return the trick lead suit for the declarer in  a suit contract."""
        self.declarer_cards = player.board.hands[player.declarer].unplayed_cards
        self.declarer_suit_cards = player.get_cards_by_suit(self.declarer_cards)

        score_reasons = {}

        # Draw trumps
        if player.trump_suit:
            score_reasons['trumps'] = self._draw_trumps(player)

        # Deprecate voids
        score_reasons['void'] = FirstSeat._deprecate_suits(player)

        # All cards are winners
        score_reasons['all_winners'] = self._all_winners_score(player)

        # Avoid frozen suits
        score_reasons['frozen'] = self._frozen_suits(player)

        # Long suits
        score_reasons['long'] = self._long_suits(player)

        # Short suits
        score_reasons['short'] = FirstSeat._short_suits(player)

        # Select best suit
        best_suit = FirstSeat._best_suit(player, score_reasons)
        # for reason, suits in score_reasons.items():
        #     print(f'1st seat {player.seat=} {reason[:8]:<8}', suits)
        # print(f'{player.seat=}, {best_suit=}')
        return best_suit

    def select_lead_card(self, player: Player, suit: Suit) -> Card:
        """Return the selected lead card for declarer."""
        if not player.opponents_trumps:
            if self._all_winners(player, suit):
                (long_hand, short_hand) = player.get_long_hand(player.declarers_hand,
                                                                player.dummys_hand, suit)
                long_cards = long_hand[suit.name]
                short_cards = short_hand[suit.name]
                print(f'{long_cards=}')
                print(f'{short_cards=}')
                if short_cards:
                    if short_cards[-1].value < long_cards[0].value:
                        if short_cards == player.suit_cards[suit.name]:
                            # player has the short hand
                            return short_cards[0]
                        else:
                            # player has the long hand
                            return long_cards[-1]


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

    @staticmethod
    def _draw_trumps(player: Player) -> List[Tuple[str, int]]:
        """Assign score to trump suit."""
        suit_scores = {suit_name: 0 for suit_name, suit in SUITS.items()}
        trump_suit = player.trump_suit

        # Is drawing trumps in strategy?
        if not FirstSeatDeclarer._can_draw_trumps(player):
            suit_scores[trump_suit.name] -= DRAW_TRUMPS_SCORE
        else:
            # are there trumps oustanding?
            (declarers_trumps, defenders_trumps) = player.total_unplayed_cards_by_suit(trump_suit)

            # Is defender's last trump > declarers?
            best_trump = 0
            for card in  declarers_trumps:
                if card.value > best_trump:
                    best_trump = card.value
            leave_trumps = len(defenders_trumps) == 1 and defenders_trumps[0].value > best_trump

            if defenders_trumps and not leave_trumps:
                suit_scores[trump_suit.name] += DRAW_TRUMPS_SCORE
            else:
                suit_scores[trump_suit.name] -= DRAW_TRUMPS_SCORE
        return [(suit_name, score) for suit_name, score in suit_scores.items()]

    @staticmethod
    def _can_draw_trumps(player: Player) -> bool:
        """Return True if declarer should draw trumps."""
        declarers_trumps = player.unplayed_cards_by_suit(player.trump_suit, player.declarer)
        dummys_trumps = player.unplayed_cards_by_suit(player.trump_suit, player.dummy)
        declarer_longer_trumps = len(declarers_trumps) > len(dummys_trumps)
        if declarer_longer_trumps:
            short_hand = player.board.hands[player.dummy]
        else:
            short_hand = player.board.hands[player.declarer]
        if short_hand.shape[3] <= 2:
            # Are there sufficient rumps in short hand?
            opponents_trumps = player.opponents_cards[player.trump_suit.name]
            if len(short_hand.cards_by_suit[player.trump_suit.name]) > len(opponents_trumps):
                return True
            # can declarer produce a void in time?
            suit = short_hand.shortest_suit
            # if declarer_longer_trumps:
            #     short_suit_cards = player.unplayed_cards_by_suit(suit, player.dummy)
            # else:
            #     short_suit_cards = player.unplayed_cards_by_suit(suit, player.declarer)

            declarers_cards = player.unplayed_cards_by_suit(suit, player.declarer)
            dummys_cards = player.unplayed_cards_by_suit(suit, player.dummy)
            suit_cards = declarers_cards + dummys_cards
            if not(Card('A', suit.name) in suit_cards or Card('K', suit.name) in suit_cards):
                return False
        return True

    @staticmethod
    def _long_suits(player: Player) -> List[Tuple[str, int]]:
        """Assign score to suits based on length (long)."""
        suit_scores = {suit_name: 0 for suit_name, suit in SUITS.items()}
        for suit in SUITS:
            number_cards = len(player.suit_cards[suit]) - 4
            if number_cards > 0:
                suit_scores[suit] = number_cards * LENGTH_SCORE
        return [(suit_name, score) for suit_name, score in suit_scores.items()]

    def _frozen_suits(self, player: Player) -> List[Tuple[str, int]]:
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
                suit_cards = self.declarer_suit_cards[suit]
                for card in suit_cards:
                    if card.is_honour:
                        hand_honours += 1
            if dummy_honours ==1 and hand_honours == 1:
                frozen_suits.append(suit)
        for suit in frozen_suits:
            suit_scores[suit] -= FROZEN_SUIT_SCORE
        return [(suit_name, score) for suit_name, score in suit_scores.items()]

    def _all_winners_score(self, player: Player) -> List[Tuple[str, int]]:
        """Assign score to a suit if all the cards are winners."""
        suit_scores = {suit_name: 0 for suit_name, suit in SUITS.items()}
        our_cards = player.our_cards
        opponents_cards = player.opponents_cards
        for suit in SUITS:
            if our_cards[suit] and not opponents_cards[suit]:
                suit_scores[suit] = ALL_WINNERS
            elif our_cards[suit] and opponents_cards[suit]:
                if our_cards[suit][-1].value > opponents_cards[suit][0].value:
                    suit_scores[suit] = ALL_WINNERS
                else:
                    pass
        return [(suit_name, score) for suit_name, score in suit_scores.items()]

    def _all_winners(self, player: Player, suit: Suit) -> bool:
        """Return True if all the cards in the suit are winners."""
        our_cards = player.our_cards[suit.name]
        opponents_cards = player.opponents_cards[suit.name]
        if our_cards and not opponents_cards:
            return True
        elif our_cards and opponents_cards:
            if our_cards[-1].value > opponents_cards[0].value:
                return True
            else:
                if our_cards[0].value > opponents_cards[0].value:
                    sequence = [our_cards[0]]
                    for index, card in enumerate(our_cards[:-1]):
                        if card.value == our_cards[index+1].value + 1:
                            sequence.append(our_cards[index+1])
                    if len(sequence) > len(opponents_cards):
                        return True
        return False