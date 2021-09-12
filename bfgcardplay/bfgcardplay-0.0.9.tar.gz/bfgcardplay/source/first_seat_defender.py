""" First seat card play for defender."""

import logging
log = logging.getLogger(__name__)

from typing import List, Dict, Union
import random

from bridgeobjects import SUITS, Card, Suit, SEATS, CARD_NAMES
from bfgsupport import Board
from .player import Player
# from .common import FirstSeat
from .first_seat import FirstSeat

class FirstSeatDefender(FirstSeat):
    def __init__(self, player: Player):
        super().__init__(player)

    def selected_card(self) -> Card:
        """Return the card if the third seat."""
        player = self.player
        if player.board.contract.is_nt:
            suit = self._select_suit_for_suit_contract()  # TODO sort out
        else:
            suit = self._select_suit_for_suit_contract()
        card = self._select_card_from_suit(suit)
        return card

    def _select_suit_for_suit_contract(self) -> Suit:
        """Return the trick lead suit for the defending a suit contract."""
        score_reasons = {}

        # Deprecate voids
        score_reasons['void'] = self._deprecate_suits()

        # Return partner's suit
        score_reasons['partner'] = self._partners_suit()

        # Lead through tenaces not to tenaces
        score_reasons['tenaces'] = self._tenace_check()

        # Lead through or to strength
        score_reasons['weakness'] = self._lead_through_strength()

        # Avoid frozen suits
        score_reasons['frozen'] = self._frozen_suits()

        # Long suits
        score_reasons['long'] = self._long_suits()

        # Short suits
        score_reasons['short'] = self._short_suits()

        # Ruff and discard
        if self.player.trump_suit:
            score_reasons['ruff'] = self._ruff_and_discard()

        # Select best suit
        best_suit = self._best_suit(score_reasons)
        return best_suit