"""Second seat card play."""

import logging
log = logging.getLogger(__name__)

from typing import List, Union, Tuple

from bridgeobjects import SUITS, Card, Denomination, Suit
from bfgsupport import Board, Trick

from .player import Player


class SecondSeat():
    def __init__(self, player: Player):
        self.player = player

    def _select_card_if_void(self, player: Player) -> Card:
        """Return card if cannot follow suit."""
        # Trump if appropriate
        if player.trump_suit:
            pass


        # Signal suit preference."""
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
