"""Fourth seat card play."""


import logging
log = logging.getLogger(__name__)

from typing import List, Union, Tuple

from bridgeobjects import SUITS, Card, Denomination, Suit
from bfgsupport import Board, Trick
from .player import Player

class FourthSeat():
    def __init__(self, player: Player):
        self.player = player

    def _winning_card(self, trick: Trick) -> Union[Card, None]:
        """Return the card if can win trick."""
        player = self.player
        cards = self.player.cards_for_trick_suit(trick)

        (value_0, value_1, value_2) = self._trick_card_values(trick, player.trump_suit)
        if cards:
            for card in cards[::-1]:
                card_value = card.value
                if card.suit == player.trump_suit:
                    card_value += 13
                if card_value > value_0 and card_value > value_2:
                    return card

        # No cards in trick suit, look for trump winner
        elif player.trump_cards:
            for card in player.trump_cards[::-1]:
                if card.value + 13 > value_2:
                    return card
        return None

    def _second_player_winning_trick(self, cards: List[Card], trick: Trick, trumps: Denomination) -> bool:
        """Return True if the second player is winning the trick."""
        (value_0, value_1, value_2) = self._trick_card_values(trick, trumps)
        if value_1 > value_0 and value_1 > value_2:
            return True
        return False

    @staticmethod
    def _trick_card_values(trick: Trick, trumps: Denomination) -> Tuple[int, int, int]:
        """Return a tuple of card values."""
        value_0 = trick.cards[0].value
        value_1 = trick.cards[1].value
        value_2 = trick.cards[2].value
        if trumps:
            if trick.cards[0].suit == trumps:
                value_0 += 13
            if trick.cards[1].suit == trumps:
                value_1 += 13
            if trick.cards[2].suit == trumps:
                value_2 += 13
        return (value_0, value_1, value_2)

    def _select_card_if_void(self) -> Card:
        """Return card if cannot follow suit."""
        # Trump if appropriate
        player = self.player
        if player.trump_suit:
            pass

        suit = self._best_suit(player)
        suit_cards = player.suit_cards[suit.name]
        for card in suit_cards:
            if not card.is_honour:
                return card

        other_suit = player.other_suit_for_signals(suit)
        other_suit_cards = player.suit_cards[other_suit]
        if other_suit_cards:
            return other_suit_cards[-1]

        for suit_name in SUITS:
            if suit_name != suit.name and suit_name != other_suit:
                final_suit_cards = player.suit_cards[suit_name]
                if final_suit_cards:
                    return final_suit_cards[-1]

        return player.suit_cards[suit.name][0]

    def _best_suit(self, player: Player) -> Suit:
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
