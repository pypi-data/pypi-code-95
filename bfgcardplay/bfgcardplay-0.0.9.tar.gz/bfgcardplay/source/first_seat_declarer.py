# first_seat_declarer.py

""" First seat card play for declarer."""

import logging
log = logging.getLogger(__name__)

from typing import List, Dict, Union, Tuple
from termcolor import colored
import random

from bridgeobjects import SUITS, Card, Suit, SEATS, CARD_NAMES

import bfgcardplay.source.global_variables as global_vars
from .player import Player
from .first_seat import FirstSeat

ALL_WINNERS = 5

class FirstSeatDeclarer(FirstSeat):
    def __init__(self, player: Player):
        super().__init__(player)
        self.declarer_suit_cards = {}
        self.manager = None

    def selected_card(self) -> Card:
        """Return the card for the first seat."""
        player = self.player
        if player.board.contract.is_nt:
            suit = self._select_suit_for_suit_contract()  # TODO NT needed
        else:
            suit = self._select_suit_for_suit_contract()
        if not player.suit_cards[suit.name]:
            raise ValueError(f'No cards for {suit}')
        card = self.select_lead_card(suit)
        return card

    def _select_suit_for_suit_contract(self) -> Suit:
        """Return the trick lead suit for the declarer in  a suit contract."""
        player = self.player
        self.manager = global_vars.manager
        declarer_cards = player.board.hands[player.declarer].unplayed_cards
        self.declarer_suit_cards = player.get_cards_by_suit(declarer_cards)

        score_reasons = {}

        # Draw trumps?
        if player.opponents_trumps:
            if self._can_draw_trumps():
                return player.trump_suit
        else:
            score_reasons['trumps'] = self._deprecate_trumps()


        # Reset Manager winning suit when no cards left
        manager = self.manager
        if manager.winning_suit:
            if player.suit_cards[manager.winning_suit.name]:
                return manager.winning_suit
            else:
                manager.winning_suit = None

        winning_suit = self._get_winning_suit(player)
        if winning_suit:
            manager.winning_suit = winning_suit
            return winning_suit

        if player.trump_suit and not player.opponents_trumps:
            long_suits = player.partnership_long_suits()
            for suit in long_suits:
                if player.can_lead_toward_tenace(suit):
                    return Suit(suit)

        # Deprecate voids
        score_reasons['void'] = self._deprecate_suits()

        # All cards are winners
        score_reasons['all_winners'] = self._all_winners_score()

        # Avoid frozen suits
        score_reasons['frozen'] = self._frozen_suits()

        # Long suits
        score_reasons['long'] = self._long_suits()

        # # Short suits
        # score_reasons['short'] = self._short_suits()

        # Select best suit
        best_suit = self._best_suit(score_reasons)
        # print(colored(f'{best_suit=} {score_reasons=}', 'red'))
        return best_suit

    def select_lead_card(self, suit: Suit) -> Card:
        """Return the selected lead card for declarer."""
        player = self.player
        manager = self.manager
        if manager.winning_suit:
            suit = manager.winning_suit
            long_player = player.get_long_hand_seat(player.declarer, player.dummy, suit)
            manager.long_player = long_player
            cards = player.suit_cards[suit.name]
            if long_player != player.seat:
                # Short hand leads top card
                return cards[0]
            else:
                # Long hand leads bottom card if short hand has cards
                if player.partners_suit_cards[suit.name]:
                    return cards[-1]
                else:
                    return cards[0]
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

    def _get_winning_suit(self, player: Player) -> Suit:
        """Return the selected winning suit."""
        winning_suits = self._get_winning_suits(player)
        max_length = 0
        long_suit = None
        for suit in winning_suits:
            suit_length = len(player.suit_cards[suit.name])
            if suit_length > max_length:
                max_length = suit_length
                long_suit = suit
        return long_suit

    def _get_winning_suits(self, player: Player) -> List[Suit]:
        """Return a list of winning suits."""
        winning_suits = []
        for suit_name, suit in SUITS.items():
            if suit != player.trump_suit:
                if player.holds_all_winners_in_suit(suit):
                    winning_suits.append(suit)
        return winning_suits


    # def _draw_trumps(self) -> List[Tuple[str, int]]:
    #     """Assign score to trump suit."""
    #     player = self.player
    #     suit_scores = {suit_name: 0 for suit_name, suit in SUITS.items()}
    #     trump_suit = player.trump_suit

    #     # Is drawing trumps in strategy?
    #     if not self._can_draw_trumps():
    #         suit_scores[trump_suit.name] -= self.DRAW_TRUMPS_SCORE
    #     else:
    #         # are there trumps oustanding?
    #         (declarers_trumps, defenders_trumps) = player.total_unplayed_cards_by_suit(trump_suit)

    #         # Is defender's last trump > declarers?
    #         best_trump = 0
    #         for card in  declarers_trumps:
    #             if card.value > best_trump:
    #                 best_trump = card.value
    #         leave_trumps = len(defenders_trumps) == 1 and defenders_trumps[0].value > best_trump

    #         if defenders_trumps and not leave_trumps:
    #             suit_scores[trump_suit.name] += self.DRAW_TRUMPS_SCORE
    #         else:
    #             suit_scores[trump_suit.name] -= self.DRAW_TRUMPS_SCORE
    #     return [(suit_name, score) for suit_name, score in suit_scores.items()]

    def _can_draw_trumps(self) -> bool:
        """Return True if declarer should draw trumps."""
        player = self.player
        if not player.trump_cards:
            return False

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

    def _long_suits(self) -> List[Tuple[str, int]]:
        """Assign score to suits based on length (long)."""
        player = self.player
        suit_scores = {suit_name: 0 for suit_name, suit in SUITS.items()}
        for suit in SUITS:
            number_cards = len(player.suit_cards[suit]) - 4
            if number_cards > 0:
                suit_scores[suit] = number_cards * self.LENGTH_SCORE
        return [(suit_name, score) for suit_name, score in suit_scores.items()]

    def _frozen_suits(self) -> List[Tuple[str, int]]:
        """Assign score to suits based on frozen suits."""
        player = self.player
        suit_scores = {suit_name: 0 for suit_name, suit in SUITS.items()}
        frozen_suits = []
        for suit, cards in player.dummys_suit_cards.items():
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
            suit_scores[suit] -= self.FROZEN_SUIT_SCORE
        return [(suit_name, score) for suit_name, score in suit_scores.items()]

    def _all_winners_score(self) -> List[Tuple[str, int]]:
        """Assign score to a suit if all the cards are winners."""
        player = self.player
        suit_scores = {suit_name: 0 for suit_name, suit in SUITS.items()}
        for suit_name, suit in SUITS.items():
            if suit != player.trump_suit:
                if player.holds_all_winners_in_suit(suit):
                    suit_scores[suit_name] = ALL_WINNERS
        return [(suit_name, score) for suit_name, score in suit_scores.items()]

    def _deprecate_trumps(self) -> List[Tuple[str, int]]:
        """Assign score to a suit if opponents have no trumps."""
        suit_scores = {suit_name: 0 for suit_name, suit in SUITS.items()}
        suit_scores[self.player.trump_suit.name] = -1 * self.TRUMP_SCORE
        return [(suit_name, score) for suit_name, score in suit_scores.items()]


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