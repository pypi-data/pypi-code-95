""" First seat card play for defender."""

import logging
log = logging.getLogger(__name__)

from typing import List, Dict, Union
import random

from bridgeobjects import SUITS, Card, Suit, SEATS, CARD_NAMES
from bfgsupport import Board
from .cardplayer import Player
from .common import FirstSeat

class FirstSeatDefender(FirstSeat):
    def __init__(self):
        pass

    @staticmethod
    def select_lead_suit_for_suit_contract(player: Player) -> Suit:
        """Return the trick lead suit for the defending a suit contract."""
        score_reasons = {}

        # Deprecate voids
        score_reasons['void'] = FirstSeat._deprecate_suits(player)

        # Return partner's suit
        score_reasons['partner'] = FirstSeat._partners_suit(player)

        # Lead through tenaces not to tenaces
        score_reasons['tenaces'] = FirstSeat._tenace_check(player)

        # Lead through or to strength
        score_reasons['weakness'] = FirstSeat._lead_through_strength(player)

        # Avoid frozen suits
        score_reasons['frozen'] = FirstSeat._frozen_suits(player)

        # Long suits
        score_reasons['long'] = FirstSeat._long_suits(player)

        # Short suits
        score_reasons['short'] = FirstSeat._short_suits(player)

        # Ruff and discard
        if player.trump_suit:
            score_reasons['ruff'] = FirstSeat._ruff_and_discard(player)

        # Select best suit
        best_suit = FirstSeat._best_suit(player, score_reasons)
        return best_suit